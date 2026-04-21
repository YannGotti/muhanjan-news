from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.submission import Submission
from app.utils.serializers import submission_to_schema

router = APIRouter(tags=['stream'])


@router.get('/stream/feed')
def stream_feed(limit: int = 100, db: Session = Depends(get_db)):
    items = (
        db.query(Submission)
        .filter(Submission.status == 'approved')
        .order_by(Submission.created_at.desc())
        .limit(limit)
        .all()
    )
    return [submission_to_schema(item).model_dump() for item in items]
