from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from db import SessionLocal, UserRequest, ChatHistory, init_db  # your db.py

# ------------------- Initialize DB -------------------
init_db()

# ------------------- Pydantic Models -------------------
class ChatItem(BaseModel):
    role: str
    content: str

class UserRequestItem(BaseModel):
    name: str
    phone: str
    email: str | None = None
    business_type: str
    location: str
    purpose: str
    days_needed: str | None = None
    chat_history: List[ChatItem] | None = []

# ------------------- FastAPI App -------------------
app = FastAPI(title="AbidPA 2 Agent API")

# ------------------- CORS -------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------- Root Route -------------------
@app.get("/")
def read_root():
    return {"message": "AI Agent is running!"}

# ------------------- Simple HTML Interface -------------------
@app.get("/interface", response_class=HTMLResponse)
def get_interface():
    html_content = """
    <html>
        <head>
            <title>AbidPA 2 Agent</title>
        </head>
        <body>
            <h1>Welcome to AbidPA 2 Agent!</h1>
            <p>Use the API endpoints:</p>
            <ul>
                <li><b>POST /user_request</b> to submit a request.</li>
                <li><b>GET /user_requests</b> to see all requests.</li>
                <li><b>Swagger UI:</b> /docs</li>
            </ul>
        </body>
    </html>
    """
    return html_content

# ------------------- Create User Request -------------------
@app.post("/user_request", response_model=UserRequestItem)
def create_user_request(request: UserRequestItem):
    db: Session = SessionLocal()
    try:
        db_request = UserRequest(
            name=request.name,
            phone=request.phone,
            email=request.email,
            business_type=request.business_type,
            location=request.location,
            purpose=request.purpose,
            days_needed=request.days_needed
        )
        db.add(db_request)
        db.commit()
        db.refresh(db_request)

        for chat in request.chat_history or []:
            db_chat = ChatHistory(
                user_request_id=db_request.id,
                role=chat.role,
                content=chat.content
            )
            db.add(db_chat)
        db.commit()
        return request
    finally:
        db.close()

# ------------------- Get All User Requests -------------------
@app.get("/user_requests", response_model=List[UserRequestItem])
def get_user_requests():
    db: Session = SessionLocal()
    try:
        requests = db.query(UserRequest).all()
        result = []
        for r in requests:
            chats = [ChatItem(role=c.role, content=c.content) for c in r.chat_history]
            result.append(UserRequestItem(
                name=r.name,
                phone=r.phone,
                email=r.email,
                business_type=r.business_type,
                location=r.location,
                purpose=r.purpose,
                days_needed=r.days_needed,
                chat_history=chats
            ))
        return result
    finally:
        db.close()
