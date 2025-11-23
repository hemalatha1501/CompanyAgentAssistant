Company Agent Assistant:-
Company Agent Assistant is a full-stack web application that simulates a company agent. The frontend is built using HTML, CSS, and JavaScript, while the backend uses Node.js and Express to handle chat interactions.

Setup Instructions:-
1. Clone the Repository
git clone https://github.com/hemalatha1501/CompanyAgentAssistant.git
cd CompanyAgentAssistant

2. Backend Setup
Navigate to the backend folder (if separated):
cd backend

Install dependencies:
npm install

Start the server:
node server.js

The backend will run on http://localhost:3000 by default.

3. Frontend Setup
Navigate to the frontend folder (or root if combined):
cd ../frontend

Open index.html in a browser.
(Optional: Use VS Code Live Server for automatic refresh.)

4. Using the Application
Open the app in your browser.
Type a message in the chat box.
Receive AI-like responses simulated by the backend.

Architecture Notes:-

Frontend:
Built with HTML for structure, CSS for styling, and JavaScript for interactivity.
Uses a responsive layout and aesthetic icons for a modern UI.

Backend:
Node.js with Express handles incoming chat requests.
Provides mock AI responses; structured for future integration with real AI APIs.

Data Flow:
User enters a message in the frontend chat interface.
Frontend sends the message to the backend API via fetch/XHR.
Backend processes the message and returns a response.
Frontend displays the response in the chat interface.

Folder Structure:
CompanyAgentAssistant/
│
├─ frontend/
│   ├─ index.html
│   ├─ style.css
│   └─ script.js
│   └─ README_FRONTEND
├─ backend/
│   ├─ server.js
│   └─ data.json 
│   └─ README_BACKEND
└─ README.md

Design Decisions
Frontend-First Approach:
Focused on creating a responsive and visually appealing interface to engage users.

Mock Backend:
Chose a simple Node.js backend to simulate AI responses without needing an actual AI API.
Enables easy future upgrade to real AI integration.

Technology Stack:
HTML, CSS, JavaScript: Lightweight, fast, and easy to maintain.
Node.js + Express: Minimal setup, handles requests efficiently.

Scalability:
Backend structured to support adding real AI APIs, persistent chat storage, and user authentication in future.

User Experience:
Modern color scheme and icons improve visual appeal.
Responsive design ensures accessibility across devices.
Modern color scheme and icons improve visual appeal.

Responsive design ensures accessibility across devices.
