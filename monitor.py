import os
import time
from datetime import datetime

def monitor_cloning_progress():
    """
    Мониторинг прогресса клонирования по логам
    """
    log_folder = "logs"
    
    # Находим последний лог файл
    if not os.path.exists(log_folder):
        print("❌ Папка с логами не найдена")
        return
    
    log_files = [f for f in os.listdir(log_folder) if f.startswith('clone_') and f.endswith('.log')]
    if not log_files:
        print("❌ Лог файлы не найдены")
        return
    
    # Берем самый новый лог файл
    latest_log = max(log_files, key=lambda f: os.path.getctime(os.path.join(log_folder, f)))
    log_path = os.path.join(log_folder, latest_log)
    
    print(f"📋 Мониторинг файла: {latest_log}")
    print("=" * 60)
    
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Анализируем лог
        processed_messages = 0
        total_messages = 0
        media_count = 0
        errors = 0
        start_time = None
        
        for line in lines:
            if "Всего сообщений для копирования:" in line:
                total_messages = int(line.split(":")[-1].strip())
            elif "Сообщение #" in line and "/4603" in line:
                # Извлекаем номер обработанного сообщения
                parts = line.split("Сообщение #")[1].split("/")
                processed_messages = int(parts[0])
            elif "Медиа:" in line:
                media_count += 1
            elif "ERROR" in line or "Ошибка" in line:
                errors += 1
            elif "Начало клонирования канала:" in line and not start_time:
                timestamp = line.split(" - ")[0]
                start_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S,%f")
        
        # Выводим статистику
        if total_messages > 0:
            progress = (processed_messages / total_messages) * 100
            print(f"📊 Прогресс: {processed_messages}/{total_messages} ({progress:.1f}%)")
        else:
            print(f"📊 Обработано сообщений: {processed_messages}")
        
        print(f"📎 Медиафайлов: {media_count}")
        print(f"❌ Ошибок: {errors}")
        
        if start_time:
            elapsed = datetime.now() - start_time
            print(f"⏱️ Время работы: {elapsed}")
            
            if processed_messages > 0 and total_messages > 0:
                remaining = total_messages - processed_messages
                avg_time = elapsed.total_seconds() / processed_messages
                eta_seconds = remaining * avg_time
                eta_hours = eta_seconds / 3600
                print(f"🎯 Оценка завершения: {eta_hours:.1f} часов")
        
        print(f"\n🔄 Последние записи:")
        print("-" * 40)
        for line in lines[-5:]:
            if line.strip():
                print(line.strip())
                
    except Exception as e:
        print(f"❌ Ошибка чтения лога: {e}")

if __name__ == '__main__':
    monitor_cloning_progress()
