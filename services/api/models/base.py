from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, String
from datetime import datetime
from typing import Any, Dict

Base = declarative_base()

class TimestampMixin:
    """Mixin to add created and updated timestamps."""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class AuditMixin:
    """Mixin to add audit fields."""
    created_by = Column(String)
    updated_by = Column(String)

    def update_audit(self, user: str):
        """Update audit fields."""
        if not self.created_by:
            self.created_by = user
        self.updated_by = user

class DictMixin:
    """Mixin to add dictionary conversion."""
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Any:
        """Create model from dictionary."""
        return cls(**{
            k: v for k, v in data.items()
            if k in cls.__table__.columns
        })

# Update Base to include common functionality
class BaseModel(Base, TimestampMixin, AuditMixin, DictMixin):
    """Abstract base model with common functionality."""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)

    def __repr__(self):
        """String representation of the model."""
        return f"<{self.__class__.__name__}(id={self.id})>" 