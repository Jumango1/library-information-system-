# Инструкция по загрузке проекта на GitHub

## Шаг 1: Создать репозиторий на GitHub

1. Открой https://github.com/new
2. Заполни форму:
   - **Repository name**: `library-information-system`
   - **Description**: `Библиотечная информационная система для магистерского экзамена (Вариант 6)`
   - **Visibility**: Public (или Private, если хочешь)
   - **НЕ СТАВЬ галочки**: "Add a README file", "Add .gitignore", "Choose a license"
3. Нажми **Create repository**

## Шаг 2: Подключить и запушить

После создания репозитория GitHub покажет команды. Выполни их в этой папке:

```bash
# Переименовать ветку master в main (если нужно)
git branch -M main

# Добавить remote
git remote add origin https://github.com/ТвойUsername/library-information-system.git

# Запушить код
git push -u origin main
```

## Альтернатива: Если у тебя SSH ключ настроен

```bash
git branch -M main
git remote add origin git@github.com:ТвойUsername/library-information-system.git
git push -u origin main
```

## Шаг 3: Проверить

Открой репозиторий на GitHub - там должны быть все файлы и 3 коммита.

---

**Готово!** После этого можешь поделиться ссылкой на репозиторий с преподавателем.
