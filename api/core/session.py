from datetime import datetime
from fastapi import HTTPException
from api.schema.session import CreateSessionRequest, UpdateSessionRequest
from api.models.chat_session import ChatSession
from uuid import uuid4


class Session:
    def __init__(self):
        pass

    def get_user_sessions(self, db, user_id: str):
        try:
            sessions = (
                db.query(ChatSession).filter(ChatSession.user_id == user_id).all()
            )
            if not sessions:
                raise HTTPException(status_code=404, detail="No sessions found")
            return {"sessions": sessions}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=str(f"Failed to get session: {e}")
            )

    def create_session(self, db, request: CreateSessionRequest):
        try:
            new_session = ChatSession(
                session_id=str(uuid4()),
                user_id=request.user_id,
                title=request.title or "New Session",
                time_created=datetime.utcnow(),
                time_updated=datetime.utcnow(),
            )
            db.add(new_session)
            db.commit()
            db.refresh(new_session)
            return new_session
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=str(f"Failed to create session: {e}")
            )

    def edit_session(self, session_id: str, request: UpdateSessionRequest, db):
        try:
            session = (
                db.query(ChatSession)
                .filter(ChatSession.session_id == session_id)
                .first()
            )
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")

            session.title = request.title
            session.time_updated = datetime.utcnow()
            db.commit()
            db.refresh(session)
            return {"detail": "Session updated successfully", "session": session}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=str(f"Failed to update session: {e}")
            )

    def delete_session(self, db, session_id: str):
        try:
            session = (
                db.query(ChatSession)
                .filter(ChatSession.session_id == session_id)
                .first()
            )
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")

            db.delete(session)
            db.commit()
            return {"detail": "Session deleted successfully"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=str(f"Failed to delete session: {e}")
            )

    def delete_user_sessions(self, db, user_id: str):
        try:
            sessions = (
                db.query(ChatSession).filter(ChatSession.user_id == user_id).all()
            )
            if not sessions:
                raise HTTPException(
                    status_code=404, detail="No sessions found for user"
                )

            for session in sessions:
                db.delete(session)
            db.commit()
            return {"detail": f"All sessions for user {user_id} deleted successfully"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=str(f"Failed to delete user sessions: {e}")
            )
