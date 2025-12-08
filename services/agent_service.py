import google.generativeai as genai
import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from database.models import Conversation, Message, ToolCall, AgentMemory
from sqlalchemy.orm import Session
from prompts import SYSTEM_PROMPT, TOOL_DESCRIPTIONS, get_current_date_context
from services.tool_service import ToolService
from utils.helpers import proto_to_dict, safe_json_serialize

logger = logging.getLogger(__name__)

class AgentService:
    def __init__(self, db: Session):
        self.db = db
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.tool_service = ToolService()
        self.model_name = "gemini-2.5-flash"
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=SYSTEM_PROMPT
        )
    
    async def get_or_create_conversation(self, phone_number: str) -> Conversation:
        """Get existing conversation or create new one"""
        conv = self.db.query(Conversation).filter(
            Conversation.phone_number == phone_number,
            Conversation.status == "active"
        ).first()
        
        if not conv:
            conv = Conversation(phone_number=phone_number)
            self.db.add(conv)
            self.db.commit()
            self.db.refresh(conv)
        
        return conv
    
    def get_conversation_history(self, conversation_id: int, limit: int = 10) -> List[Dict]:
        """Get recent conversation history"""
        messages = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.timestamp.desc()).limit(limit).all()
        
        history = []
        for msg in reversed(messages):
            history.append({
                "role": "user" if msg.direction == "inbound" else "model",
                "parts": [msg.content]
            })
        
        return history
    
    def get_user_memory(self, phone_number: str) -> Dict[str, str]:
        """Get stored user information"""
        memories = self.db.query(AgentMemory).filter(
            AgentMemory.phone_number == phone_number
        ).all()
        
        return {mem.key: mem.value for mem in memories}
    
    def save_user_memory(self, phone_number: str, key: str, value: str):
        """Save user information with error handling"""
        try:
            memory = self.db.query(AgentMemory).filter(
                AgentMemory.phone_number == phone_number,
                AgentMemory.key == key
            ).first()
            
            if memory:
                memory.value = value
                memory.updated_at = datetime.utcnow()
            else:
                memory = AgentMemory(
                    phone_number=phone_number,
                    key=key,
                    value=value
                )
                self.db.add(memory)
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error saving user memory: {str(e)}")
            self.db.rollback()
            raise
    
    def save_message(self, conversation_id: int, phone_number: str, 
                    message_sid: str, direction: str, content: str):
        """Save message to database with error handling"""
        try:
            # Generate unique message_sid for outbound messages if empty
            if not message_sid:
                import uuid
                message_sid = f"OUT_{uuid.uuid4().hex[:24]}"
            
            msg = Message(
                conversation_id=conversation_id,
                phone_number=phone_number,
                message_sid=message_sid,
                direction=direction,
                content=content
            )
            self.db.add(msg)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error saving message: {str(e)}")
            self.db.rollback()
            raise
    
    def save_tool_call(self, conversation_id: int, tool_name: str, 
                      input_data: Dict, output_data: Dict):
        """Save tool call to database with bulletproof serialization"""
        try:
            # Safely serialize input and output data to prevent ANY serialization errors
            safe_input = safe_json_serialize(input_data)
            safe_output = safe_json_serialize(output_data)
            
            tool_call = ToolCall(
                conversation_id=conversation_id,
                tool_name=tool_name,
                input_data=safe_input,
                output_data=safe_output,
                success=str(output_data.get("success", False)),
                error_message=output_data.get("error")
            )
            self.db.add(tool_call)
            self.db.commit()
            
        except Exception as e:
            # If serialization still fails, rollback and save minimal version
            logger.error(f"Error saving tool call for {tool_name}: {str(e)}")
            self.db.rollback()
            
            try:
                # Fallback: Save minimal information
                tool_call = ToolCall(
                    conversation_id=conversation_id,
                    tool_name=tool_name,
                    input_data={"error": "serialization_failed"},
                    output_data={"error": "serialization_failed", "success": False},
                    success="False",
                    error_message=f"Serialization error: {str(e)}"
                )
                self.db.add(tool_call)
                self.db.commit()
                logger.info(f"Saved minimal tool call record for {tool_name}")
            except Exception as fallback_error:
                # If even the fallback fails, just log and continue
                logger.error(f"Could not save tool call at all: {fallback_error}")
                self.db.rollback()
    
    async def process_message(self, phone_number: str, user_message: str, 
                             message_sid: str, user_name: Optional[str] = None) -> str:
        """Process incoming message and generate response"""
        
        # Get or create conversation
        conversation = await self.get_or_create_conversation(phone_number)
        
        # Update user name if provided
        if user_name and not conversation.user_name:
            conversation.user_name = user_name
            self.db.commit()
        
        # Save incoming message
        self.save_message(conversation.id, phone_number, message_sid, "inbound", user_message)
        
        # Get conversation history
        history = self.get_conversation_history(conversation.id, limit=10)
        
        # Get user memory
        memory = self.get_user_memory(phone_number)
        
        # Build context with phone number and name from WhatsApp
        # Format phone number for display (e.g., +919773645411)
        formatted_phone = phone_number if phone_number.startswith('+') else f"+{phone_number}"
        
        context_info = f"\n\n**CURRENT USER CONTEXT:**"
        context_info += f"\n- WhatsApp Number: {formatted_phone}"
        
        # Include WhatsApp profile name if available
        if user_name:
            context_info += f"\n- WhatsApp Profile Name: {user_name}"
        
        # Include saved memory
        if memory:
            if memory.get("name"):
                context_info += f"\n- Confirmed Name: {memory.get('name')}"
            if memory.get("phone_number"):
                context_info += f"\n- Confirmed Phone: {memory.get('phone_number')}"
            if memory.get("preferences"):
                context_info += f"\n- Preferences: {memory.get('preferences')}"
        
        context_info += f"\n\n**INSTRUCTIONS:**"
        context_info += f"\n- If you need phone number and user hasn't confirmed yet, ask: 'Should I use your WhatsApp number ({formatted_phone}) for the booking?'"
        if user_name:
            context_info += f"\n- If you need name and user hasn't confirmed yet, ask: 'Can I use \"{user_name}\" for the booking, or would you prefer a different name?'"
        context_info += f"\n- Once confirmed, save to memory and never ask again"
        context_info += f"\n- Be natural and conversational, never mention 'tools' or 'functions'"
        
        # Prepare tools for Gemini function calling
        tools = self._convert_tools_to_gemini_format()
        
        # Call Gemini API with function calling
        response_text = await self._call_gemini_with_tools(
            history=history,
            user_message=user_message,
            tools=tools,
            conversation_id=conversation.id,
            phone_number=phone_number,
            context_info=context_info
        )
        
        # Extract and save user information from responses
        lower_msg = user_message.lower()
        
        # Handle phone number confirmation
        if any(phrase in lower_msg for phrase in ["whatsapp is fine", "same number", "whatsapp number", "this number", "yes use whatsapp"]):
            if not memory.get("phone_number"):
                formatted_phone = phone_number if phone_number.startswith('+') else f"+{phone_number}"
                self.save_user_memory(phone_number, "phone_number", formatted_phone)
                logger.info(f"Saved WhatsApp number as confirmed phone: {formatted_phone}")
        
        # Handle explicit phone number provided
        import re
        phone_match = re.search(r'(\+?\d{10,13})', user_message)
        if phone_match and "whatsapp" not in lower_msg:
            extracted_phone = phone_match.group(1)
            if extracted_phone != phone_number:  # Different from WhatsApp number
                self.save_user_memory(phone_number, "phone_number", extracted_phone)
                logger.info(f"Saved different phone number: {extracted_phone}")
        
        # Handle name confirmation
        if user_name and any(phrase in lower_msg for phrase in ["yes", "correct", "that's right", "fine", "ok", "use that"]):
            if not memory.get("name") and len(user_message.split()) < 5:  # Short confirmation
                self.save_user_memory(phone_number, "name", user_name)
                logger.info(f"Saved WhatsApp profile name: {user_name}")
        
        # Extract name from "my name is X" or "I am X"
        if "my name is" in lower_msg or "i am" in lower_msg or "i'm" in lower_msg:
            words = user_message.split()
            for i, word in enumerate(words):
                if word.lower() in ["is", "am", "i'm"] and i + 1 < len(words):
                    potential_name = words[i + 1].strip(".,!?")
                    if potential_name and potential_name.lower() not in ["the", "a", "an", "from", "at"]:
                        self.save_user_memory(phone_number, "name", potential_name.title())
                        logger.info(f"Extracted and saved name: {potential_name.title()}")
                        break
        
        # Save outgoing message
        self.save_message(conversation.id, phone_number, "", "outbound", response_text)
        
        return response_text
    
    def _convert_json_schema_type_to_gemini(self, json_type: str) -> Any:
        """Convert JSON Schema type string to Gemini Type enum"""
        type_mapping = {
            "string": genai.protos.Type.STRING,
            "number": genai.protos.Type.NUMBER,
            "integer": genai.protos.Type.INTEGER,
            "boolean": genai.protos.Type.BOOLEAN,
            "array": genai.protos.Type.ARRAY,
            "object": genai.protos.Type.OBJECT
        }
        return type_mapping.get(json_type.lower(), genai.protos.Type.STRING)
    
    def _convert_property_to_gemini_schema(self, prop_schema: Dict) -> genai.protos.Schema:
        """Recursively convert a JSON Schema property to Gemini Schema"""
        prop_type = prop_schema.get("type", "string")
        gemini_type = self._convert_json_schema_type_to_gemini(prop_type)
        
        schema_kwargs = {
            "type": gemini_type,
        }
        
        # Add description if available
        if "description" in prop_schema:
            schema_kwargs["description"] = prop_schema["description"]
        
        # Handle enum - encode in description instead of schema
        if "enum" in prop_schema:
            enum_values = ", ".join(str(v) for v in prop_schema["enum"])
            if "description" in schema_kwargs:
                schema_kwargs["description"] += f" (allowed values: {enum_values})"
            else:
                schema_kwargs["description"] = f"Allowed values: {enum_values}"
            # Don't add enum to schema_kwargs - Gemini protobuf doesn't handle it well
        
        # Handle array items
        if prop_type == "array" and "items" in prop_schema:
            items_schema = self._convert_property_to_gemini_schema(prop_schema["items"])
            schema_kwargs["items"] = items_schema
        
        # Handle object properties
        if prop_type == "object" and "properties" in prop_schema:
            properties = {}
            for key, value in prop_schema["properties"].items():
                properties[key] = self._convert_property_to_gemini_schema(value)
            schema_kwargs["properties"] = properties
            
            # Add required fields for objects
            if "required" in prop_schema:
                schema_kwargs["required"] = prop_schema["required"]
        
        return genai.protos.Schema(**schema_kwargs)
    
    def _convert_tools_to_gemini_format(self) -> List:
        """Convert tool descriptions to Gemini function calling format"""
        function_declarations = []
        
        for tool_data in TOOL_DESCRIPTIONS.values():
            # Convert properties
            properties = {}
            for prop_name, prop_schema in tool_data["input_schema"].get("properties", {}).items():
                properties[prop_name] = self._convert_property_to_gemini_schema(prop_schema)
            
            # Build the parameters schema
            parameters_kwargs = {
                "type": genai.protos.Type.OBJECT,
                "properties": properties
            }
            
            # Add required fields if they exist
            if "required" in tool_data["input_schema"]:
                parameters_kwargs["required"] = tool_data["input_schema"]["required"]
            
            # Create function declaration
            function_declaration = genai.protos.FunctionDeclaration(
                name=tool_data["name"],
                description=tool_data["description"],
                parameters=genai.protos.Schema(**parameters_kwargs)
            )
            
            function_declarations.append(function_declaration)
        
        return [genai.protos.Tool(function_declarations=function_declarations)]
    
    async def _call_gemini_with_tools(self, history: List[Dict], user_message: str,
                                     tools: List, conversation_id: int, 
                                     phone_number: str, context_info: str = "") -> str:
        """Call Gemini API with function calling capability"""
        
        # Update system instruction with date context and user context
        date_context = get_current_date_context()
        system_instruction = SYSTEM_PROMPT + f"\n\n{date_context}"
        if context_info:
            system_instruction += f"\n\nCONTEXT:{context_info}"
        
        # Create model with updated system instruction and tools
        model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=system_instruction,
            tools=tools
        )
        
        try:
            # Start chat with history
            chat = model.start_chat(history=history)
            
            # Send message
            response = chat.send_message(user_message)
            
            # Handle function calls
            max_iterations = 5
            iteration = 0
            
            while iteration < max_iterations:
                # Check if response has the expected structure
                if not response or not response.candidates:
                    logger.warning("Response has no candidates")
                    break
                
                candidate = response.candidates[0]
                if not candidate.content or not candidate.content.parts:
                    logger.warning("Candidate has no content or parts")
                    break
                
                # Check for function calls
                function_calls = [
                    part for part in candidate.content.parts 
                    if hasattr(part, 'function_call') and part.function_call
                ]
                
                if not function_calls:
                    # No more function calls, we're done
                    break
                
                # Process each function call
                function_responses = []
                
                for function_call_part in function_calls:
                    function_call = function_call_part.function_call
                    tool_name = function_call.name
                    
                    # Convert protobuf args to native Python types (CRITICAL FIX)
                    raw_args = dict(function_call.args) if function_call.args else {}
                    tool_input = proto_to_dict(raw_args)
                    
                    logger.info(f"Calling tool: {tool_name} with input: {tool_input}")
                    
                    try:
                        # Call the tool
                        if tool_name == "request_update_or_cancel":
                            tool_result = await self.tool_service.request_update_or_cancel(tool_input)
                        else:
                            tool_result = await self.tool_service.call_tool(tool_name, tool_input)
                        
                        # Save tool call
                        self.save_tool_call(conversation_id, tool_name, tool_input, tool_result)
                        
                        # Add function response
                        function_responses.append(
                            genai.protos.Part(
                                function_response=genai.protos.FunctionResponse(
                                    name=tool_name,
                                    response={"result": json.dumps(tool_result) if isinstance(tool_result, dict) else str(tool_result)}
                                )
                            )
                        )
                    except Exception as tool_error:
                        logger.error(f"Error calling tool {tool_name}: {str(tool_error)}")
                        # Add error response
                        function_responses.append(
                            genai.protos.Part(
                                function_response=genai.protos.FunctionResponse(
                                    name=tool_name,
                                    response={"error": str(tool_error)}
                                )
                            )
                        )
                
                # Send function responses back to model
                try:
                    response = chat.send_message(function_responses)
                except Exception as send_error:
                    logger.error(f"Error sending function responses: {str(send_error)}")
                    break
                
                iteration += 1
            
            # Extract final text response
            assistant_message = ""
            if response and response.candidates:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    text_parts = [
                        part.text for part in candidate.content.parts 
                        if hasattr(part, 'text') and part.text
                    ]
                    assistant_message = "".join(text_parts).strip()
            
            if not assistant_message:
                logger.warning("No text content in final response")
                return "I apologize, but I'm having trouble processing your request. Could you please rephrase?"
            
            return assistant_message
            
        except Exception as e:
            logger.error(f"Error calling Gemini API: {str(e)}", exc_info=True)
            return "I'm sorry, I'm experiencing technical difficulties. Please try again in a moment."
    
    async def close(self):
        """Cleanup resources"""
        await self.tool_service.close()