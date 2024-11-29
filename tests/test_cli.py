import os

import pytest as pytest
from pydantic import ValidationError

from src.constants import DATA_FILE_FOR_TESTS, BookStatus
from src.exceptions import BookDoesNotExists
from src.schemas import BookCreate, BookRead
from src.service import LibraryService


@pytest.fixture(scope="session")
def library_service() -> LibraryService:
    yield LibraryService(DATA_FILE_FOR_TESTS)

    if os.path.exists(DATA_FILE_FOR_TESTS):
        os.remove(DATA_FILE_FOR_TESTS)


@pytest.mark.library_service
@pytest.mark.parametrize(
    "title, author, year",
    [
        ["Тёмные аллеи", "Бунин Иван Алексеевич", 1937],
        ["Реквием", "Ахматова Анна", 1963],
        ["Мертвые души", "Гоголь Николай Васильевич", 1842],
        ["1984", "George Orwell", 1949]
    ]
)
def test_add_book(library_service, title, author, year):
    result = library_service.add_book(BookCreate(title=title, author=author, year=year), need_save=False)

    assert isinstance(result, BookRead)
    assert result.id is not None
    assert result.status == BookStatus.available


@pytest.mark.library_service
@pytest.mark.parametrize(
    "title, author, year",
    [
        ["Очень длинное название----------------------------------------------------", "Бунин Иван Алексеевич", 1937],
        ["Цифры в имени автора", "Бунин Иван Алексеевич123", 1937],
        ["два символа '.' подряд в имени автора", "Бунин Иван Алексеевич..", 1937],
        ["два пробела подряд в имени автора", "Бунин Иван  Алексеевич", 1937],
        ["два символа ',' подряд в имени автора", "Бунин Иван Алексеевич,, Гоголь Николай Васильевич", 1937],
        ["наличие недопустимого символа в имени автора", "Бунин Иван Алексеевич$", 1937],
        ["строка вместо даты", "Бунин Иван Алексеевич$", "какой-то год"],
        ["отрицательная дата", "Бунин Иван Алексеевич$", -1],
    ]
)
def test_add_book_failed(library_service, title, author, year):
    with pytest.raises(ValidationError):
        library_service.add_book(BookCreate(title=title, author=author, year=year))


@pytest.mark.library_service
def test_list_books(library_service):
    books = library_service.list_books()

    assert len(books) == 4
    assert books[0].title == "1984" and books[-1].title == "Тёмные аллеи"


@pytest.mark.library_service
def test_find_book_by_id(library_service):
    book = library_service.add_book(BookCreate(title="Книга для поиска по id", author="Автор", year=1000), need_save=False)
    found_book = library_service.find_book_by_id(book.id)

    assert book == found_book

    not_existing_book = library_service.find_book_by_id("1")

    assert not_existing_book is None


@pytest.mark.library_service
def test_find_book_by_id_not_valid_id_type(library_service):
    with pytest.raises(AttributeError):
        library_service.find_book_by_id(1)


@pytest.mark.library_service
def test_find_books_by_name(library_service):
    name1 = "Природа"
    name2 = "Разнообразная природа России"
    name3 = "Просто книга"
    name4 = "Гербарий"
    author1 = "Первый Автор"
    author2 = "Второй Автор"
    author3 = "Просто автор"

    book1 = library_service.add_book(BookCreate(title=name1, author=author1, year=1000), need_save=False)
    book2 = library_service.add_book(BookCreate(title=name1, author=author2, year=2000), need_save=False)
    book3 = library_service.add_book(BookCreate(title=name2, author=author2, year=2002), need_save=False)
    library_service.add_book(BookCreate(title=name3, author=author3, year=300), need_save=False)

    found_books = library_service.find_books_by_name(name1)

    assert len(found_books) == 3
    assert found_books[0] == book2 and found_books[1] == book1 and found_books[2] == book3

    found_books = library_service.find_books_by_name(name2)

    assert len(found_books) == 1
    assert found_books[0] == book3

    found_books = library_service.find_books_by_name(name4)

    assert len(found_books) == 0


@pytest.mark.library_service
def test_find_books_by_author(library_service):
    name1 = "Азбука"
    name2 = "Букварь"
    name3 = "Энциклопедия"
    author1 = "Пушкин"
    author2 = "Есенин"
    author3 = "Пушкин, Есенин"
    author4 = "Евклид"

    book1 = library_service.add_book(BookCreate(title=name1, author=author1, year=1000), need_save=False)
    book2 = library_service.add_book(BookCreate(title=name1, author=author2, year=2000), need_save=False)
    book3 = library_service.add_book(BookCreate(title=name2, author=author2, year=2002), need_save=False)
    book4 = library_service.add_book(BookCreate(title=name3, author=author3, year=2001), need_save=False)

    found_books = library_service.find_books_by_author(author1)

    assert len(found_books) == 2
    assert found_books[0] == book1 and found_books[1] == book4

    found_books = library_service.find_books_by_author(author2)

    assert len(found_books) == 3
    assert found_books[0] == book2 and found_books[1] == book3 and found_books[2] == book4

    found_books = library_service.find_books_by_author(author4)

    assert len(found_books) == 0


@pytest.mark.library_service
def test_find_books_by_year(library_service):
    name1 = "Азбука"
    name2 = "Букварь"
    name3 = "Энциклопедия"
    author1 = "Онегин"
    year1 = 1111
    year2 = 2222
    year3 = 3333
    year4 = "1111"

    book1 = library_service.add_book(BookCreate(title=name1, author=author1, year=year1), need_save=False)
    book2 = library_service.add_book(BookCreate(title=name2, author=author1, year=year2), need_save=False)
    book3 = library_service.add_book(BookCreate(title=name3, author=author1, year=year1), need_save=False)

    found_books = library_service.find_books_by_year(year1)

    assert len(found_books) == 2
    assert found_books[0] == book1 and found_books[1] == book3

    found_books = library_service.find_books_by_year(year4)

    assert len(found_books) == 2
    assert found_books[0] == book1 and found_books[1] == book3

    found_books = library_service.find_books_by_year(year2)

    assert len(found_books) == 1
    assert found_books[0] == book2

    found_books = library_service.find_books_by_year(year3)

    assert len(found_books) == 0



@pytest.mark.library_service
def test_delete_book(library_service):
    book = library_service.add_book(BookCreate(title="Книга для удаления", author="Автор", year=1000), need_save=False)
    library_service.delete_book(book.id, need_save=False)
    book = library_service.find_book_by_id(book.id)

    assert book is None


@pytest.mark.library_service
def test_delete_book_book_does_not_exist(library_service):
    with pytest.raises(BookDoesNotExists):
        library_service.delete_book("1", need_save=False)


@pytest.mark.library_service
def test_update_status(library_service):
    book = library_service.add_book(
        BookCreate(title="Книга для обновления статуса", author="Автор", year=1000),
        need_save=False
    )

    library_service.update_status(book.id, BookStatus.issued, need_save=False)
    book = library_service.find_book_by_id(book.id)

    assert book.status == BookStatus.issued


@pytest.mark.library_service
def test_update_status_book_does_not_exist(library_service):
    with pytest.raises(BookDoesNotExists):
        library_service.update_status("1", BookStatus.issued, need_save=False)


@pytest.mark.library_service
def test_save_data(library_service):
    library_service.save_data()

    another_library_service = LibraryService(DATA_FILE_FOR_TESTS)
    books = another_library_service.list_books()

    assert len(books) == 14
