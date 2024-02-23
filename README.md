# aio_send_dir
[github](https://github.com/devalv/aio_send_dir)

## Для чего

Например, надо отправить coverage отчет после прогона pytest

<!-- TODO: дописать -->

```python
def pytest_sessionfinish(session, exitstatus):
    await send_dir(
        dir_path="htmlcov",
        smtp_hostname="localhost",
        smtp_port=1025,
        from_email="yoba@yoba.net",
        recipients_emails="peka@yoba.net",
    )
```
