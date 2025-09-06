# Telegram Channel Cloner / Клонирование канала Telegram

> English first – русская версия ниже.

---

## English

### ⚠️ Legal & Ethical Notice

This tool is for educational, archival, migration and personal backup purposes only. You are solely responsible for ensuring you have the right to copy content. The authors assume **no liability** for misuse.

### ✅ Features

- Full re-upload based cloning (text + media) – not forwarding.
- Works with private/public channels (ID, invite link, @username).
- Photos / documents / videos / audio / GIF / stickers handled.
- Formatting preserved where possible (entities, links, bold/italic).
- Auto flood-wait handling & retry logic.
- Three resume modes: by message ID, text fragment, or chronological position.
- Autosave file (`progress_<channel>.log`) with source message links.
- Temporary media deleted after upload (saves disk space).
- Detailed logging + ETA.
- Demo mode (no sending, analysis only).

### 🗂 Structure

```text
main.py          # Core logic (copy + resume + autosave)
config.py        # Configuration & resume parameters
logger_utils.py  # Logging helpers
progress_*.log   # Autosaved source links (generated)
media_*/         # Temporary media files (per source channel)
logs/            # Run logs
```

### ⚙️ Install

```bash
pip install telethon
```

### 🔐 Telegram API Setup

1. <https://my.telegram.org> → API Development Tools.
2. Create app → copy API ID / hash.
3. First run will request phone + code (and 2FA if enabled).

### 🛠 Configure (`config.py` excerpt)

```python
API_ID = "YOUR_ID"
API_HASH = "YOUR_HASH"
PHONE = "+123456789"

SOURCE_CHANNEL = -1001234567890
TARGET_CHANNEL = "@your_target"

START_FROM_MESSAGE_ID = 1239   # Highest priority (or None)
RESUME_FROM_TEXT = None        # Fallback by text fragment
SKIP_TO_POSITION = None        # Fallback numeric position (1 = oldest)

DELAY_BETWEEN_MESSAGES = 1.0
DOWNLOAD_MEDIA = True
PRESERVE_FORMATTING = True
DEMO_MODE = False
```

### ▶️ Run

```bash
python main.py
```

Log + autosave appear in workspace.

### 🔄 Resume Strategy

Order of precedence: `START_FROM_MESSAGE_ID` > `RESUME_FROM_TEXT` > `SKIP_TO_POSITION`.
Use message ID for precision (from copied link: last number in `https://t.me/c/<internal>/<id>`).

### 📝 Autosave Format

Each successful copy appends:

```text
<sequence>\t<source_message_id>\t<https://t.me/c/<internal>/<id>>
```

Last line = last copied message.

### ⏸ Recover After Interruption

1. Open `progress_<channel>.log`.
2. Take the `<source_message_id>` of last or next desired.
3. Set `START_FROM_MESSAGE_ID`.
4. Rerun.

### 🧪 Demo Mode

Set `DEMO_MODE = True` – no messages sent.

### 🛡 Limitations

- Cannot copy reactions / polls / view counts / comment threads.
- Some protected media may still be inaccessible.

### 🧹 Cleanup

Media removed after upload. Orphan leftovers (after crash) can be deleted manually.

### 🚀 Possible Improvements

Parallel uploads (careful with limits), JSON export, web dashboard, Docker.

### 📜 License

Add an MIT (or other) license before public release.

### ❓ FAQ / Вопросы

**Slow on large video?** Normal – chunked download.
**ETA unstable early?** Stabilizes after more messages.
**Resumed at wrong point?** Prefer `START_FROM_MESSAGE_ID`.

---

## Русская версия

### ⚠️ Юридическое и этическое уведомление

Инструмент предназначен только для обучения, миграции собственных данных и личного бэкапа. Ответственность за правомерность копирования несёте вы.

### ✅ Возможности

- Полное копирование (текст + медиа) через повторную загрузку, не пересылку.
- Приватные и публичные каналы (ID, инвайт, @username).
- Фото / документы / видео / аудио / GIF / стикеры.
- Сохранение форматирования (entities, ссылки, выделение).
- Авто‑обработка flood wait.
- Три режима возобновления: ID, текст, позиция.
- Автосохранение ссылок (`progress_<канал>.log`).
- Удаление временных медиа после отправки.
- Статистика, ETA, демо режим.

### 🗂 Структура

См. блок English – идентична.

### ⚙️ Установка

```bash
pip install telethon
```

### 🔐 API

1. <https://my.telegram.org> → создать приложение.
2. Впишите `API_ID`, `API_HASH`, номер телефона в `config.py`.
3. Первый запуск создаст файл сессии.

### 🛠 Конфигурация (фрагмент)

```python
START_FROM_MESSAGE_ID = 1239
RESUME_FROM_TEXT = None
SKIP_TO_POSITION = None
```

Приоритет: ID → Текст → Позиция (1 = самое старое).

### ▶️ Запуск

```bash
python main.py
```

### 🔄 Возобновление

Откройте последнюю строку `progress_*.log`, возьмите ID, установите `START_FROM_MESSAGE_ID`, перезапустите.

### 🧪 Демо режим

`DEMO_MODE = True` – без отправки.

### 🛡 Ограничения

Не переносятся реакции, просмотры, комментарии, опросы.

### 🧹 Очистка

Временные медиа удаляются сразу; остатки можно удалить вручную.

### ❓ FAQ

**Зависает на видео?** Ждите – идёт скачивание.
**ETA странная?** Нормализуется позже.
**Смещение точки старта?** Используйте ID.

### 📋 Перед публикацией

- [ ] Удалите реальные ключи из `config.py`.
- [ ] Добавьте `.gitignore` для `*.session`, `progress_*.log`, `media_*`, `logs/`.
- [ ] Добавьте LICENSE.

---

Happy archiving / Удачного архивирования!
