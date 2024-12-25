from fastapi import HTTPException

class CustomHTTPException(HTTPException):
    def __init__(self, status_code: int, message: str, data=None):
        detail = {
            "isDone": False,
            "data": data,
            "message": message,
        }
        super().__init__(status_code=status_code, detail=detail)