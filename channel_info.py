import asyncio
from telethon import TelegramClient
from config import API_ID, API_HASH, PHONE

async def list_dialogs():
    """
    Выводит список всех каналов, групп и чатов пользователя
    """
    client = TelegramClient('session_info', API_ID, API_HASH)
    
    try:
        await client.start(phone=PHONE)
        print("✅ Подключено к Telegram")
        print("\n📋 Ваши каналы и группы:")
        print("=" * 60)
        
        async for dialog in client.iter_dialogs():
            if dialog.is_channel or dialog.is_group:
                entity_type = "Канал" if dialog.is_channel else "Группа"
                
                print(f"🔸 {entity_type}: {dialog.name}")
                print(f"   ID: {dialog.entity.id}")
                
                # Безопасная проверка username
                username = getattr(dialog.entity, 'username', None)
                if username:
                    print(f"   Username: @{username}")
                    print(f"   Ссылка: https://t.me/{username}")
                else:
                    print("   Username: Нет")
                
                # Безопасная проверка количества участников
                participants = getattr(dialog.entity, 'participants_count', None)
                if participants:
                    print(f"   Участников: {participants}")
                else:
                    print("   Участников: N/A")
                    
                print("-" * 40)
        
        print("\n💡 Для копирования используйте:")
        print("   - Username: @channel_username")
        print("   - ID: -1001234567890 (для каналов/супергрупп)")
        print("   - Ссылку: https://t.me/channel_username")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        await client.disconnect()

if __name__ == '__main__':
    asyncio.run(list_dialogs())
