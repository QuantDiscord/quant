class HTTPException(Exception):
    ...


class Forbidden(HTTPException):
    ...


class InternalServerError(HTTPException):
    ...


class RateLimitExceeded(HTTPException):
    ...


class UnexpectedError(HTTPException):
    ...
