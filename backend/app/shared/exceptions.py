from fastapi import HTTPException, status


class AppException(HTTPException):
    error_code = "ERROR"


class NotFoundException(AppException):
    error_code = "NOT_FOUND"

    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class UnauthorizedException(AppException):
    error_code = "UNAUTHORIZED"

    def __init__(self, detail: str = "Not authenticated"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenException(AppException):
    error_code = "FORBIDDEN"

    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class ConflictException(AppException):
    error_code = "CONFLICT"

    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class BadRequestException(AppException):
    error_code = "BAD_REQUEST"

    def __init__(self, detail: str = "Bad request", error_code: str | None = None):
        if error_code:
            self.error_code = error_code
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class ValidationException(AppException):
    error_code = "VALIDATION_ERROR"

    def __init__(self, detail: str = "Validation failed"):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)
