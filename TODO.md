# TODO: Integrate NLP Chatbot Sentiment Analysis

## Steps to Complete Integration

- [x] Update backend/requirements.txt to include google-generativeai for Gemini-Pro API
- [x] Add ChatHistory model to backend/models.py for storing chat interactions in database
- [x] Update backend/.env to include GOOGLE_API_KEY placeholder
- [x] Modify backend/routes/chat_routes.py to generate AI responses using Gemini-Pro, analyze sentiment on responses, and save to database
- [x] Enhance frontend/src/pages/Chat.jsx to display AI responses and sentiment data in chat history
- [x] Install updated dependencies in backend
- [ ] Test integrated chat functionality with authentication
- [ ] Verify sentiment analysis and AI response generation
