class ServiceException(Exception):
    def __init__(self, status_code: int = 500, message: str = "") -> None:
        self.status_code = status_code
        self.message = message
