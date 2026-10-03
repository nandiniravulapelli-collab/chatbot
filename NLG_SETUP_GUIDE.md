# NLG Integration Setup Guide

## Overview
This guide explains how to set up and use the Natural-Language Generation (NLG) feature that has been added to your AI-Powered Smart University Assistant Chatbot.

## What's New
- **Google Gemini API Integration**: The chatbot now uses Google's Gemini API for natural language generation
- **Context-Aware Responses**: Responses are generated using relevant information from MongoDB
- **Conversation History**: The system considers recent conversation history for follow-up questions
- **Fallback Mechanism**: If NLG fails, the system automatically falls back to the existing FAQ/ML response system

## Installation Steps

### 1. Install Dependencies
The required packages have been added to `requirements.txt`:
- `google-generativeai==0.3.2` - Google Gemini API client
- `python-dotenv==1.0.0` - Environment variable management

Install them:
```bash
cd project
pip install -r requirements.txt
```

### 2. Get a Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the API key

### 3. Configure Environment Variables
Edit the `.env` file in the project directory and add your Gemini API key:

```env
SECRET_KEY=university-chatbot-secret-key-2024
MONGO_URI=mongodb://localhost:27017/university_chatbot
GEMINI_API_KEY=your-actual-gemini-api-key-here
```

Replace `your-actual-gemini-api-key-here` with your actual API key.

## How It Works

### Response Generation Flow
1. **User Question**: User asks a question
2. **Intent Prediction**: The existing ML system predicts the intent and retrieves relevant context from MongoDB
3. **Context Gathering**: System collects:
   - Relevant MongoDB data (FAQs, fee structure, exam schedules, etc.)
   - Recent conversation history (last 5 exchanges)
4. **NLG Generation**: Gemini API generates a natural, conversational response using the context
5. **Fallback**: If NLG fails, the system uses the original FAQ/ML response
6. **Response Delivery**: The response is sent to the user with metadata indicating the source (NLG or FAQ)

### Key Features

#### Context-Aware Responses
The NLG system uses MongoDB context to ensure responses are accurate:
- **FAQ Data**: Relevant FAQ entries
- **University Data**: Fee structure, exam schedules, hostel info, library timings, etc.
- **No Hallucinations**: The system is instructed to only use provided context

#### Conversation History
The system maintains context from recent conversations:
- Last 5 Q&A exchanges are included in the prompt
- Enables follow-up questions like "What about the hostel fee?"
- Maintains conversation flow

#### Fallback Mechanism
If NLG fails for any reason:
- API key not configured
- API quota exceeded
- Network issues
- Invalid responses

The system automatically falls back to the existing FAQ/ML response system, ensuring the chatbot remains functional.

## Testing

### Test the NLG Integration
Run the test script:
```bash
cd project
python test_nlg.py
```

This will:
- Verify the NLG generator initialization
- Test response generation with sample data
- Verify the fallback mechanism

### Test with the Full Application
1. Start MongoDB (if not already running)
2. Start the Flask application:
```bash
cd project
python app.py
```
3. Open the chatbot interface in your browser
4. Ask questions and observe the responses
5. Check the response source in the API response (check browser console or network tab)

## Configuration Options

### Adjust Conversation History Length
In `app.py`, modify the limit in the chat route:
```python
conversation_history = list(chat_history_col.find(
    {'user_id': user_id},
    {'question': 1, 'answer': 1}
).sort('timestamp', -1).limit(5))  # Change 5 to desired number
```

### Modify NLG Prompt
In `ml/nlg_generator.py`, edit the `_build_prompt` method to customize:
- System instructions
- Context formatting
- Response style guidelines

### Disable NLG Temporarily
To disable NLG temporarily without removing the code:
1. Set `GEMINI_API_KEY` to empty string in `.env`
2. The system will automatically fall back to FAQ responses

## Troubleshooting

### "GEMINI_API_KEY not found" Error
- Ensure `.env` file exists in the project directory
- Verify the API key is set correctly
- Restart the Flask application after changing `.env`

### NLG Not Working
- Check if the API key is valid
- Verify you have API quota available
- Check your internet connection
- Review Flask application logs for errors

### Responses Still Using FAQ
- This is normal fallback behavior if NLG fails
- Check the `response_source` field in the API response
- Review logs for NLG generation errors

### Context Not Being Used
- Verify MongoDB collections have data
- Check that the intent prediction is working correctly
- Review the context data being passed to the NLG generator

## File Changes Summary

### New Files
- `ml/nlg_generator.py` - NLG generator using Gemini API
- `test_nlg.py` - Test script for NLG integration
- `.env.example` - Example environment variables file
- `.env` - Your actual environment variables (not in git)
- `.gitignore` - Updated to ignore .env but keep .env.example
- `NLG_SETUP_GUIDE.md` - This setup guide

### Modified Files
- `requirements.txt` - Added Gemini and dotenv dependencies
- `config.py` - Added GEMINI_API_KEY configuration and dotenv loading
- `app.py` - Integrated NLG with fallback mechanism
- `ml/predict.py` - Updated to return context data along with responses

## Security Notes

- **Never commit `.env` to version control** - It contains sensitive API keys
- **Rotate API keys regularly** - Follow Google's security best practices
- **Monitor API usage** - Check your Google Cloud console for usage patterns
- **Use environment variables** - Don't hardcode API keys in source code

## Next Steps

1. ✅ Install dependencies (completed if you ran pip install)
2. ⏳ Get your Gemini API key
3. ⏳ Configure `.env` with your API key
4. ⏳ Test with `python test_nlg.py`
5. ⏳ Start the application and test the chatbot
6. ⏳ Monitor logs and adjust prompt if needed

## Support

If you encounter issues:
1. Check the Flask application logs
2. Review the test script output
3. Verify your API key in Google Cloud Console
4. Check Google Gemini API status page

## API Key Management

To keep your API key secure:
- Use the `.env` file (already configured)
- Add `.env` to `.gitignore` (already done)
- Use different API keys for development and production
- Set up API key restrictions in Google Cloud Console
