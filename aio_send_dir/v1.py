import asyncio
import logging
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import aiofiles
from aiofiles.os import scandir
from aiosmtplib import SMTP
from zipstream import AioZipStream

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


async def compress_report(dir_path: Path) -> Path:
    if not isinstance(dir_path, Path):
        dir_path: Path = Path(dir_path)
    assert dir_path.is_dir(), f"Path {dir_path} should be a directory that contains htmlcov report"

    report_name: Path = Path(f"{dir_path}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.zip")
    async with aiofiles.open(report_name, mode="wb") as z:
        async for chunk in AioZipStream(
            ({"file": f, "compression": "deflate"} for f in await scandir(dir_path))
        ).stream():
            await z.write(chunk)

    return report_name


async def send_mail(
    smtp_hostname: str,
    smtp_port: int,
    from_email: str,
    recipients_emails: str,
    report_path: Path,
    use_tls: bool = False,
    validate_certs: bool = False,
    subject: str = "Your coverage report",
    message: str = "Your coverage report is enclosed in the email attachment",
    text_type: str = "plain",
    smtp_user: str | None = None,
    smtp_pass: str | None = None,
) -> None:
    assert smtp_hostname, "Hostname should be set"
    assert smtp_port, "Port should be set"
    assert recipients_emails, "Recipients emails should be set"

    msg = MIMEMultipart()
    msg.add_header("From", from_email)
    msg.add_header("To", recipients_emails)
    msg.add_header("Subject", subject)
    msg.attach(MIMEText(message, text_type, "utf-8"))
    # Attach report
    part = MIMEBase("application", "octet-stream")
    async with aiofiles.open(report_path, "rb") as f:
        part.set_payload(await f.read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f"attachment; filename={report_path.name}")
    msg.attach(part)

    server = SMTP(hostname=smtp_hostname, port=smtp_port, use_tls=use_tls, validate_certs=validate_certs)
    await server.connect()
    if use_tls:
        await server.starttls()
    else:
        await server.ehlo()
    if smtp_user:
        await server.login(smtp_user, smtp_pass)
    await server.send_message(msg)
    await server.quit()


def delete_file(zip_path: Path) -> None:
    try:
        zip_path.unlink()
    except FileNotFoundError:
        pass
    except Exception as err:
        _LOGGER.exception(err)


async def send_dir(
    dir_path: Path,
    smtp_hostname: str,
    smtp_port: int,
    from_email: str,
    recipient_emails: str,
    use_tls: bool = False,
    validate_certs: bool = False,
    subject: str = "Your coverage report",
    message: str = "Your coverage report is enclosed in the email attachment",
    text_type: str = "plain",
    smtp_user: str | None = None,
    smtp_pass: str | None = None,
):
    compressed_report: Path = await compress_report(dir_path)
    _LOGGER.debug(f"{compressed_report=}")
    await send_mail(
        smtp_hostname=smtp_hostname,
        smtp_port=smtp_port,
        from_email=from_email,
        recipients_emails=recipient_emails,
        report_path=compressed_report,
        use_tls=use_tls,
        validate_certs=validate_certs,
        subject=subject,
        message=message,
        text_type=text_type,
        smtp_user=smtp_user,
        smtp_pass=smtp_pass,
    )
    delete_file(compressed_report)


async def main():
    await send_dir(
        dir_path="htmlcov",
        smtp_hostname="localhost",
        smtp_port=1025,
        from_email="yoba@yoba.net",
        recipient_emails="biba@space.ru",
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())
