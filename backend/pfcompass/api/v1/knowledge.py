from typing import List
from fastapi import APIRouter, Query
from pydantic import BaseModel

from pfcompass.ai.rag_retriever import rag_retriever

router = APIRouter(prefix="/knowledge", tags=["RAG Knowledge Base"])


class KnowledgeChunkResponse(BaseModel):
    chunk_id: str
    doc_title: str
    section: str
    content: str
    scheme_reference: str


@router.get("/search", response_model=List[KnowledgeChunkResponse])
async def search_knowledge(
    q: str = Query(..., description="Natural language search query for EPFO scheme rules"),
    limit: int = Query(3, ge=1, le=10)
):
    """Semantic vector search over authentic EPFO scheme documentation."""
    chunks = rag_retriever.retrieve(q, top_k=limit)
    return [
        KnowledgeChunkResponse(
            chunk_id=c.chunk_id,
            doc_title=c.doc_title,
            section=c.section,
            content=c.content,
            scheme_reference=c.scheme_reference
        )
        for c in chunks
    ]
