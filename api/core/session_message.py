from typing import Dict, List
from api.models.session_messages import SessionMessages
from fastapi import HTTPException
from datetime import datetime
from uuid import uuid4


class SessionMessage:
    def __init__(self):
        pass

    def get_session_messages(self, db, session_id: str):
        try:
            messages = (
                db.query(SessionMessages)
                .filter(SessionMessages.session_id == session_id)
                .order_by(SessionMessages.timestamp)
                .all()
            )
            if not messages:
                return {"messages": []}
            return {"messages": messages}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=str(f"Failed to get messages: {e}")
            )

    def add_message(self, db, session_id: str, content: Dict, sources: List):
        try:
            new_message = SessionMessages(
                message_id=str(uuid4()),
                session_id=session_id,
                content=content,
                sources=sources,
                timestamp=datetime.utcnow(),
            )
            db.add(new_message)
            db.commit()
            db.refresh(new_message)
            return new_message
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=str(f"Failed to add message: {e}")
            )

    def like_message(self, message_id: str, like: str, db):
        try:
            message = (
                db.query(SessionMessages)
                .filter(SessionMessages.message_id == message_id)
                .first()
            )
            if not message:
                raise HTTPException(status_code=404, detail="Message not found")

            message.like = like
            db.commit()
            db.refresh(message)
            return {
                "detail": "Message liked successfully",
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=str(f"Failed to like message: {e}")
            )

    def submit_feedback(self, message_id: str, feedback: str, stars: int, db):
        try:
            message = (
                db.query(SessionMessages)
                .filter(SessionMessages.message_id == message_id)
                .first()
            )
            if not message:
                raise HTTPException(status_code=404, detail="Message not found")

            message.feedback = feedback if feedback else message.feedback
            message.stars = stars if stars else message.stars
            db.commit()
            db.refresh(message)
            return {
                "detail": "Feedback submitted successfully",
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=str(f"Failed to submit feedback: {e}")
            )
