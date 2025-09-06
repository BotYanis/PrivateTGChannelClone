import asyncio
from telethon import TelegramClient
from config import API_ID, API_HASH, PHONE, TARGET_CHANNEL

async def check_recent_messages():
    """
    Проверяет последние сообщения в целевом канале
    """
    client = TelegramClient('cloner_session', API_ID, API_HASH)  # Используем ту же сессию
    
    try:
        await client.start(phone=PHONE)
        print("✅ Подключено к Telegram")
        
        target = await client.get_entity(TARGET_CHANNEL)
        print(f"🎯 Проверяем канал: {target.title}")
        print(f"🆔 ID: {target.id}")
        
        print("\n📋 Последние 10 сообщений в канале:")
        print("=" * 50)
        
        count = 0
        async for message in client.iter_messages(target, limit=10):
            count += 1
            if message.text:
                text_preview = message.text[:100] + "..." if len(message.text) > 100 else message.text
                print(f"{count}. ID:{message.id} | {text_preview}")
            else:
                print(f"{count}. ID:{message.id} | [Медиа без текста]")
        
        if count == 0:
            print("❌ В канале нет сообщений!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        await client.disconnect()

if __name__ == '__main__':
    asyncio.run(check_recent_messages())
