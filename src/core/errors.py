class IngestionException(Exception):
    status_code: int = 500
    code: str = "internal_error"

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class FileTooLargeException(IngestionException):
    status_code = 413
    code = "file_too_large"

    def __init__(self, max_mb: int):
        super().__init__(f"File exceeds the {max_mb} Mb limit")


class UnsupportedFileTypeException(IngestionException):
    status_code = 415
    code = "unsupported_file_type"

    def __init__(self, extension: str):
        super().__init__(f"Unsupported file extension: {extension}")


class VectorStoreUnavailableException(IngestionException):
    status_code = 503
    code = "vector_store_unavailable"

    def __init__(self):
        super().__init__("Vector store is unavailable")


class LlmUnavailableException(IngestionException):
    status_code = 503
    code = "llm_unavailable"

    def __init__(self):
        super().__init__("Llm is unavailable")
