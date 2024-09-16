# avito-sep24-solution

Решение тестового задания на стажировку в Авито (бэкенд), сентябрь 2024 г.

## Запуск

### Напрямую

1. Установить poetry
2. `poetry install`
3. `POSTGRES_URL=... python3 -m uvicorn avito_sep24:app --host=0.0.0.0 --port=8080`

### Docker

Предполагается, что Docker уже установлен.

```bash
docker build . -t avito_sep_24
docker run -P 8080:8080 -e POSTGRES_URL=... avito_sep_24
```

В обоих случаях нужно заменить `...` на ссылку с подключением к базе данных
