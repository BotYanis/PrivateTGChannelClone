import logging
import os
from datetime import datetime

def setup_logging(channel_name):
    """
    Настройка логирования для отслеживания процесса клонирования
    """
    # Создаем папку для логов
    logs_folder = "logs"
    if not os.path.exists(logs_folder):
        os.makedirs(logs_folder)
    
    # Имя файла лога с временной меткой
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"{logs_folder}/clone_{channel_name}_{timestamp}.log"
    
    # Настройка логгера
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()  # Также выводить в консоль
        ]
    )
    
    return logging.getLogger(__name__)

def log_message_info(logger, message, count, total):
    """
    Логирование информации о сообщении
    """
    progress = (count / total) * 100 if total > 0 else 0
    
    message_info = f"Сообщение #{count}/{total} ({progress:.1f}%)"
    
    if message.text:
        text_preview = message.text[:50] + "..." if len(message.text) > 50 else message.text
        message_info += f" - Текст: {text_preview}"
    
    if message.media:
        media_type = type(message.media).__name__
        message_info += f" - Медиа: {media_type}"
    
    logger.info(message_info)

def log_final_stats(logger, count, skipped, media_downloaded, total_time, media_folder):
    """
    Логирование финальной статистики
    """
    logger.info("=" * 50)
    logger.info("КЛОНИРОВАНИЕ ЗАВЕРШЕНО")
    logger.info("=" * 50)
    logger.info(f"Успешно скопировано сообщений: {count}")
    logger.info(f"Скачано медиафайлов: {media_downloaded}")
    logger.info(f"Пропущено сообщений: {skipped}")
    logger.info(f"Общее время: {total_time:.1f} секунд")
    logger.info(f"Медиафайлы сохранены в: {media_folder}")
    logger.info("=" * 50)
