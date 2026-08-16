from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


# Import models here to ensure they are registered with Base.metadata
from camp_match.modules.identity.adapters.persistence.models import AccountModel  # noqa
