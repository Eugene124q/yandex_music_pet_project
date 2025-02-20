# 🎵 Music Insights Dashboard
Этот проект представляет собой инструмент для анализа данных о ваших любимых исполнителях с использованием **API Яндекс.Музыки**, **Python**, **PostgreSQL**, **Docker** и **инструментов BI**.

# 🎯 Цель проекта
Самостоятельно разработать аналитическое end-to-end решение, включая все этапы работы с данными: от идеи, сбора и предварительной обработки данных до их анализа и визуализации. Проект направлен на закрепление навыков использования современных инструментов и технологий для обработки, анализа и интерпретации данных.

# 📚 Функциональность проекта

![Reference Image](/evgenij/pet_project/Images/Снимок%20экрана%20(646).png)
### Сбор данных через API Яндекс.Музыки

- Выгрузка информации о выбранных вами исполнителях, отмеченных как **"Мне нравится"**
- Сбор дополнительных данных: информация о треках, альбомах, стране, дате рождения исполнителя, популярных треках и похожих артистах
- Скрипты для взаимодействия с **API** реализованы на языке **Python**

### Хранилище данных

- Данные хранятся в базе данных **PostgreSQL**, развернутой на сервере **Linux Ubuntu 22.04**

### Аналитический дашборд

- Развернут инструмент **Apache Superset** для построения и визуализации отчетов на основе данных
- Итоговый дашборд помогает анализировать музыкальные предпочтения, популярные треки и связь между исполнителями
- Посмотреть итоговый дашборд можно [здесь]

### Автоматическое обновление данных

- Обновление данных происходит ежедневно в заданное время с помощью планировщика задач (**crontab**)
- Обновления загружаются в базу данных без необходимости вмешательства пользователя

### Система Alert-ов

- Оповещение в **Telegram** о успешном/неуспешном запуске скриптов/dbt-тестов

![Reference Image](/evgenij/pet_project/Images/Снимок%20экрана%20(643).png)

### Использование dbt для моделирования данных

- Дашборд **Superset** основан на моделях, созданных с помощью **dbt**, что обеспечивает чистую, согласованную и воспроизводимую обработку данных
- Для сырых таблиц и моделей настроены **dbt-тесты**, которые проверяют целостность и качество данных

### Документация dbt

![Reference Image](/evgenij/pet_project/Images/Снимок%20экрана%20(645).png)

- Полная документация для dbt-моделей и данных доступна [здесь](https://eugene124q.github.io/pet_project_dbt/)

# 🔄 Этапы работы над проектом

### Начало проекта

- Разработка идеи проекта
- Изучение документации **API Яндекс.Музыки**

### Проектирование и настройка окружения

- Аренда **VPS сервера**
- Развернута база данных **PostgreSQL**
- Создание и настройка **venv**
- Развернуты **Docker-контейнеры** для **Apache Superset**
- Подключение системы контроля версий **Git**
- Инициализация **dbt-проекта**

### Сбор данных

- Реализованы скрипты на **Python** для работы с **API**, позволяющие собирать данные об исполнителях, альбомах, треках и популярных композициях
- Сформирована схема базы данных для удобного хранения и обработки данных

### Анализ и моделирование данных

- Созданы модели данных с использованием **dbt** для подготовки данных к аналитике
- Внедрены **dbt-тесты** для проверки качества данных
- Сформирована модели данных, готовые для построения визуализаций

### Визуализация и отчетность

Разработан итоговый дашборд в **Apache Superset**, который включает:
- Анализ любимых исполнителей и их релизов
- Самые популярные релизы выбранных исполнителей
- История релизов исполнителей
- Популярные треки исполнителей
- Сходства между исполнителями

### Автоматизация обновлений

- Настроен планировщик задач **Cron** для автоматического обновления данных ежедневно

# 🛠 Проблемы и решения

### yandex_music.exceptions.UnauthorizedError: Unauthorized 

При выполнении **Bash-скрипта**, который, в свою очередь, запускает **Python-скрипт** для выгрузки данных через **API Яндекс.Музыки**, иногда возникала ошибка авторизации **(UnauthorizedError)**. Ошибка носила непостоянный характер и могла появляться в разные дни без видимых изменений в коде или учетных данных

Для обработки этой ошибки в **Bash-скрипт** была добавлена логика повторных попыток выполнения с заданным интервалом, при помощи цикла **WHILE**. В случае ошибки происходит повторный запуск **Python-скрипта** до **MAX_RETRIES** раз, а при каждом сбое отправляется уведомление в Telegram. Если после всех попыток скрипт так и не завершился успешно, пользователь получает финальное уведомление о сбое

![Reference Image](/evgenij/pet_project/Images/Снимок%20экрана%20(641).png)

### Проблема сделать отчет **Superset** публичным

### Альбом/релиз стал недоступен в сервисе Яндекс.Музыка
![Reference Image](/evgenij/pet_project/Images/Отсуствие%20страницы.png)
Иногда некоторые альбомы/релизы исполнителей, отмеченных как "Мне нравится" в Яндекс.Музыке, могут становиться недоступными (удалены или скрыты в сервисе). Для этого случая был написаны dbt тесты (в том числе, проверка отсуствия id альбома/релиза в таблице-источнике). В такой ситуации, при очередном автоматическом запуске проекта, возникают ошибки dbt тестов.
![Reference Image](/evgenij/pet_project/Images/dbt%20tests%20error.png)
 Проблема обусловлена особенностями работы Яндекс.Музыки и может возникать спонтанно.

На данный момент, решением этого случая является ручная корректировка данных или обновление списка исполнителей.

При помощи sql-запроса: 
```sql
select album_id
from albums_metrics
where album_id not in (select distinct album_id
					   from albums)
```
я нахожу те id альбомов или релизов, которые отсуствуют в таблице-источнике, затем выполняю запрос с условием:
```sql
delete from <table_name>
where album_id = <missing_id>
```
таким образом я вручную удаляю соответствующие записи из базы данных с помощью DBeaver, выполняя SQL-запрос на удаление строк, соответствующих исчезнувшим альбомам/релизам.




# 📊 Результаты проекта

### Единый источник данных: 
Построена база данных с актуальной информацией о ваших любимых исполнителях
### Аналитика музыкальных предпочтений: 
Разработан наглядный [дашборд] для анализа популярных треков и рекомендаций
### Автоматизация процессов: 
Сбор и обработка данных полностью автоматизированы
### Гибкость и масштабируемость: 
Использование **dbt** и **Superset** позволяет легко модифицировать отчеты
### Прозрачность данных: 
Интуитивно понятные визуализации упрощают восприятие музыкальных трендов
### Контроль качества данных: 
Благодаря **dbt-тестам** данные проходят проверку на целостность и соответствие ожиданиям

# ⚙ Технологии и инструменты

- **Python**: написание скриптов, взаимодействующих с API Яндекс.Музыка.
- **API Яндекс.Музыка**: получение информации об исполнителях и их музыке.
- **PostgreSQL**: хранение полученных данных.
- **Docker**: развёртывание Apache Superset.
- **Apache Superset**: создание визуализации и анализа данных.
- **DBT**: моделирование данных и внедрение тестов.
- **DBEaver**: управление базой данных и выполнения SQL-запросов.
- **CRON**: автоматизация обновления данных.
- **Git** + **GitHub**: контроль версий.