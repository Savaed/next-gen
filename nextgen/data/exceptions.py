class NotFoundError(Exception):
    """Searched element not found because it doesn't exist or the sequence is empty."""

    pass


class ManyObjectsError(Exception):
    """The result of query or filtering a sequency returned many objects but single was expected."""

    pass


class DbError(Exception):
    """Generic MongoDB error. May be related to a malformed query, connection issues etc."""

    pass
