# Настройка публичного доступа через ngrok

## Вариант 1: ngrok (Рекомендуется)

### Шаг 1: Скачать ngrok

1. Открой https://ngrok.com/download
2. Скачай версию для Windows
3. Распакуй ngrok.exe в любую папку (например, в папку проекта)

### Шаг 2: Зарегистрироваться (бесплатно)

1. Открой https://dashboard.ngrok.com/signup
2. Зарегистрируйся (можно через Google/GitHub)
3. Скопируй свой authtoken со страницы: https://dashboard.ngrok.com/get-started/your-authtoken

### Шаг 3: Настроить authtoken

```bash
# В папке где лежит ngrok.exe
ngrok config add-authtoken ВАШ_ТОКЕН
```

### Шаг 4: Запустить туннель

```bash
# В папке где лежит ngrok.exe
ngrok http 80
```

### Шаг 5: Получить публичный URL

После запуска увидишь что-то вроде:

```
Forwarding   https://abc123.ngrok-free.app -> http://localhost:80
```

**Этот URL можешь отправить преподавателю!** Он будет работать пока ngrok запущен.

---

## Вариант 2: Cloudflare Tunnel (Альтернатива)

### Установка

```bash
# Скачать: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/

# Запустить
cloudflared tunnel --url http://localhost:80
```

---

## Вариант 3: Локальная сеть (Самый простой)

Если преподаватель в той же сети Wi-Fi:

```bash
# Узнать свой IP
ipconfig

# Найти IPv4 адрес (например: 192.168.1.100)
# Преподаватель открывает: http://192.168.1.100
```

---

## Рекомендация

**Используй ngrok** - это самый надёжный способ. Займёт 5 минут на установку.

После установки просто запусти:
```bash
ngrok http 80
```

И получишь публичный URL для демонстрации! 🚀
