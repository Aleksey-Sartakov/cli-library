from enum import Enum


DATA_FILE = "library.json"
DATA_FILE_FOR_TESTS = "test_library.json"
LIBRARY_SERVICE_NAME_IN_CLICK_CONTEXT = "library_service"


class BookStatus(str, Enum):
    available = "в наличии"
    issued = "выдана"
