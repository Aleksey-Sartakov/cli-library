class BookDoesNotExists(Exception):
    def __init__(self, book_id: str):
        self.msg = f"The book with the ID \"{book_id}\" does not exist."

    def __str__(self) -> str:
        return self.msg
