from fastapi import APIRouter, Depends, HTTPException
from api.database.database import get_db
from api.config.state import State

router = APIRouter(tags=["Source"])


@router.post("/")
async def list_sources(db=Depends(get_db)):
    try:
        sources = State.source_controller.list_sources(db)
        return {"sources": sources}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{source_id}")
async def delete_source(source_id: str, db=Depends(get_db)):
    try:
        State.source_controller.delete_source(source_id, db)
        return {"message": f"Source {source_id} deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
