from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from api.schema.session import CreateSessionRequest, UpdateSessionRequest
from api.models.chat_session import ChatSession
from api.database.database import get_db
from uuid import uuid4
from api.config.state import State

router = APIRouter(tags=["Session"])


@router.get("/")
async def get_user_sessions(user_id: str, db=Depends(get_db)):
    try:
        return State.session_controller.get_user_sessions(db, user_id)
    except Exception as e:
        State.logger.error(f"Error getting sessions for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(f"Failed to get session: {e}"))


@router.post("/")
async def create_session(request: CreateSessionRequest, db=Depends(get_db)):
    try:
        return State.session_controller.create_session(db, request)
    except Exception as e:
        State.logger.error(f"Error creating session for user {request.user_id}: {e}")
        raise HTTPException(
            status_code=500, detail=str(f"Failed to create session: {e}")
        )


@router.put("/{session_id}")
async def update_session(
    session_id: str, request: UpdateSessionRequest, db=Depends(get_db)
):
    try:
        session = State.session_controller.edit_session(session_id, request, db)
        return {"detail": "Session updated successfully", "session": session}
    except Exception as e:
        State.logger.error(f"Error updating session {session_id}: {e}")
        raise HTTPException(
            status_code=500, detail=str(f"Failed to update session: {e}")
        )


@router.delete("/{session_id}")
async def delete_session(session_id: str, db=Depends(get_db)):
    try:
        return State.session_controller.delete_session(session_id=session_id, db=db)
    except Exception as e:
        State.logger.error(f"Error deleting session {session_id}: {e}")
        raise HTTPException(
            status_code=500, detail=str(f"Failed to delete session: {e}")
        )


@router.delete("/{user_id}")
async def delete_user_sessions(user_id: str, db=Depends(get_db)):
    try:
        return State.session_controller.delete_user_sessions(user_id=user_id, db=db)
    except Exception as e:
        State.logger.error(f"Error deleting user sessions for user {user_id}: {e}")
        raise HTTPException(
            status_code=500, detail=str(f"Failed to delete user sessions: {e}")
        )


@router.get("/messages")
async def get_session_messages(session_id: str, db=Depends(get_db)):
    try:
        return State.message_controller.get_session_messages(db, session_id)
    except Exception as e:
        State.logger.error(f"Error getting messages for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(f"Failed to get messages: {e}"))


@router.put("/message/like")
async def like_message(message_id: str, like: str, db=Depends(get_db)):
    try:
        return State.message_controller.like_message(message_id, like, db)
    except Exception as e:
        State.logger.error(f"Error liking message {message_id}: {e}")
        raise HTTPException(status_code=500, detail=str(f"Failed to like message: {e}"))


@router.put("/message/feedback")
async def add_message_feedback(
    message_id: str, feedback: str, stars: int, db=Depends(get_db)
):
    try:
        return State.message_controller.submit_feedback(message_id, feedback, stars, db)
    except Exception as e:
        State.logger.error(f"Error adding feedback to message {message_id}: {e}")
        raise HTTPException(
            status_code=500, detail=str(f"Failed to add feedback to message: {e}")
        )
