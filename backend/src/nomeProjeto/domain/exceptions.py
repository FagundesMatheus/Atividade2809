class DomainError(Exception):
    pass


class FileNotFoundDomainError(DomainError):
    pass


class FileExecutionError(DomainError):
    pass


class DatabaseOperationError(DomainError):
    pass


class ItemAlreadyExistsError(DomainError):
    pass
