import json
import os
import uuid

from pydantic import BaseModel

from src.constants import BookStatus
from src.exceptions import BookDoesNotExists
from src.schemas import BookCreate, BookRead


class BookSchemaEncoder(json.JSONEncoder):
    """Custom class for converting pydantic models for a book to json"""

    def default(self, obj):
        if isinstance(obj, BaseModel):
            return obj.model_dump(exclude_none=True)
        return json.JSONEncoder.default(self, obj)


class LibraryService:
    def __init__(self, file_name: str):
        """
        Download data from a file and save it to "self.books"

        ## Attributes ##
        :self.file_name: the relative or absolute path to the file
        :self.books: the list of books in the library received from the file.
        When loading, each book is converted to the pydantic "BookRead" class
        """

        self.file_name: str = file_name
        self.books: list[BookRead] = self._load_data(file_name)

    @staticmethod
    def _load_data(file_name: str) -> list[BookRead]:
        """
        Download data about books from a file.

        Converts data about each book into an instance of the "BookRead" class.
        If the file does not exist at the specified path, or it is empty, it
        returns an empty list.
        """

        if os.path.exists(file_name):
            with open(file_name, "r", encoding='utf-8') as file:
                return [BookRead.model_validate(book) for book in json.load(file)]

        return []

    def save_data(self) -> None:
        """
        Save the current list of "self.books" to a file.

        Completely overwrites the file.
        """

        with open(self.file_name, "w", encoding='utf-8') as file:
            json.dump(self.books, file, ensure_ascii=False, indent=4, cls=BookSchemaEncoder)

    def add_book(self, data: BookCreate, need_save: bool = True) -> BookRead:
        """Add a new book to the list."""

        new_book = {
            "id": str(uuid.uuid4()),
            "title": data.title,
            "author": data.author,
            "year": data.year,
            "status": BookStatus.available.value
        }
        validated_book = BookRead.model_validate(new_book)
        self.books.append(validated_book)

        if need_save:
            self.save_data()

        return validated_book

    def list_books(self) -> list[BookRead]:
        """Get a sorted list of all books"""

        return sorted(self.books, key=lambda x: (x.title, x.author, x.id))

    def find_books_by_name(self, name: str) -> list[BookRead]:
        """Get a sorted list of books whose name contains the specified substring."""

        books = [book for book in self.books if name.lower() in book.title.lower()]
        books.sort(key=lambda x: (x.title, x.author, x.year, x.id))

        return books

    def find_books_by_author(self, author: str) -> list[BookRead]:
        """Get a sorted list of books whose author contains the specified substring."""

        books = [book for book in self.books if author.lower() in book.author.lower()]
        books.sort(key=lambda x: (x.author, x.title, x.year, x.id))

        return books

    def find_books_by_year(self, year: int) -> list[BookRead]:
        """Get a sorted list of books whose year matches the specified one."""

        books = [book for book in self.books if int(year) == book.year]
        books.sort(key=lambda x: (x.year, x.author, x.title, x.id))

        return books

    def find_book_by_id(self, book_id: str) -> BookRead | None:
        """Get a book by id."""

        for book in self.books:
            if book_id.lower() == book.id.lower():
                return book

        return None

    def delete_book(self, book_id: str, need_save: bool = True) -> None:
        """
        Delete a book by id.

        If a book with the specified id does not exist, the error
        "BookDoesNotExists" will be raised.
        """

        book = self.find_book_by_id(book_id)
        if not book:
            raise BookDoesNotExists(book_id)

        self.books.remove(book)

        if need_save:
            self.save_data()

    def update_status(self, book_id: str, status: BookStatus, need_save: bool = True) -> None:
        """
        Update a book status by id.

        If a book with the specified id does not exist, the error
        "BookDoesNotExists" will be raised.
        """

        for book in self.books:
            if book.id == book_id:
                book.status = status.value

                if need_save:
                    self.save_data()

                return

        raise BookDoesNotExists(book_id)
