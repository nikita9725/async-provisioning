# Equipment-Provisioning: сервисы A, B, Worker, Task Status Refresher

Репозиторий содержит реализацию тестового задания — «асинхронный запуск процесса активации оборудования». 
Проект состоит из трёх самостоятельных компонентов.

| Папка                 | Сервис                | Краткое назначение                                          |
|-----------------------|-----------------------|-------------------------------------------------------------|
| service_a             | Service-A             | Синхронный «чёрный ящик» (заглушка прототипа конфигуратора) |
| service_b             | Servie-B              | Управление задачами активации оборудования                  |  
| worker                | Worker                | Выполняет задачи обновления конфигурации, вызывая сервис А  |
| task_status_refresher | Task Status Refresher | Переводит в FAILED зависшие задачи в IN_PROGRESS            |

---

## Быстрый старт

### Установка uv
Инcтрукция по установке менеджера пакетов uv доступна [ссылке](https://docs.astral.sh/uv/getting-started/installation/#installation-methods)

### Установка .env файла
Сначала копируется файл .env.example, затем в случае необходимости подставляются нужные параметры
```bash
cp .env.example .env
```

###  Сервис A
Сервис А запускается командой `uv run main.py service-a`
Опции: 
 - `--port` - указывается порт сервиса (по умолчанию 8000)

###  Сервис B
Сервис А запускается командой `uv run main.py service-b`
Опции: 
 - `--port` - указывается порт сервиса (по умолчанию 8000)

###  Сервис Worker
Сервис А запускается командой `uv run main.py worker`

###  Сервис Task Status Refresher
Сервис А запускается командой `uv run main.py task-status-refresher`

## Запуск через docker-compose
Для запуска в docker-compose нужно воспользоваться командой `docker-compose up -d`

## Запуск линтера и форматтера
Запустить линтер и форматтер ruff можно следующими командами
```bash
uv run ruff check --fix
uv run ruff format
```
