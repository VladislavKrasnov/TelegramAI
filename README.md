# Telegram Bot для общения на базе ИИ

🤖 Этот бот позволяет вести увлекательные и интерактивные беседы, используя модели искусственного интеллекта. Пользователи могут выбирать между различными моделями, сбрасывать контекст и получать административную статистику (для администраторов). Бот создан с использованием Python и Telegram Bot API.

---

## 📋 Функционал

- **Ответы на базе ИИ**: Бот предоставляет интеллектуальные и интерактивные ответы на сообщения пользователей.
- **Выбор модели**: Пользователи могут переключаться между заданными моделями ИИ (например, GPT v1 и GPT v2).
- **Сброс контекста**: Очистите контекст чата для начала нового разговора.
- **Административная панель**: Администраторы могут просматривать статистику пользователей и другие метрики.
- **Логирование ошибок**: Полное логирование для отслеживания ошибок и отладки.

---

## 📦 Требования

- Python 3.8+
- Зависимости:
  - `telebot`
  - `sqlite3`
  - `mistralai`

Для установки зависимостей выполните команду:

```bash
pip install -r requirements.txt
```

---

## 🔧 Настройка

### 1. **Создание бота в Telegram**:
   - Создайте бота через [BotFather](https://t.me/BotFather) в Telegram и получите токен бота.

### 2. **Конфигурация**:
   - В файле `data/config.py` укажите следующие переменные:
     - `BOT_TOKEN`: Токен, полученный от BotFather.
     - `ADMIN_ID`: Telegram ID администратора.
     - `API_KEY`: API-ключ для библиотеки `mistralai`.

---

## 🛠️ Запуск бота

Запустите бота:
   ```bash
   python main.py
   ```

Бот начнёт опрашивать сообщения и будет готов к взаимодействию с пользователями.

---

## ⚙️ Команды бота

### Команды для пользователей:

- `/start` — Запустить или перезапустить бота.
- `/help` — Посмотреть справку и доступные команды.
- `/mode` — Выбрать модель ИИ для ответов.
- `/reset` — Очистить контекст беседы.

### Команды для администраторов:

- `/admin` — Доступ к административной панели (только для администраторов).
- Кнопка `Статистика` — Просмотр общего числа пользователей.

---

## 🔒 Безопасность

- **Доступ только для администраторов**: Некоторые функции, такие как статистика, доступны только администратору.
- **Ограничение запросов**: Предотвращает спам запросами, устанавливая время ожидания между сообщениями.
- **Обработка ошибок**: Все исключения записываются в файл для обеспечения стабильности и упрощения отладки.

---

## 🛡️ Логирование ошибок

Все ошибки записываются в файл, указанный в `LOG_FILE_PATH`, для удобного мониторинга и отладки. Формат журнала включает метки времени для лучшей отслеживаемости.

---

🚀 Приятного использования!