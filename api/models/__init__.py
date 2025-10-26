"""Import model modules so SQLAlchemy can discover mapped classes when
relationships use fully-qualified string names like
'api.models.session_messages.SessionMessages'.
"""

# Import model modules to ensure they are registered with SQLAlchemy's
# declarative base when the package is imported.
from . import chat_session  # noqa: F401
from . import session_messages  # noqa: F401

__all__ = ["chat_session", "session_messages"]
