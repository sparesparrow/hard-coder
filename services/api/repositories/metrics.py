from typing import List, Optional, Type, TypeVar, Generic, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, and_
from sqlalchemy.orm import selectinload

from ..models.metrics import (
    Metric,
    ScreenshotMetric,
    NetworkMetric,
    ClipboardMetric
)
from ..database import transaction

T = TypeVar('T', bound=Metric)

class MetricRepository(Generic[T]):
    """Generic repository for handling metric operations."""
    
    def __init__(self, session: AsyncSession, model: Type[T]):
        self._session = session
        self._model = model
    
    async def create(self, metric: T) -> T:
        """Create a new metric."""
        self._session.add(metric)
        await self._session.commit()
        await self._session.refresh(metric)
        return metric
    
    async def get_by_id(self, metric_id: int) -> Optional[T]:
        """Get metric by ID."""
        query = select(self._model).where(self._model.id == metric_id)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[T]:
        """Get all metrics with optional time range filtering."""
        query = select(self._model)
        
        if start_time:
            query = query.where(self._model.timestamp >= start_time)
        if end_time:
            query = query.where(self._model.timestamp <= end_time)
            
        query = query.order_by(self._model.timestamp.desc())
        query = query.limit(limit).offset(offset)
        
        result = await self._session.execute(query)
        return result.scalars().all()
    
    async def delete(self, metric_id: int) -> bool:
        """Delete a metric by ID."""
        query = delete(self._model).where(self._model.id == metric_id)
        result = await self._session.execute(query)
        await self._session.commit()
        return result.rowcount > 0
    
    async def cleanup_old_metrics(self, before_date: datetime) -> int:
        """Delete metrics older than the specified date."""
        query = delete(self._model).where(self._model.timestamp < before_date)
        result = await self._session.execute(query)
        await self._session.commit()
        return result.rowcount

class ScreenshotMetricRepository(MetricRepository[ScreenshotMetric]):
    """Repository for screenshot metrics."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, ScreenshotMetric)
    
    async def get_by_dimensions(
        self,
        min_width: Optional[int] = None,
        min_height: Optional[int] = None,
        limit: int = 100
    ) -> List[ScreenshotMetric]:
        """Get screenshots filtered by dimensions."""
        query = select(self._model)
        
        if min_width:
            query = query.where(self._model.width >= min_width)
        if min_height:
            query = query.where(self._model.height >= min_height)
            
        query = query.order_by(self._model.timestamp.desc()).limit(limit)
        
        result = await self._session.execute(query)
        return result.scalars().all()

class NetworkMetricRepository(MetricRepository[NetworkMetric]):
    """Repository for network metrics."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, NetworkMetric)
    
    async def get_by_bandwidth(
        self,
        min_bandwidth: float,
        limit: int = 100
    ) -> List[NetworkMetric]:
        """Get network metrics filtered by minimum bandwidth."""
        query = select(self._model)\
            .where(self._model.bandwidth_mbps >= min_bandwidth)\
            .order_by(self._model.timestamp.desc())\
            .limit(limit)
            
        result = await self._session.execute(query)
        return result.scalars().all()

class ClipboardMetricRepository(MetricRepository[ClipboardMetric]):
    """Repository for clipboard metrics."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, ClipboardMetric)
    
    async def get_by_content_type(
        self,
        content_type: str,
        limit: int = 100
    ) -> List[ClipboardMetric]:
        """Get clipboard metrics filtered by content type."""
        query = select(self._model)\
            .where(self._model.content_type == content_type)\
            .order_by(self._model.timestamp.desc())\
            .limit(limit)
            
        result = await self._session.execute(query)
        return result.scalars().all()
    
    async def get_filtered_content(
        self,
        limit: int = 100
    ) -> List[ClipboardMetric]:
        """Get clipboard metrics that have been filtered."""
        query = select(self._model)\
            .where(self._model.is_filtered == True)\
            .order_by(self._model.timestamp.desc())\
            .limit(limit)
            
        result = await self._session.execute(query)
        return result.scalars().all()

# Factory function to create repositories
def create_metric_repository(
    session: AsyncSession,
    metric_type: str
) -> MetricRepository:
    """Create appropriate repository based on metric type."""
    repositories = {
        "screenshot": ScreenshotMetricRepository,
        "network": NetworkMetricRepository,
        "clipboard": ClipboardMetricRepository
    }
    
    repo_class = repositories.get(metric_type)
    if not repo_class:
        raise ValueError(f"Unknown metric type: {metric_type}")
        
    return repo_class(session) 