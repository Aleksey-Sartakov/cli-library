import click
from pydantic import ValidationError

from src.constants import LIBRARY_SERVICE_NAME_IN_CLICK_CONTEXT, DATA_FILE, BookStatus
from src.exceptions import BookDoesNotExists
from src.schemas import BookCreate
from src.service import LibraryService


@click.group()
@click.pass_context
def cli(ctx) -> None:
    """
    The entry point for library management.

    An instance of the "LibraryService" class is initialized.
    This instance is available to all teams within the same session.
    """

    ctx.ensure_object(dict)
    ctx.obj[LIBRARY_SERVICE_NAME_IN_CLICK_CONTEXT]: LibraryService = LibraryService(DATA_FILE)


@cli.command()
@click.argument("title")
@click.argument("author")
@click.argument("year")
@click.pass_context
def add(ctx, title: str, author: str, year: int) -> None:
    """
    Add a new book to the library.

    :param title: the title of the book
    :param author: one or more authors of the book
    :param year: the year of publication of the book
    """

    library_service = ctx.obj[LIBRARY_SERVICE_NAME_IN_CLICK_CONTEXT]

    try:
        new_book = library_service.add_book(BookCreate(title=title, author=author, year=year))

        click.echo(f"The book \"{new_book.title}\" successfully added with id = {new_book.id}")

    except ValidationError as e:
        click.echo(f"Validation error. The arguments passed do not meet the requirements:\n{e}")

    except Exception as e:
        click.echo(f"Unknown error:\n{e}")


@cli.command()
@click.pass_context
def list_books(ctx) -> None:
    """Get a sorted list of all books in the library."""

    library_service: LibraryService = ctx.obj[LIBRARY_SERVICE_NAME_IN_CLICK_CONTEXT]
    books = library_service.list_books()

    if not books:
        click.echo("The library is empty.")
    else:
        for book in books:
            click.echo(f"{book.id} | {book.title} | {book.author} | {book.year} | {book.status}")


@cli.command()
@click.argument("name")
@click.pass_context
def find_by_name(ctx, name: str) -> None:
    """Get a list of books whose title contains the specified substring."""

    library_service: LibraryService = ctx.obj[LIBRARY_SERVICE_NAME_IN_CLICK_CONTEXT]
    books = library_service.find_books_by_name(name)

    if not books:
        click.echo(f"No books with the word '{name}' in their title were found.")
    else:
        for book in books:
            click.echo(f"{book.id} | {book.title} | {book.author} | {book.year} | {book.status}")


@cli.command()
@click.argument("author")
@click.pass_context
def find_by_author(ctx, author: str) -> None:
    """Get a sorted list of books whose author contains the specified substring."""

    library_service: LibraryService = ctx.obj[LIBRARY_SERVICE_NAME_IN_CLICK_CONTEXT]
    books = library_service.find_books_by_author(author)

    if not books:
        click.echo(f"Books by the author '{author}' have not been found.")
    else:
        for book in books:
            click.echo(f"{book.id} | {book.title} | {book.author} | {book.year} | {book.status}")


@cli.command()
@click.argument("year")
@click.pass_context
def find_by_year(ctx, year: int) -> None:
    """Get a sorted list of books whose year matches the specified one."""

    library_service: LibraryService = ctx.obj[LIBRARY_SERVICE_NAME_IN_CLICK_CONTEXT]

    try:
        books = library_service.find_books_by_year(year)

        if not books:
            click.echo(f"No books with the year '{year}' could be found.")
        else:
            for book in books:
                click.echo(f"{book.id} | {book.title} | {book.author} | {book.year} | {book.status}")

    except ValueError:
        click.echo(f"Invalid parameter type. The year must be a number.")


@cli.command()
@click.argument("name")
@click.pass_context
def find_by_id(ctx, book_id: str) -> None:
    """Get information about the book by id."""

    library_service: LibraryService = ctx.obj[LIBRARY_SERVICE_NAME_IN_CLICK_CONTEXT]
    book = library_service.find_book_by_id(book_id)

    if not book:
        click.echo(f"The book with id '{book_id}' could not be found.")
    else:
        click.echo(f"{book.id} | {book.title} | {book.author} | {book.year} | {book.status}")


@cli.command()
@click.argument("book_id")
@click.pass_context
def delete(ctx, book_id: str) -> None:
    """Delete a book by id."""

    library_service: LibraryService = ctx.obj[LIBRARY_SERVICE_NAME_IN_CLICK_CONTEXT]

    try:
        library_service.delete_book(book_id)

        click.echo(f"The book with id \"{book_id}\" has been successfully deleted.")

    except BookDoesNotExists as e:
        click.echo(e)

    except Exception as e:
        click.echo(f"Unknown error:\n{e}")


@cli.command()
@click.argument("book_id")
@click.pass_context
def get(ctx, book_id: str) -> None:
    """
    Take a book from the library.

    Changes the status of the book to "BookStatus.issued"
    """

    library_service: LibraryService = ctx.obj[LIBRARY_SERVICE_NAME_IN_CLICK_CONTEXT]

    try:
        book = library_service.find_book_by_id(book_id)

        if book.status == BookStatus.issued:
            click.echo(f"The book with id \"{book_id}\" is not available now")
        else:
            library_service.update_status(book_id, BookStatus.issued)
            click.echo(f"The book with id \"{book_id}\" has been successfully issued. The status of the book has been"
                       f"changed to \"{BookStatus.issued.value}\".")

    except BookDoesNotExists as e:
        click.echo(e)

    except Exception as e:
        click.echo(f"Unknown error:\n{e}")


@cli.command()
@click.argument("book_id")
@click.pass_context
def return_book(ctx, book_id: str) -> None:
    """
    Return the book to the library.

    Changes the status of the book to "BookStatus.available"
    """

    library_service: LibraryService = ctx.obj[LIBRARY_SERVICE_NAME_IN_CLICK_CONTEXT]

    try:
        library_service.update_status(book_id, BookStatus.available)
        click.echo(f"The book with id \"{book_id}\" has been successfully accepted. The status of the book has been"
                   f"changed to \"{BookStatus.available.value}\".")

    except BookDoesNotExists:
        click.echo(f"The book with id \"{book_id}\" does not belong to this library. If you want to transfer this"
                   "book to this library, use the \"add\" command")

    except Exception as e:
        click.echo(f"Unknown error:\n{e}")


if __name__ == "__main__":
    cli()
