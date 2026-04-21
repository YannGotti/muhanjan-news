import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.user import User
from app.models.submission import Submission, Attachment
from app.schemas.bot import BotUserUpsert, SubmissionCreate, TwitchNicknameUpdate
from app.services.links import extract_links
from app.services.settings import is_moderation_enabled

router = APIRouter(tags=["bot"])


@router.post('/bot/users/upsert')
def upsert_user(payload: BotUserUpsert, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.telegram_id == payload.telegram_id).first()
    if not user:
        user = User(
            telegram_id=payload.telegram_id,
            username=payload.username,
            first_name=payload.first_name,
            last_name=payload.last_name,
        )
        db.add(user)
    else:
        user.username = payload.username
        user.first_name = payload.first_name
        user.last_name = payload.last_name
    db.commit()
    db.refresh(user)
    return {
        'id': user.id,
        'has_twitch_nickname': bool(user.twitch_nickname),
        'is_banned': user.is_banned,
    }


@router.post('/bot/users/twitch')
def set_twitch(payload: TwitchNicknameUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.telegram_id == payload.telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='Пользователь не найден')
    user.twitch_nickname = payload.twitch_nickname.strip()
    db.add(user)
    db.commit()
    return {'ok': True}


@router.get('/bot/users/{telegram_id}')
def get_user_state(telegram_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        return {'exists': False}
    return {
        'exists': True,
        'id': user.id,
        'has_twitch_nickname': bool(user.twitch_nickname),
        'is_banned': user.is_banned,
        'ban_reason': user.ban_reason,
        'twitch_nickname': user.twitch_nickname,
    }


@router.post('/bot/submissions')
def create_submission(payload: SubmissionCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.telegram_id == payload.telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='Пользователь не найден')
    if user.is_banned:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Вы заблокированы и не можете отправлять предложку')
    if not user.twitch_nickname:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Сначала укажите Twitch-ник')

    links = payload.links or extract_links(payload.message_text)
    status_value = 'pending' if is_moderation_enabled(db) else 'approved'

    submission = Submission(
        user_id=user.id,
        message_text=payload.message_text,
        links_json=json.dumps(links, ensure_ascii=False),
        status=status_value,
        source_message_id=payload.source_message_id,
    )
    db.add(submission)
    db.flush()

    for item in payload.attachments:
        db.add(Attachment(
            submission_id=submission.id,
            telegram_file_id=item.telegram_file_id,
            telegram_unique_file_id=item.telegram_unique_file_id,
            file_type=item.file_type,
            original_name=item.original_name,
            mime_type=item.mime_type,
            file_size=item.file_size,
            storage_path=item.storage_path,
            public_url=item.public_url,
        ))

    db.commit()
    db.refresh(submission)
    return {'ok': True, 'submission_id': submission.id, 'status': submission.status}
