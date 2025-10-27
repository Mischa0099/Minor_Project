# GenAI Healthcare Assistant (Phase 1)

A full-stack web application prototype for healthcare using AI-powered sentiment analysis.

## Features

- User authentication (register/login) with JWT
- User profile management
- Chat interface for sentiment analysis
- Flask backend with Hugging Face Transformers
- React frontend with TailwindCSS

## Project Structure

```
genai-healthcare-assistant/
├── backend/
│   ├── app.py
│   ├── models.py
│   ├── routes/
│   │   ├── auth_routes.py
│   │   ├── user_routes.py
│   │   └── chat_routes.py
│   ├── requirements.txt
│   ├── .env
│   └── database.db (created on first run)
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── Navbar.jsx
    │   │   └── Footer.jsx
    │   ├── pages/
    │   │   ├── Home.jsx
    │   │   ├── Login.jsx
    │   │   ├── Register.jsx
    │   │   ├── Profile.jsx
    │   │   └── Chat.jsx
    │   ├── App.jsx
    │   ├── index.js
    │   └── index.css
    └── package.json
```

## Setup Instructions

### Backend

1. Navigate to backend directory:
   ```
   cd backend
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the Flask app:
   ```
   python app.py
   ```
   The backend will start on http://localhost:5000

### Frontend

1. Navigate to frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the React app:
   ```
   npm start
   ```
   The frontend will start on http://localhost:3000

## Usage

1. Register a new account or login.
2. Update your profile with personal details.
3. Go to the Chat page and send messages.
4. Sentiment analysis results are printed in the backend terminal.

## Future Extensions

- Integrate chatbot responses based on sentiment.
- Migrate to MongoDB for scalability.
- Add IoT device data connection.
- Implement dashboards for health metrics.

## Notes

- Sentiment model loads on server startup (may take time).
- Database is SQLite for simplicity; can be changed to PostgreSQL/MySQL.
- JWT tokens are stored in localStorage (not secure for production).
