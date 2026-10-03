# MongoDB Setup Guide for UniBot

## Issue: HTTP 500 Error on Sign-in

The HTTP 500 error you're experiencing is caused by **MongoDB not running**. The UniBot application requires MongoDB to be running to handle user authentication, data storage, and chat history.

## Solution: Start MongoDB

### Windows

#### Option 1: Using MongoDB as a Service (Recommended)

1. Open **Command Prompt** as Administrator
2. Start MongoDB service:
   ```cmd
   net start MongoDB
   ```

If the service is not installed, install MongoDB first:
1. Download MongoDB from [https://www.mongodb.com/try/download/community](https://www.mongodb.com/try/download/community)
2. Install with default settings
3. Install as a service during installation

#### Option 2: Start MongoDB Manually

1. Create data directory if it doesn't exist:
   ```cmd
   mkdir C:\data\db
   ```

2. Start MongoDB:
   ```cmd
   "C:\Program Files\MongoDB\Server\7.0\bin\mongod.exe" --dbpath C:\data\db
   ```

#### Option 3: Using MongoDB Atlas (Cloud - Easiest)

If you don't want to install MongoDB locally:

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free account
3. Create a free cluster
4. Get your connection string
5. Update `.env` file with your Atlas connection string:
   ```env
   MONGO_URI=mongodb+srv://your_username:your_password@cluster0.mongodb.net/university_chatbot
   ```

### Linux/Mac

#### Start MongoDB Service
```bash
sudo systemctl start mongod
```

#### Or Start Manually
```bash
mongod --dbpath /data/db
```

## Verify MongoDB is Running

Open a new terminal and run:
```bash
# Windows
mongo

# Linux/Mac
mongosh
```

If MongoDB is running, you'll see the MongoDB shell prompt.

## Update Application Configuration

Your current configuration in `.env`:
```env
MONGO_URI=mongodb://localhost:27017/university_chatbot
```

This is correct for local MongoDB. If using MongoDB Atlas, update it with your connection string.

## Start the Application

Once MongoDB is running:

1. Start the Flask application:
   ```bash
   cd project
   venv\Scripts\python.exe app.py
   ```

2. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

3. Try signing in - the error should be resolved

## Troubleshooting

### MongoDB won't start

**Windows:**
- Check if another MongoDB instance is already running: `tasklist | findstr mongo`
- Kill existing processes: `taskkill /F /IM mongod.exe`
- Check MongoDB logs in: `C:\Program Files\MongoDB\Server\7.0\log\mongod.log`

**Linux/Mac:**
- Check logs: `sudo journalctl -u mongod`
- Check if port 27017 is in use: `sudo lsof -i :27017`

### Connection errors

If you still get connection errors:

1. Verify MongoDB is running: `mongosh` or `mongo`
2. Check the MongoDB URI in `.env` is correct
3. Ensure firewall is not blocking port 27017
4. Check MongoDB logs for errors

### Quick Test

Test MongoDB connection with Python:
```bash
cd project
venv\Scripts\python.exe -c "from pymongo import MongoClient; client = MongoClient('mongodb://localhost:27017'); print('Connected successfully' if client.admin.command('ping') else 'Connection failed')"
```

## Alternative: Use Mock Data for Testing

If you want to test the application without MongoDB temporarily, you can modify the database connection to use mock data. However, this is not recommended for production use.

## Summary

The HTTP 500 error is a **MongoDB connection issue**, not a code problem. Once MongoDB is running, the sign-in functionality will work correctly.

**Quick Fix:**
1. Start MongoDB: `net start MongoDB` (Windows) or `sudo systemctl start mongod` (Linux/Mac)
2. Refresh the application
3. Try signing in again

If you need help with MongoDB installation or configuration, please let me know!
