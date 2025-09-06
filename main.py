import asyncio
import os
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, FloodWaitError
from telethon.tl.types import InputPeerChannel, MessageMediaPhoto, MessageMediaDocument, MessageMediaWebPage
from telethon.tl.types import MessageEntityMention, MessageEntityUrl, MessageEntityTextUrl
import time
from config import *
from logger_utils import setup_logging, log_message_info, log_final_stats

# Константы
MAX_RETRIES = 3  # Максимальное количество попыток при ошибках

# Сессия (файл для хранения сессии)
session_name = 'cloner_session'

async def copy_message_with_media(client, message, target, media_folder):
    """
    Копирует сообщение с полным сохранением медиафайлов и форматирования
    """
    max_retries = MAX_RETRIES
    
    for attempt in range(max_retries):
        try:
            text = message.text or ""
            media_file = None
            
            # Пропускаем пустые сообщения без медиа
            if not text and not message.media:
                print(f"\n⚠️ Пропускаем пустое сообщение")
                return False, None
            
            # Обработка различных типов медиа
            if message.media and DOWNLOAD_MEDIA:
                try:
                    if isinstance(message.media, MessageMediaPhoto):
                        # Фотографии - скачиваем и загружаем как новые файлы
                        media_file = await client.download_media(message, file=media_folder)
                        
                    elif isinstance(message.media, MessageMediaDocument):
                        # Документы, видео, аудио, стикеры, гифки - скачиваем и загружаем как новые файлы
                        media_file = await client.download_media(message, file=media_folder)
                            
                    elif isinstance(message.media, MessageMediaWebPage):
                        # Веб-страницы - отправляем только текст с отключенным превью
                        media_file = None
                except Exception as e:
                    print(f"\n⚠️ Ошибка скачивания медиа (попытка {attempt + 1}/{max_retries}): {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2)
                        continue
                    media_file = None
            
            # Обрезаем текст если он слишком длинный для подписи к медиа
            if media_file and len(text) > 1024:
                text = text[:1020] + "..."
                print(f"\n✂️ Текст обрезан до 1024 символов для медиа")
            
            # Подготовка параметров для отправки
            send_params = {
                'entity': target,
                'link_preview': False,
                'parse_mode': None
            }
            
            # Если есть текст, добавляем его
            if text:
                send_params['message'] = text
            elif media_file:
                # Если нет текста но есть медиа, отправляем с пустым сообщением
                send_params['message'] = ""
            else:
                # Если нет ни текста, ни медиа - пропускаем
                print(f"\n⚠️ Пропускаем сообщение без контента")
                return False, None
            
            # Добавляем медиафайл если есть
            if media_file:
                send_params['file'] = media_file
            
            # Сохраняем форматирование если включено
            if PRESERVE_FORMATTING and message.entities:
                send_params['formatting_entities'] = message.entities
            
            # Отправляем сообщение
            sent_message = await client.send_message(**send_params)
            
            # Удаляем медиафайл после отправки, чтобы не занимать место
            if media_file and isinstance(media_file, str) and os.path.exists(media_file):
                try:
                    os.remove(media_file)
                    print(f"\n🗑️ Медиафайл удален: {os.path.basename(media_file)}")
                except Exception as e:
                    print(f"\n⚠️ Не удалось удалить файл {media_file}: {e}")
            
            # Подтверждение отправки
            if sent_message:
                print(f"\n✅ Сообщение #{sent_message.id} успешно отправлено в канал {target.title}")
                return True, media_file
            else:
                print(f"\n❌ Сообщение не было отправлено")
                return False, None
            
        except FloodWaitError as e:
            print(f"\n⏳ Флуд контроль (попытка {attempt + 1}/{max_retries}): ожидание {e.seconds} секунд")
            await asyncio.sleep(e.seconds)
            continue
            
        except Exception as e:
            error_msg = str(e)
            
            # Специальная обработка для защищенных чатов
            if "You can't forward messages from a protected chat" in error_msg:
                print(f"\n🔒 Медиафайл защищен от пересылки, отправляем только текст")
                try:
                    # Удаляем файл если он был скачан
                    if 'media_file' in locals() and media_file and isinstance(media_file, str) and os.path.exists(media_file):
                        os.remove(media_file)
                    
                    # Отправляем только текст без медиа
                    if text:
                        text_params = {
                            'entity': target,
                            'message': text,
                            'link_preview': False,
                            'parse_mode': None
                        }
                        if PRESERVE_FORMATTING and message.entities:
                            text_params['formatting_entities'] = message.entities
                        
                        sent_message = await client.send_message(**text_params)
                        if sent_message:
                            print(f"\n✅ Текстовое сообщение отправлено (медиа пропущено)")
                            return True, None
                except Exception as text_error:
                    print(f"\n⚠️ Ошибка отправки текста: {text_error}")
                
                return False, None
            
            # Специальная обработка для слишком длинных подписей
            elif "The caption is too long" in error_msg:
                print(f"\n✂️ Подпись слишком длинная, отправляем отдельно")
                try:
                    # Удаляем файл если он был скачан
                    if 'media_file' in locals() and media_file and isinstance(media_file, str) and os.path.exists(media_file):
                        os.remove(media_file)
                    
                    # Отправляем текст отдельно
                    if text:
                        text_params = {
                            'entity': target,
                            'message': text,
                            'link_preview': False,
                            'parse_mode': None
                        }
                        if PRESERVE_FORMATTING and message.entities:
                            text_params['formatting_entities'] = message.entities
                        
                        sent_message = await client.send_message(**text_params)
                        if sent_message:
                            print(f"\n✅ Длинный текст отправлен отдельно")
                            return True, None
                except Exception as text_error:
                    print(f"\n⚠️ Ошибка отправки длинного текста: {text_error}")
                
                return False, None
            
            print(f"\n❌ Ошибка копирования сообщения (попытка {attempt + 1}/{max_retries}): {e}")
            # Удаляем файл в случае ошибки
            if 'media_file' in locals() and media_file and isinstance(media_file, str) and os.path.exists(media_file):
                try:
                    os.remove(media_file)
                except:
                    pass
            if attempt < max_retries - 1:
                await asyncio.sleep(3)
                continue
            return False, None
    
    print(f"\n❌ Не удалось скопировать сообщение после {max_retries} попыток")
    return False, None

async def get_channel_info(client, channel_link):
    """
    Получает информацию о канале
    """
    try:
        entity = await client.get_entity(channel_link)
        total_messages = 0
        
        # Подсчитываем общее количество сообщений
        async for _ in client.iter_messages(entity, limit=None):
            total_messages += 1
            
        return entity, total_messages
    except Exception as e:
        print(f"Ошибка получения информации о канале: {e}")
        return None, 0

async def find_message_by_text(client, source_entity, search_text, limit=10000):
    """Ищем сообщение по фрагменту текста в хронологическом порядке.
    Возвращаем (position, message). Position = порядковый номер от 1 (самое старое)."""
    print(f"\n🔍 Ищем сообщение с текстом: '{search_text[:50]}...'")
    # Сначала собираем сообщения (в обратном порядке по умолчанию) в список до лимита
    collected = []
    async for m in client.iter_messages(source_entity, limit=limit):
        collected.append(m)
    # Теперь переворачиваем чтобы идти от старых к новым
    collected.reverse()
    for idx, message in enumerate(collected, start=1):
        if message.text and search_text in message.text:
            print(f"\n✅ Найдено сообщение на позиции {idx} (ID={message.id})")
            print(f"📝 Текст: {message.text[:120]}...")
            return idx, message
        if idx % 100 == 0:
            print(f"🔍 Проверено {idx} сообщений...")
    print(f"\n❌ Сообщение не найдено (просмотрено {len(collected)} сообщений)")
    return None, None

async def main():
    client = TelegramClient(session_name, API_ID, API_HASH)

    try:
        # Подключение
        await client.start(phone=PHONE)
        print("✅ Подключено к Telegram")

        # Получаем информацию об источнике
        print("🔍 Получаем информацию об исходном канале...")
        source, total_messages = await get_channel_info(client, SOURCE_CHANNEL)
        if not source:
            print("❌ Не удалось подключиться к исходному каналу")
            return
            
        print(f"📊 Источник: {source.title}")
        print(f"📈 Всего сообщений в канале: {total_messages}")

        # Настройка логирования
        logger = setup_logging(source.title.replace(' ', '_'))
        logger.info(f"Начало клонирования канала: {source.title}")
        logger.info(f"Всего сообщений для копирования: {total_messages}")

        # Получаем информацию о целевом канале
        if not DEMO_MODE:
            print("🎯 Подключаемся к целевому каналу...")
            target, _ = await get_channel_info(client, TARGET_CHANNEL)
            if not target:
                print("❌ Не удалось подключиться к целевому каналу")
                return
                
            print(f"📝 Целевой канал: {target.title}")
            logger.info(f"Целевой канал: {target.title}")
        else:
            print("🔍 ДЕМО РЕЖИМ: Анализ без отправки сообщений")
            logger.info("ДЕМО РЕЖИМ: Анализ без отправки сообщений")
            target = None

        # Создаем папку для медиафайлов
        # Очищаем имя от недопустимых символов для Windows
        safe_name = source.title.replace(' ', '_').replace(':', '').replace('!', '').replace('?', '').replace('/', '').replace('\\', '')
        media_folder = f"{MEDIA_FOLDER_PREFIX}{safe_name}"
        if not os.path.exists(media_folder):
            os.makedirs(media_folder)
        print(f"📁 Создана папка для медиа: {media_folder}")
        logger.info(f"Папка для медиафайлов: {media_folder}")

        # Файл автосохранения прогресса
        progress_file_path = f"progress_{safe_name}.log"
        print(f"📝 Автосохранение прогресса в: {progress_file_path}")
        logger.info(f"Файл прогресса: {progress_file_path}")

        def build_source_message_link(src_entity_id: int, msg_id: int) -> str:
            """Формирует ссылку вида https://t.me/c/<internal>/<message_id> для приватного канала.
            ID канала в ссылке = channel_id без префикса -100.
            """
            sid = str(src_entity_id)
            if sid.startswith('-100'):
                internal = sid[4:]
            else:
                # fallback для других типов
                internal = sid.lstrip('-')
            return f"https://t.me/c/{internal}/{msg_id}"

        # Определяем позицию для начала
        start_position = None
        # Определяем способ возобновления (приоритет: ID -> TEXT -> POSITION)
        if 'START_FROM_MESSAGE_ID' in globals() and START_FROM_MESSAGE_ID:
            # Нужно вычислить позицию этого ID в хронологическом порядке
            print(f"🔄 Возобновляем с ID сообщения: {START_FROM_MESSAGE_ID}")
            # Собираем все ID (или до лимита) — для больших каналов можно оптимизировать
            ids = []
            async for m in client.iter_messages(source, limit=None):
                ids.append(m.id)
            ids.reverse()  # теперь от старых к новым
            try:
                index = ids.index(START_FROM_MESSAGE_ID)
                start_position = index + 1  # позиция начиная с 1
                print(f"✅ ID найден. Позиция: {start_position}")
            except ValueError:
                print("❌ Указанный ID не найден. Начинаем с начала")
        elif RESUME_FROM_TEXT:
            print(f"🔍 Ищем сообщение для возобновления по тексту...")
            found_position, found_message = await find_message_by_text(client, source, RESUME_FROM_TEXT)
            if found_position:
                start_position = found_position
                print(f"✅ Найдено! Возобновляем с позиции: {start_position} (ID={found_message.id})")
            else:
                print("❌ Сообщение не найдено, начинаем с начала")
        elif SKIP_TO_POSITION:
            start_position = SKIP_TO_POSITION
            print(f"🔄 Возобновляем с позиции: {start_position}")
        
        # Начинаем процесс клонирования
        count = 0
        skipped = 0
        media_downloaded = 0
        start_time = time.time()
        current_position = 0
        
        # Для полного клонирования используем общее количество сообщений
        if DEMO_LIMIT >= total_messages:
            process_limit = total_messages
            print(f"\n🚀 Начинаем ПОЛНОЕ клонирование канала!")
            if start_position:
                print(f"📊 Всего сообщений к обработке: {total_messages - start_position + 1} (с позиции {start_position})")
            else:
                print(f"📊 Всего сообщений к обработке: {total_messages}")
        else:
            process_limit = DEMO_LIMIT
            print(f"\n🚀 Начинаем частичное клонирование {DEMO_LIMIT} сообщений...")

        print("=" * 60)

        async for message in client.iter_messages(source, reverse=True):
            current_position += 1
            
            # Пропускаем сообщения до нужной позиции
            if start_position and current_position < start_position:
                if current_position % 100 == 0:
                    print(f"⏩ Пропускаем до позиции {start_position}: {current_position}/{start_position}")
                continue
            
            try:
                # Ограничение количества сообщений (только если меньше общего количества)
                if DEMO_LIMIT < total_messages and count >= DEMO_LIMIT:
                    break
                    
                # Проверяем содержимое сообщения
                if SKIP_EMPTY_MESSAGES and not message.text and not message.media:
                    skipped += 1
                    continue
                
                # Копируем сообщение
                if DEMO_MODE:
                    # В демо режиме только анализируем
                    success = True
                    media_file = None
                    if message.media:
                        media_file = "demo_media_file"
                        media_downloaded += 1
                else:
                    # Реальное копирование
                    success, media_file = await copy_message_with_media(
                        client, message, target, media_folder
                    )
                
                if success:
                    count += 1
                    if media_file and not DEMO_MODE:
                        media_downloaded += 1
                    
                    # Логируем прогресс
                    log_message_info(logger, message, count, total_messages)

                    # Автосохранение ссылки на исходное сообщение
                    try:
                        source_link = build_source_message_link(source.id, message.id)
                        with open(progress_file_path, 'a', encoding='utf-8') as pf:
                            # Формат: порядковый_номер\tID_сообщения\tСсылка\n
                            pf.write(f"{count}\t{message.id}\t{source_link}\n")
                        # Дополнительно пишем в лог раз в 100 сообщений
                        if count % 100 == 0:
                            logger.info(f"Автосохранено {count} ссылок. Последняя: {source_link}")
                    except Exception as autosave_err:
                        logger.warning(f"Не удалось сохранить прогресс (сообщение {message.id}): {autosave_err}")
                    
                    # Промежуточные отчеты каждые 100 сообщений
                    if count % 100 == 0:
                        elapsed_time = time.time() - start_time
                        logger.info(f"🎯 ПРОМЕЖУТОЧНЫЙ ОТЧЕТ: Обработано {count} сообщений за {elapsed_time:.1f}с")
                        print(f"\n🎯 Обработано {count} сообщений. Продолжаем...")
                    
                    # Прогресс в консоли с расширенной статистикой
                    progress = (count / process_limit) * 100 if process_limit > 0 else 0
                    elapsed_time = time.time() - start_time
                    
                    # Оценка времени завершения
                    if count > 0:
                        avg_time_per_message = elapsed_time / count
                        remaining_messages = process_limit - count
                        eta_seconds = remaining_messages * avg_time_per_message
                        eta_minutes = eta_seconds / 60
                        eta_hours = eta_minutes / 60
                        
                        if eta_hours >= 1:
                            eta_text = f"{eta_hours:.1f}ч"
                        elif eta_minutes >= 1:
                            eta_text = f"{eta_minutes:.1f}м"
                        else:
                            eta_text = f"{eta_seconds:.0f}с"
                    else:
                        eta_text = "∞"
                    
                    mode_text = "КОПИРОВАНИЕ" if not DEMO_MODE else "АНАЛИЗ"
                    print(f"📋 {mode_text}: {count}/{process_limit} ({progress:.1f}%) | "
                          f"Медиа: {media_downloaded} | Время: {elapsed_time:.0f}с | ETA: {eta_text}", end='\r')
                else:
                    skipped += 1
                    logger.warning(f"Пропущено сообщение #{count + skipped}")

                # Пауза между сообщениями (меньше в демо режиме)
                delay = 0.1 if DEMO_MODE else DELAY_BETWEEN_MESSAGES
                await asyncio.sleep(delay)
                
            except FloodWaitError as e:
                print(f"\n⏳ Флуд контроль активен. Ожидание {e.seconds} секунд...")
                logger.warning(f"Флуд контроль: ожидание {e.seconds} секунд")
                await asyncio.sleep(e.seconds)
                continue
                
            except Exception as e:
                print(f"\n❌ Ошибка при обработке сообщения: {e}")
                logger.error(f"Ошибка при обработке сообщения: {e}")
                skipped += 1
                await asyncio.sleep(1)
                continue

        # Итоговая статистика
        total_time = time.time() - start_time
        print(f"\n\n🎉 Клонирование завершено!")
        print("=" * 50)
        print(f"✅ Успешно скопировано сообщений: {count}")
        print(f"📎 Скачано медиафайлов: {media_downloaded}")
        print(f"⚠️  Пропущено сообщений: {skipped}")
        print(f"⏱️  Общее время: {total_time:.1f} секунд")
        print(f"📁 Медиафайлы сохранены в: {media_folder}")

        # Логируем финальную статистику
        log_final_stats(logger, count, skipped, media_downloaded, total_time, media_folder)
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        if 'logger' in locals():
            logger.error(f"Критическая ошибка: {e}")
    finally:
        await client.disconnect()
        print("🔌 Отключено от Telegram")
        if 'logger' in locals():
            logger.info("Отключено от Telegram")


# Запуск
if __name__ == '__main__':
    asyncio.run(main())