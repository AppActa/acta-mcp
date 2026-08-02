class ActaMCPError(Exception):
    """Erro esperado do domínio."""


class AuthenticationError(ActaMCPError):
    pass


class AuthorizationError(ActaMCPError):
    pass


class NotFoundError(ActaMCPError):
    pass


class InvalidInputError(ActaMCPError):
    pass
