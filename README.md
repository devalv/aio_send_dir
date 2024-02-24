# aio_send_dir
[github](https://github.com/devalv/aio_send_dir)

## Для чего

Например, надо отправить coverage отчет после прогона pytest

```python
def pytest_sessionfinish(session, exitstatus):
    import asyncio

    asyncio.run(send_dir(
        dir_path="htmlcov",
        smtp_hostname="localhost",
        smtp_port=1025,
        from_email="yoba@yoba.net",
        recipient_emails="peka@yoba.net",
        )
    )
```

## Публикация
Для ручной публикации необходимо задать переменные окружения `PYPI_USERNAME` и `PYPI_PASSWORD`
