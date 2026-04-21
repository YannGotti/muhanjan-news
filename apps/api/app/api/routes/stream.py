from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_db
from app.models.submission import Submission
from app.utils.serializers import submission_to_schema

router = APIRouter(tags=["stream"])


@router.get("/stream/feed")
def stream_feed(
    limit: int = Query(default=100, ge=1, le=300),
    db: Session = Depends(get_db),
):
    items = (
        db.query(Submission)
        .options(selectinload(Submission.user), selectinload(Submission.attachments))
        .filter(Submission.status == "approved")
        .order_by(Submission.created_at.desc())
        .limit(limit)
        .all()
    )
    return [submission_to_schema(item).model_dump() for item in items]
