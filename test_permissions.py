import asyncio
from telethon import TelegramClient
from telethon.tl.types import ChannelParticipantsAdmins
from config import API_ID, API_HASH, PHONE, TARGET_CHANNEL

async def check_channel_permissions():
    """
    Проверяет права доступа к целевому каналу
    """
    client = TelegramClient('test_session', API_ID, API_HASH)
    
    try:
        await client.start(phone=PHONE)
        print("✅ Подключено к Telegram")
        
        # Получаем информацию о целевом канале
        target = await client.get_entity(TARGET_CHANNEL)
        print(f"🎯 Целевой канал: {target.title}")
        print(f"🆔 ID: {target.id}")
        print(f"👥 Участников: {getattr(target, 'participants_count', 'N/A')}")
        
        # Проверяем права администратора
        try:
            me = await client.get_me()
            print(f"👤 Ваш аккаунт: {me.first_name} ({me.username or 'без username'})")
            
            # Получаем информацию об участнике (вас)
            participant = await client.get_permissions(target, me)
            print(f"📝 Ваши права в канале:")
            print(f"   - Администратор: {participant.is_admin}")
            print(f"   - Создатель: {participant.is_creator}")
            print(f"   - Может отправлять сообщения: {participant.post_messages}")
            print(f"   - Может изменять канал: {participant.change_info}")
            
            if not participant.post_messages and not participant.is_admin:
                print("❌ У вас нет прав для отправки сообщений в этот канал!")
                print("💡 Предоставьте себе права администратора или используйте другой канал")
            else:
                print("✅ У вас есть права для отправки сообщений")
                
        except Exception as e:
            print(f"⚠️ Ошибка при проверке прав: {e}")
            
        # Пробуем отправить тестовое сообщение
        try:
            test_message = await client.send_message(target, "🧪 Тестовое сообщение от клонера каналов")
            print("✅ Тестовое сообщение успешно отправлено!")
            
            # Удаляем тестовое сообщение
            await asyncio.sleep(2)
            await client.delete_messages(target, test_message)
            print("🗑️ Тестовое сообщение удалено")
            
        except Exception as e:
            print(f"❌ Ошибка отправки тестового сообщения: {e}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        await client.disconnect()

if __name__ == '__main__':
    asyncio.run(check_channel_permissions())
