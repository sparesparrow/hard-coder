import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import asyncio
from collections import defaultdict
import statistics
from ..interfaces.service_interfaces import MetricsCollectorInterface

logger = logging.getLogger(__name__)

class MetricsCollector(MetricsCollectorInterface):
    """Metrics collector implementation with in-memory storage and periodic aggregation."""
    
    def __init__(self):
        self._latency_metrics: Dict[str, List[float]] = defaultdict(list)
        self._error_metrics: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self._aggregation_task: Optional[asyncio.Task] = None
        self._retention_period = timedelta(hours=24)
        self._aggregation_interval = 300  # 5 minutes
        self._max_metrics_per_operation = 10000
        logger.info("Initializing metrics collector")

    async def initialize(self) -> None:
        """Initialize the metrics collector."""
        try:
            self._aggregation_task = asyncio.create_task(self._aggregate_metrics())
            logger.info("Metrics collector initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize metrics collector: {str(e)}")
            raise

    async def cleanup(self) -> None:
        """Clean up resources."""
        try:
            if self._aggregation_task:
                self._aggregation_task.cancel()
                try:
                    await self._aggregation_task
                except asyncio.CancelledError:
                    pass
                self._aggregation_task = None

            self._latency_metrics.clear()
            self._error_metrics.clear()
            logger.info("Metrics collector cleaned up")
        except Exception as e:
            logger.error(f"Error during metrics collector cleanup: {str(e)}")
            raise

    async def record_latency(self,
        operation: str,
        duration_ms: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record operation latency."""
        try:
            metrics = self._latency_metrics[operation]
            metrics.append(duration_ms)
            
            # Trim if exceeding max size
            if len(metrics) > self._max_metrics_per_operation:
                metrics.pop(0)
                
            logger.debug(f"Recorded latency for {operation}: {duration_ms}ms")
        except Exception as e:
            logger.error(f"Failed to record latency for {operation}: {str(e)}")
            raise

    async def record_error(self,
        operation: str,
        error: Exception,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record operation error."""
        try:
            error_data = {
                "timestamp": datetime.utcnow(),
                "error_type": type(error).__name__,
                "error_message": str(error),
                "metadata": metadata or {}
            }
            
            errors = self._error_metrics[operation]
            errors.append(error_data)
            
            # Trim if exceeding max size
            if len(errors) > self._max_metrics_per_operation:
                errors.pop(0)
                
            logger.debug(f"Recorded error for {operation}: {error_data['error_type']}")
        except Exception as e:
            logger.error(f"Failed to record error for {operation}: {str(e)}")
            raise

    async def get_metrics(self,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Get metrics for time period."""
        try:
            metrics = {
                "latency": await self._get_latency_metrics(start_time, end_time),
                "errors": await self._get_error_metrics(start_time, end_time),
                "period": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat()
                }
            }
            return metrics
        except Exception as e:
            logger.error(f"Failed to get metrics: {str(e)}")
            raise

    async def _get_latency_metrics(self,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Calculate latency metrics for the period."""
        latency_metrics = {}
        
        for operation, durations in self._latency_metrics.items():
            if not durations:
                continue
                
            try:
                latency_metrics[operation] = {
                    "count": len(durations),
                    "min": min(durations),
                    "max": max(durations),
                    "mean": statistics.mean(durations),
                    "median": statistics.median(durations),
                    "p95": self._percentile(durations, 95),
                    "p99": self._percentile(durations, 99)
                }
            except Exception as e:
                logger.error(f"Error calculating latency metrics for {operation}: {str(e)}")
                continue
                
        return latency_metrics

    async def _get_error_metrics(self,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Calculate error metrics for the period."""
        error_metrics = {}
        
        for operation, errors in self._error_metrics.items():
            if not errors:
                continue
                
            try:
                # Filter errors within time period
                period_errors = [
                    error for error in errors
                    if start_time <= error["timestamp"] <= end_time
                ]
                
                if not period_errors:
                    continue
                    
                # Group errors by type
                error_types = defaultdict(int)
                for error in period_errors:
                    error_types[error["error_type"]] += 1
                    
                error_metrics[operation] = {
                    "total_count": len(period_errors),
                    "error_types": dict(error_types),
                    "latest_errors": sorted(
                        period_errors,
                        key=lambda x: x["timestamp"],
                        reverse=True
                    )[:5]  # Keep last 5 errors
                }
            except Exception as e:
                logger.error(f"Error calculating error metrics for {operation}: {str(e)}")
                continue
                
        return error_metrics

    async def _aggregate_metrics(self) -> None:
        """Periodically aggregate and clean up old metrics."""
        while True:
            try:
                await asyncio.sleep(self._aggregation_interval)
                
                cutoff_time = datetime.utcnow() - self._retention_period
                
                # Clean up old error metrics
                for operation, errors in self._error_metrics.items():
                    self._error_metrics[operation] = [
                        error for error in errors
                        if error["timestamp"] > cutoff_time
                    ]
                    
                # Could add additional aggregation logic here
                # For example, rolling up metrics into time-based buckets
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metrics aggregation: {str(e)}")

    def _percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile value."""
        if not values:
            return 0.0
            
        sorted_values = sorted(values)
        index = (len(sorted_values) - 1) * percentile / 100
        
        if index.is_integer():
            return sorted_values[int(index)]
            
        lower_index = int(index)
        fraction = index - lower_index
        
        lower_value = sorted_values[lower_index]
        upper_value = sorted_values[lower_index + 1]
        
        return lower_value + (upper_value - lower_value) * fraction 