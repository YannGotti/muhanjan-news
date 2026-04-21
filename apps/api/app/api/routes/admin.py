from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_db
from app.models.user import User
from app.models.submission import Submission, ModerationAction
from app.schemas.admin import ReviewRequest, BanRequest
from app.utils.serializers import submission_to_schema

router = APIRouter(tags=['admin'])


def log_action(db: Session, actor: str, action_type: str, submission_id: int | None = None, user_id: int | None = None, comment: str | None = None):
    db.add(ModerationAction(
        submission_id=submission_id,
        user_id=user_id,
        action_type=action_type,
        actor_username=actor,
        comment=comment,
    ))
    db.commit()


@router.get('/admin/submissions')
def list_submissions(
    status: str | None = None,
    _: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    query = db.query(Submission).order_by(Submission.created_at.desc())
    if status:
        query = query.filter(Submission.status == status)
    items = query.all()
    return [submission_to_schema(item).model_dump() for item in items]


@router.post('/admin/submissions/{submission_id}/approve')
def approve_submission(
    submission_id: int,
    payload: ReviewRequest,
    actor: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    item = db.query(Submission).filter(Submission.id == submission_id).first()
    if not item:
        raise HTTPException(status_code=404, detail='Предложка не найдена')
    item.status = 'approved'
    item.approved_at = datetime.now(timezone.utc)
    item.review_comment = payload.comment
    db.add(item)
    db.commit()
    log_action(db, actor=actor, action_type='approve', submission_id=item.id, user_id=item.user_id, comment=payload.comment)
    return {'ok': True}


@router.post('/admin/submissions/{submission_id}/reject')
def reject_submission(
    submission_id: int,
    payload: ReviewRequest,
    actor: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    item = db.query(Submission).filter(Submission.id == submission_id).first()
    if not item:
        raise HTTPException(status_code=404, detail='Предложка не найдена')
    item.status = 'rejected'
    item.rejected_at = datetime.now(timezone.utc)
    item.review_comment = payload.comment
    db.add(item)
    db.commit()
    log_action(db, actor=actor, action_type='reject', submission_id=item.id, user_id=item.user_id, comment=payload.comment)
    return {'ok': True}


@router.post('/admin/users/{user_id}/ban')
def ban_user(
    user_id: int,
    payload: BanRequest,
    actor: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='Пользователь не найден')
    user.is_banned = True
    user.ban_reason = payload.reason or 'Заблокирован модератором'
    db.add(user)
    db.commit()
    log_action(db, actor=actor, action_type='ban_user', user_id=user.id, comment=user.ban_reason)
    return {'ok': True}


@router.post('/admin/users/{user_id}/unban')
def unban_user(
    user_id: int,
    actor: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='Пользователь не найден')
    user.is_banned = False
    user.ban_reason = None
    db.add(user)
    db.commit()
    log_action(db, actor=actor, action_type='unban_user', user_id=user.id)
    return {'ok': True}
