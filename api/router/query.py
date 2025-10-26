from fastapi import APIRouter, Depends, HTTPException
from api.models.models import QueryRequest, QueryResponse
from api.config.state import State
from api.database.database import get_db

router = APIRouter(tags=["Query"])


@router.post("/")
async def process_query(request: QueryRequest, db=Depends(get_db)):
    try:
        response = State.query_controller.generate_response(
            query=request.query,
            category=request.state.category,
            sub_category=request.state.sub_category,
            model_name=request.state.model_name,
            top_k=request.state.top_k,
            session_id=request.session_id,
            memory_service=request.state.memory_service,
            temperature=request.state.temperature,
            db=db,
        )
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reddit")
async def process_reddit_query(
    request: QueryRequest, db=Depends(get_db)
):
    try:
        response = State.query_controller.generate_reddit_response(
            query=request.query,
            model_name=request.state.model_name,
            temperature=request.state.temperature,
            username=request.state.reddit_username,
            relevance=request.state.relevance,
            top_k=request.state.top_k,
            session_id=request.session_id,
            memory_service=request.state.memory_service,
            db=db,
        )
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
