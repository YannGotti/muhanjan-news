MENU_SEND = "Отправить материал"
MENU_STATUS = "Мой статус"
MENU_RECENT = "Мои последние"
MENU_CHANGE_TWITCH = "Изменить Twitch"
MENU_HELP = "Как отправить"
MENU_MENU = "Показать меню"

MAIN_MENU_BUTTONS = [
    [MENU_SEND, MENU_STATUS],
    [MENU_RECENT, MENU_CHANGE_TWITCH],
    [MENU_HELP, MENU_MENU],
]

START_GREETING = (
    "<b>MuhanjanNews</b>\n\n"
    "Это бот для отправки материалов в предложку. "
    "Ты можешь прислать текст, ссылку, фото, документ, анимацию, голосовое, аудио или видео."
)

FIRST_TWITCH_REQUEST = (
    "Для начала укажи свой <b>Twitch-ник</b>.\n"
    "Пример: <code>muhanjan</code>\n\n"
    "После этого бот откроет полное меню и ты сможешь отправлять материалы."
)

HELP_TEXT = (
    "<b>Как отправить материал</b>\n\n"
    "1. Отправь <b>одним сообщением</b> текст, ссылку, фото, документ, голосовое, аудио, анимацию или видео.\n"
    "2. Бот сначала покажет предпросмотр, а потом предложит подтвердить отправку.\n"
    "3. После отправки бот скажет, материал ушёл на проверку или сразу опубликован.\n\n"
    "<b>Лучше всего присылать так:</b>\n"
    "• краткий понятный текст\n"
    "• одна тема в одном сообщении\n"
    "• если есть ссылка — добавь её в это же сообщение\n"
    "• если есть файл — приложи его сразу"
)

SEND_HINT_TEXT = (
    "<b>Что можно отправить прямо сейчас</b>\n\n"
    "• текст\n"
    "• ссылку\n"
    "• фото\n"
    "• документ\n"
    "• анимацию\n"
    "• голосовое\n"
    "• аудио\n"
    "• видео\n\n"
    "Просто пришли это <b>одним сообщением</b>. "
    "Бот покажет предпросмотр и попросит подтвердить отправку."
)

STATUS_TEMPLATE = (
    "<b>Твой статус</b>\n\n"
    "Twitch: <code>{twitch}</code>\n"
    "Отправка: {sending}\n"
    "{ban_line}"
)

BAN_LINE = "Причина ограничения: <i>{reason}</i>"

TWITCH_UPDATED = (
    "Готово. Сохранил Twitch-ник: <code>{nickname}</code>\n\n"
    "Теперь можешь отправлять материалы."
)

ASK_NEW_TWITCH = (
    "Отправь новый <b>Twitch-ник</b> одним сообщением.\n"
    "Минимум 3 символа, без лишнего текста."
)

TWITCH_TOO_SHORT = "Twitch-ник должен быть длиной хотя бы 3 символа."

BANNED_MESSAGE = (
    "Сейчас отправка для тебя недоступна.\n"
    "{reason_block}"
)

BANNED_REASON_BLOCK = "Причина: <i>{reason}</i>"

SUBMISSION_SUCCESS_PENDING = (
    "Материал принят. Он отправлен в <b>очередь на проверку</b>."
)

SUBMISSION_SUCCESS_APPROVED = (
    "Материал принят и <b>сразу опубликован</b>."
)

SUBMISSION_FAILED = (
    "Не удалось принять материал. Попробуй ещё раз чуть позже."
)

NEED_TWITCH_FIRST = (
    "Сначала укажи Twitch-ник. Нажми /start или кнопку «Изменить Twitch»."
)

FALLBACK_TEXT = (
    "Я не понял сообщение.\n\n"
    "Нажми «Как отправить», чтобы увидеть формат, "
    "или просто пришли материал одним сообщением."
)

EMPTY_SUBMISSION = (
    "В этом сообщении нет текста, ссылки, фото, документа, анимации, голосового, аудио или видео. "
    "Отправь материал ещё раз."
)

RATE_LIMIT_MESSAGE = (
    "Ты отправляешь материалы слишком быстро. "
    "Подожди ещё <b>{seconds}</b> сек. и попробуй снова."
)

DUPLICATE_SUBMISSION_MESSAGE = (
    "Это сообщение уже обрабатывается или уже было отправлено."
)

API_TEMPORARY_UNAVAILABLE = (
    "Сервис временно недоступен. Попробуй ещё раз чуть позже."
)

PROFILE_TEMPORARY_UNAVAILABLE = (
    "Не удалось получить твой статус прямо сейчас. Попробуй ещё раз."
)

GENERIC_ERROR_MESSAGE = (
    "Что-то пошло не так. Попробуй выполнить действие ещё раз."
)

FILE_TOO_LARGE_MESSAGE = (
    "Файл слишком большой. Максимальный размер — <b>{max_size_mb} МБ</b>."
)

RECENT_SUBMISSIONS_EMPTY = (
    "У тебя пока нет отправленных материалов."
)

RECENT_SUBMISSIONS_HEADER = (
    "<b>Твои последние материалы</b>\n\n{items}"
)

RECENT_SUBMISSION_ITEM = (
    "• <b>#{id}</b> · {status_label}\n"
    "  {created_at}\n"
    "  {preview}{comment_block}"
)

RECENT_COMMENT_BLOCK = "\n  Комментарий модератора: {comment}"

SUBMISSION_PREVIEW_HEADER = (
    "<b>Предпросмотр материала</b>\n\n"
    "{summary}\n\n"
    "Проверь всё и нажми кнопку ниже."
)

SUBMISSION_PREVIEW_EXPIRED = (
    "Предпросмотр уже устарел. Отправь материал ещё раз."
)

SUBMISSION_PREVIEW_CANCELED = (
    "Отправка отменена. Можешь прислать другой материал."
)

SUBMISSION_ALREADY_SENT_MESSAGE = (
    "Этот материал уже был отправлен ранее."
)

PREVIEW_TEXT_LABEL = "Текст"
PREVIEW_LINKS_LABEL = "Ссылки"
PREVIEW_ATTACHMENTS_LABEL = "Вложения"
PREVIEW_NO_TEXT = "без текста"
PREVIEW_NO_ATTACHMENTS = "нет"
PREVIEW_CONFIRM = "Отправить"
PREVIEW_CANCEL = "Отмена"
