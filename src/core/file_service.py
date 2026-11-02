from pathlib import Path

from fastapi import UploadFile

from core.config import Settings
from core.errors import FileTooLargeException, UnsupportedFileTypeException


class FileService:
    def __init__(self, settings: Settings):
        self.settings = settings

    def validate(self, file: UploadFile, max_bytes: int) -> None:
        self._validate_size(file=file, max_bytes=max_bytes)
        self._validate_type(file_name=file.filename)

    def _validate_size(self, file: UploadFile, max_bytes: int) -> None:
        if file.size is not None and file.size > max_bytes:
            raise FileTooLargeException(max_bytes)

    def _validate_type(self, file_name) -> None:
        extension = self.get_file_extension(file_name)
        if extension not in self.settings.allowed_file_extensions:
            raise UnsupportedFileTypeException(extension)

    def get_file_extension(self, file_name) -> str:
        return Path(file_name).suffix.lower()
