from pathlib import Path
from uuid import uuid4

import aiofiles.os
import pytest
from aiosmtplib import SMTPConnectError

from aio_send_dir.v1 import compress_report, delete_file, send_mail


@pytest.fixture
async def htmlcov():
    temp_dir: Path = Path("htmlcov123")
    await aiofiles.os.makedirs(temp_dir, exist_ok=True)
    yield temp_dir
    await aiofiles.os.rmdir(temp_dir)


@pytest.fixture()
async def compressed_report():
    temp_file: Path = Path(f"htmlcov{str(uuid4())[:4]}.zip")
    async with aiofiles.open(temp_file, mode="x") as _:
        pass
    yield temp_file
    try:
        await aiofiles.os.remove(temp_file)
    except FileNotFoundError:
        pass


async def test_compress_report(htmlcov):
    compressed: Path = await compress_report(htmlcov)
    assert compressed.is_file()
    assert compressed.suffix == ".zip"
    await aiofiles.os.remove(compressed)


async def test_compress_report_with_bad_path():
    try:
        await compress_report("bad")
    except AssertionError:
        assert True
    except Exception as err:
        raise AssertionError from err
    else:
        raise AssertionError


async def test_delete_existing_file(compressed_report):
    try:
        await delete_file(compressed_report)
    except Exception as err:
        raise AssertionError from err
    else:
        assert True


async def test_delete_notfound_file():
    try:
        await delete_file("123")
    except Exception as err:
        raise AssertionError from err
    else:
        assert True


async def test_bad_smtp(compressed_report):
    try:
        await send_mail("localhost", 25, "yoba@peka.net", "peka@peka.net", compressed_report)
    except SMTPConnectError:
        assert True
    except Exception as err:
        raise AssertionError from err
    else:
        raise AssertionError
