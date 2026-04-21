from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_admin, get_db
from app.models.user import User
from app.models.submission import Submission, ModerationAction
from app.schemas.admin import ReviewRequest, BanRequest
from app.utils.serializers import submission_to_schema

router = APIRouter(tags=["admin"])


def log_action(
    db: Session,
    actor: str,
    action_type: str,
    submission_id: int | None = None,
    user_id: int | None = None,
    comment: str | None = None,
):
    db.add(
        ModerationAction(
            submission_id=submission_id,
            user_id=user_id,
            action_type=action_type,
            actor_username=actor,
            comment=comment,
        )
    )
    db.commit()


def _apply_submission_filters(
    query,
    *,
    status: str | None,
    q: str | None,
    has_text: bool | None,
    has_attachments: bool | None,
    has_links: bool | None,
):
    if status:
        query = query.filter(Submission.status == status)

    if q:
        term = f"%{q.strip()}%"
        query = query.join(User).filter(
            or_(
                User.twitch_nickname.ilike(term),
                User.username.ilike(term),
                User.first_name.ilike(term),
                User.last_name.ilike(term),
                Submission.message_text.ilike(term),
                Submission.links_json.ilike(term),
            )
        )

    if has_text is True:
        query = query.filter(Submission.message_text.is_not(None), Submission.message_text != "")
    elif has_text is False:
        query = query.filter(or_(Submission.message_text.is_(None), Submission.message_text == ""))

    if has_attachments is True:
        query = query.filter(Submission.attachments.any())
    elif has_attachments is False:
        query = query.filter(~Submission.attachments.any())

    if has_links is True:
        query = query.filter(Submission.links_json.is_not(None), Submission.links_json != "[]")
    elif has_links is False:
        query = query.filter(or_(Submission.links_json.is_(None), Submission.links_json == "[]"))

    return query


@router.get("/admin/submissions")
def list_submissions(
    status: str | None = None,
    q: str | None = None,
    has_text: bool | None = None,
    has_attachments: bool | None = None,
    has_links: bool | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    _: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    base_query = (
        db.query(Submission)
        .options(selectinload(Submission.user), selectinload(Submission.attachments))
        .order_by(Submission.created_at.desc())
    )

    filtered_query = _apply_submission_filters(
        base_query,
        status=status,
        q=q,
        has_text=has_text,
        has_attachments=has_attachments,
        has_links=has_links,
    )

    total = filtered_query.order_by(None).count()
    items = filtered_query.offset(offset).limit(limit).all()

    return {
        "items": [submission_to_schema(item).model_dump() for item in items],
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + len(items) < total,
    }


@router.post("/admin/submissions/{submission_id}/approve")
def approve_submission(
    submission_id: int,
    payload: ReviewRequest,
    actor: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    item = (
        db.query(Submission)
        .options(selectinload(Submission.user), selectinload(Submission.attachments))
        .filter(Submission.id == submission_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Предложка не найдена")

    item.status = "approved"
    item.approved_at = datetime.now(timezone.utc)
    item.rejected_at = None
    item.review_comment = payload.comment
    db.add(item)
    db.commit()

    log_action(
        db,
        actor=actor,
        action_type="approve",
        submission_id=item.id,
        user_id=item.user_id,
        comment=payload.comment,
    )
    return {"ok": True}


@router.post("/admin/submissions/{submission_id}/reject")
def reject_submission(
    submission_id: int,
    payload: ReviewRequest,
    actor: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    item = db.query(Submission).filter(Submission.id == submission_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Предложка не найдена")

    item.status = "rejected"
    item.rejected_at = datetime.now(timezone.utc)
    item.approved_at = None
    item.review_comment = payload.comment
    db.add(item)
    db.commit()

    log_action(
        db,
        actor=actor,
        action_type="reject",
        submission_id=item.id,
        user_id=item.user_id,
        comment=payload.comment,
    )
    return {"ok": True}


@router.post("/admin/users/{user_id}/ban")
def ban_user(
    user_id: int,
    payload: BanRequest,
    actor: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    user.is_banned = True
    user.ban_reason = payload.reason or "Заблокирован модератором"
    db.add(user)
    db.commit()

    log_action(db, actor=actor, action_type="ban_user", user_id=user.id, comment=user.ban_reason)
    return {"ok": True}


@router.post("/admin/users/{user_id}/unban")
def unban_user(
    user_id: int,
    actor: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    user.is_banned = False
    user.ban_reason = None
    db.add(user)
    db.commit()

    log_action(db, actor=actor, action_type="unban_user", user_id=user.id)
    return {"ok": True}
