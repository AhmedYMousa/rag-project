class FileTooLargeException(Exception):
    def __init__(self, max_bytes: int):
        self.message = f"File exceeds the {max_bytes} Mb limit"
        self.error_code = 413
        super().__init__(self.message)


class UnsupportedFileTypeException(Exception):
    def __init__(self, extension):
        self.message = f"Unsupported file extension: {extension}"
        self.error_code = 415
        super().__init__(self.message)
