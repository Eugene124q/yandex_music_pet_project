#!/bin/bash
set -e

# Переходим в директорию проекта
cd $MY_PROJECT_PATH

# Загрузка переменных окружения из файла .env
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

# Переменные для Telegram
TELEGRAM_TOKEN=$TELEGRAM_TOKEN
CHAT_ID=$CHAT_ID

# Название проекта
SCRIPT_NAME="yandex_mertica"

# Запоминаем время начала
START_TIME=$(date +%s)

# Активируем виртуальное окружение
source venv/bin/activate

# Запускаем скрипт и перенаправляем вывод
if ! ./Yandex_music_data_script.py >output_$SCRIPT_NAME.txt 2>errors_$SCRIPT_NAME.txt; then
    # Запоминаем время завершения
    END_TIME=$(date +%s)
    # Рассчитываем продолжительность выполнения
    EXECUTION_TIME=$((END_TIME - START_TIME))
    
    # Если скрипт завершился с ошибкой, отправляем сообщение в Telegram
    curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_TOKEN/sendMessage" \
        -d chat_id=$CHAT_ID \
        -d text="Ошибка в проекте $SCRIPT_NAME. Время работы: $EXECUTION_TIME сек. Проверьте файл error_$SCRIPT_NAME.txt"
else
    # Запоминаем время завершения
    END_TIME=$(date +%s)
    # Рассчитываем продолжительность выполнения
    EXECUTION_TIME=$((END_TIME - START_TIME))

    # Если скрипт завершился успешно, отправляем сообщение в Telegram
    curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_TOKEN/sendMessage" \
        -d chat_id=$CHAT_ID \
        -d text="Проект $SCRIPT_NAME успешно выполнен. Время работы: $EXECUTION_TIME сек."
fi

# Деактивируем виртуальное окружение
deactivate