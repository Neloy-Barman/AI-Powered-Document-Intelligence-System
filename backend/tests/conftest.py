# Fixture scopes, shortest to longest:
# function - new value for each test function (default)
# class    - one value per test class
# module   - one value per test module
# package  - one value per test package
# session  - one value for the whole test run
#
# Use the narrowest scope that works:
# - session for read-only values shared by all tests, like file paths
# - function when the fixture uses tmp_path or must reset between tests
# A fixture cannot depend on another fixture with a narrower scope.

from pathlib import Path

import pytest

TEST_ROOT = Path(__file__).resolve().parent


# PDF parser fixtures
VALID_PDF_PATH = TEST_ROOT / "fixtures" / "valid.pdf"
CORRUPTED_PDF_PATH = TEST_ROOT / "fixtures" / "corrupted.pdf"
NO_CONTENT_PDF_PATH = TEST_ROOT / "fixtures" / "no_content.pdf"


# CSV parser fixtures
VALID_CSV_PATH = TEST_ROOT / "fixtures" / "valid.csv"
CORRUPTED_CSV_PATH = TEST_ROOT / "fixtures" / "corrupted.csv"


# Spreadsheet parser fixtures
VALID_SPREADSHEET_PATH = TEST_ROOT / "fixtures" / "valid.xlsx"
CORRUPTED_SPREADSHEET_PATH = TEST_ROOT / "fixtures" / "corrupted.xlsx"


# Image parser fixtures
VALID_IMAGE_PATH = TEST_ROOT / "fixtures" / "valid.png"
NO_CONTENT_IMAGE_PATH = TEST_ROOT / "fixtures" / "no_content.jpg"
CORRUPTED_IMAGE_PATH = TEST_ROOT / "fixtures" / "corrupted.tiff"


# PDF parser fixtures
@pytest.fixture(scope="session")
def valid_pdf_path() -> Path:
    return VALID_PDF_PATH


@pytest.fixture
def missing_pdf_path(tmp_path: Path) -> Path:
    return tmp_path / "missing.pdf"


@pytest.fixture(scope="session")
def corrupted_pdf_path() -> Path:
    return CORRUPTED_PDF_PATH


@pytest.fixture(scope="session")
def no_content_pdf_path() -> Path:
    return NO_CONTENT_PDF_PATH


# CSV parser fixtures
@pytest.fixture(scope="session")
def valid_csv_path() -> Path:
    return VALID_CSV_PATH


@pytest.fixture
def missing_csv_path(tmp_path: Path) -> Path:
    return tmp_path / "missing.csv"


@pytest.fixture(scope="session")
def corrupted_csv_path() -> Path:
    return CORRUPTED_CSV_PATH


# Spreadsheet parser fixtures
@pytest.fixture(scope="session")
def valid_spreadsheet_path() -> Path:
    return VALID_SPREADSHEET_PATH


@pytest.fixture
def missing_spreadsheet_path(tmp_path: Path) -> Path:
    return tmp_path / "missing.xlsx"


@pytest.fixture(scope="session")
def corrupted_spreadsheet_path() -> Path:
    return CORRUPTED_SPREADSHEET_PATH


# Image parser fixtures
@pytest.fixture(scope="session")
def valid_image_path() -> Path:
    return VALID_IMAGE_PATH


@pytest.fixture
def missing_image_path(tmp_path: Path) -> Path:
    return tmp_path / "missing.png"


@pytest.fixture(scope="session")
def no_content_image_path() -> Path:
    return NO_CONTENT_IMAGE_PATH


from PIL import Image


@pytest.fixture
def no_content_image_path() -> Path:
    # path = tmp_path / "blank.png"
    Image.new("RGB", (800, 600), color="white").save(NO_CONTENT_IMAGE_PATH)
    return NO_CONTENT_IMAGE_PATH


@pytest.fixture(scope="session")
def corrupted_image_path() -> Path:
    return CORRUPTED_IMAGE_PATH
