# How to Test Travel Studio API Endpoints

## 🎯 Quick Answer

Run this command:
```bash
python test_travel_api.py
```

That's it! The script will test common endpoint patterns and show you the results.

---

## 📝 What You'll See

Currently, all endpoints return:
```json
{"success":false,"message":"Route not found"}
```

This means the endpoints we're testing don't exist on the server.

---

## ✅ What's Working

- ✅ Your bearer token is valid (no 401 errors)
- ✅ The server is responding (no timeouts)
- ✅ Authentication is configured correctly

## ❌ What's Missing

- ❌ The correct API endpoint paths
- ❌ API documentation

---

## 🔑 Your Credentials

**API URL**: `https://travel-studio-backend-e2bkc2e0a8e4e3hy.centralindia-01.azurewebsites.net`

**Token** (in `.env`): Already configured ✅

**Hotel ID**: `aec93eab-a17b-4bec-b44a-08030dead54f`

**Token Expires**: February 8, 2025

---

## 🚀 Next Steps

1. **Contact Travel Studio Team** and ask for:
   - API documentation URL
   - List of available endpoints
   - Example API requests/responses

2. **Once you have the correct endpoints**, update `services/travel_studio_service.py`

3. **Test again**: `python test_travel_api.py`

4. **Start using it** in your WhatsApp agent!

---

## 📚 More Information

- **Quick Start**: `QUICK_START.md`
- **Full Testing Guide**: `TESTING_GUIDE.md`
- **Step-by-Step**: `TESTING_STEPS.md`
- **Integration Details**: `INTEGRATION_SUMMARY.md`

---

## 💡 Test Other Endpoints

You can manually test any endpoint with curl:

```bash
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJob3RlbElkIjoiYWVjOTNlYWItYTE3Yi00YmVjLWI0NGEtMDgwMzBkZWFkNTRmIiwiZW1haWwiOiJkcmRAZ21haWwuY29tIiwicm9sZSI6ImhvdGVsIiwiaWF0IjoxNzY0NjY1MTM0LCJleHAiOjE3NjUyNjk5MzR9.ga5XUbkfj1WduHx5965wUXdFUhaebVoEw4j_uM9tCCY" \
https://travel-studio-backend-e2bkc2e0a8e4e3hy.centralindia-01.azurewebsites.net/YOUR_ENDPOINT_HERE
```

Replace `YOUR_ENDPOINT_HERE` with the endpoint you want to test.
