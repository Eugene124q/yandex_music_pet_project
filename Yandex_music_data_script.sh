#!/bin/bash
#set -e

# Название проекта
SCRIPT_NAME="yandex_music_data"

# Максимальное количество попыток
MAX_RETRIES=3
RETRY_INTERVAL=3600 # Интервал между попытками (в секундах)

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

# Функция для отправки сообщений в Telegram
send_telegram_message() {
    local message="$1"
    curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_TOKEN/sendMessage" \
        -d chat_id=$CHAT_ID \
        -d text="$message"
}

# Переменные для повторного запуска
attempt=0
success=false

# Основной цикл выполнения с попытками
while [[ $attempt -lt $MAX_RETRIES ]]; do
    ((attempt++))
    echo "Попытка $attempt из $MAX_RETRIES..."

    # Активируем виртуальное окружение
    source venv/bin/activate

    # Загрузка данных в базу данных
    if ./Yandex_music_data_script.py > output_$SCRIPT_NAME.txt 2> errors_$SCRIPT_NAME.txt; then
        success=true
        echo "Скрипт Yandex_music_data_script.py выполнен успешно."
        break
    else
        echo "Ошибка при загрузке данных на попытке $attempt. Ждём $RETRY_INTERVAL секунд."
        send_telegram_message "Ошибка при загрузке данных в проект $SCRIPT_NAME (попытка $attempt). Проверьте файл errors_$SCRIPT_NAME.txt."
    fi

    deactivate
    sleep $RETRY_INTERVAL
done

# Если скрипт не был выполнен успешно после всех попыток
if [[ $success == false ]]; then
    send_telegram_message "Скрипт $SCRIPT_NAME не завершён успешно после $MAX_RETRIES попыток."
    exit 1
fi

# Переходим в директорию dbt-проекта
cd $MY_DBT_PROJECT_PATH

# Выполнение тестов dbt
if ! dbt test > dbt_test_output.txt 2> dbt_test_errors.txt; then
    send_telegram_message "Тесты dbt не прошли для проекта $SCRIPT_NAME. Проверьте файлы dbt_test_output.txt и dbt_test_errors.txt"
    deactivate
    exit 1
fi

# Запоминаем время завершения
END_TIME=$(date +%s)

# Рассчитываем продолжительность выполнения
EXECUTION_TIME=$((END_TIME - START_TIME))

# Отправляем уведомление об успешном выполнении
send_telegram_message "Проект $SCRIPT_NAME успешно выполнен. Время работы: $EXECUTION_TIME сек."

# Деактивируем виртуальное окружение
deactivate
