class ClientRequestError(Exception):
    def __init__(self, status_code: int, reason: str) -> None:
        self.status_code = status_code
        self.reason = reason


def assert400(condition: bool, reason: str = "bad request") -> None:
    if not condition:
        raise ClientRequestError(400, reason)


def assert401(
    condition: bool, reason: str = "credentials are invalid or expired"
) -> None:
    if not condition:
        raise ClientRequestError(401, reason)


def assert403(
    condition: bool,
    reason: str = "you don't have permission to access this resource",
) -> None:
    if not condition:
        raise ClientRequestError(403, reason)


def assert404(condition: bool, reason: str = "not found") -> None:
    if not condition:
        raise ClientRequestError(404, reason)


def assert409(condition: bool, reason: str = "conflict") -> None:
    if not condition:
        raise ClientRequestError(409, reason)
