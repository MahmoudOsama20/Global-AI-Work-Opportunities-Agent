class AppException(Exception):
    """Base application exception."""
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ConfigurationError(AppException):
    """Raised when application or YAML configuration is invalid."""
    pass


class ConnectorError(AppException):
    """Raised when an external connector fails to fetch or parse data."""
    def __init__(self, source_id: str, message: str, details: dict | None = None):
        super().__init__(f"Connector [{source_id}] error: {message}", details)
        self.source_id = source_id


class ConnectorTimeoutError(ConnectorError):
    """Raised when a connector exceeds its execution timeout."""
    pass


class ValidationError(AppException):
    """Raised when data fails schema or domain validation."""
    pass


class DatabaseError(AppException):
    """Raised for database access or transaction failures."""
    pass


class SourceDiscoveryError(AppException):
    """Raised when source discovery or search fails."""
    pass


class AuthenticationRequiredError(AppException):
    """Raised when private account inspection requires interactive user login."""
    def __init__(self, source_id: str, login_url: str):
        super().__init__(
            f"Authentication required for [{source_id}]. Please log in manually at {login_url}",
            {"source_id": source_id, "login_url": login_url},
        )
        self.source_id = source_id
        self.login_url = login_url

