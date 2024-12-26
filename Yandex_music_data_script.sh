#!/bin/bash
set -e

# Название проекта
SCRIPT_NAME="yandex_music_data"

# Запоминаем время начала
START_TIME=$(date +%s)

# Переходим в директорию проекта
cd $MY_PROJECT_PATH

# Загрузка переменных окружения из файла .env
if [ -f ".env" ]; then
    export $(grep -v '^#' ".env" | xargs)
fi

# Переменные для Telegram
TELEGRAM_TOKEN=$TELEGRAM_TOKEN
CHAT_ID=$CHAT_ID

# Активируем виртуальное окружение
source venv/bin/activate

# Загрузка данных в базу данных
if ! ./Yandex_music_data_script.py > output_$SCRIPT_NAME.txt 2> errors_$SCRIPT_NAME.txt; then
    # Если загрузка данных завершилась с ошибкой, отправляем сообщение в Telegram
    curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_TOKEN/sendMessage" \
        -d chat_id=$CHAT_ID \
        -d text="Ошибка при загрузке данных в проект $SCRIPT_NAME. Проверьте файл errors_$SCRIPT_NAME.txt"
    deactivate
    exit 1
fi

# Переходим в директорию dbt-проекта
cd $MY_DBT_PROJECT_PATH

# Выполнение тестов dbt
if ! dbt test > dbt_test_output.txt 2> dbt_test_errors.txt; then
    # Если тесты не прошли, отправляем сообщение в Telegram
    curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_TOKEN/sendMessage" \
        -d chat_id=$CHAT_ID \
        -d text="Тесты dbt не прошли для проекта $SCRIPT_NAME. Проверьте файлы dbt_test_output.txt и dbt_test_errors.txt"
    deactivate
    exit 1
fi

# Запоминаем время завершения
END_TIME=$(date +%s)

# Рассчитываем продолжительность выполнения
EXECUTION_TIME=$((END_TIME - START_TIME))

# Отправляем уведомление об успешном выполнении, оставаясь в виртуальном окружении
curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_TOKEN/sendMessage" \
    -d chat_id=$CHAT_ID \
    -d text="Проект $SCRIPT_NAME успешно выполнен. Время работы: $EXECUTION_TIME сек."

# Деактивируем виртуальное окружение
deactivate
