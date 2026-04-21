from sqlalchemy.orm import Session
from app.models.submission import AppSetting


MODERATION_KEY = "moderation_enabled"


def get_or_create_setting(db: Session, key: str, default_value: str) -> AppSetting:
    setting = db.query(AppSetting).filter(AppSetting.key == key).first()
    if not setting:
        setting = AppSetting(key=key, value=default_value)
        db.add(setting)
        db.commit()
        db.refresh(setting)
    return setting


def is_moderation_enabled(db: Session) -> bool:
    setting = get_or_create_setting(db, MODERATION_KEY, "true")
    return setting.value.lower() == "true"


def set_moderation_enabled(db: Session, enabled: bool) -> bool:
    setting = get_or_create_setting(db, MODERATION_KEY, "true")
    setting.value = "true" if enabled else "false"
    db.add(setting)
    db.commit()
    return enabled
