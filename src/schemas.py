from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_core import ValidationError

from src.constants import BookStatus


class BaseBookSchema(BaseModel):
    title: str = Field(max_length=50)
    author: str
    year: int = Field(ge=0)

    model_config = ConfigDict(from_attributes=True)

    @field_validator("author")
    @classmethod
    def validate_author(cls, value: str):
        if not all(c.isalpha() or c.isspace() or c in ".,-" for c in value):
            raise ValueError("author must contain only letters, spaces, commas, periods, or dashes")

        if "  " in value or ".." in value or ",," in value:
            raise ValueError("author must not contain consecutive spaces, periods, or commas")

        return value


class BookCreate(BaseBookSchema):
    pass


class BookRead(BaseBookSchema):
    id: str
    status: BookStatus


class BookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    year: int | None = None
    status: BookStatus = None
