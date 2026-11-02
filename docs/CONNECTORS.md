# Connector Architecture & Implementation Specification

## 1. Base Connector Interface

Every connector inherits from `BaseConnector`:

```python
from abc import ABC, abstractmethod
from typing import List, Optional
from app.schemas.opportunity import NormalizedOpportunity
from app.schemas.connector import ConnectorResult, HealthCheckResult

class BaseConnector(ABC):
    source_id: str
    source_name: str
    category: str

    @abstractmethod
    async def health_check(self) -> HealthCheckResult:
        """Verify endpoint connectivity and readiness."""
        pass

    @abstractmethod
    async def collect(self, limit: Optional[int] = None) -> ConnectorResult:
        """Fetch raw listings from the source and return normalized records."""
        pass

    @abstractmethod
    def normalize(self, raw_item: dict) -> NormalizedOpportunity:
        """Transform raw source schema into the universal model."""
        pass
```

---

## 2. Supported Collection Protocols

1. **REST APIs with Official Endpoints**:
   - `RemotiveConnector`: Queries `https://remotive.com/api/remote-jobs` with category and search query filters.
   - `RemoteOKConnector`: Queries `https://remoteok.com/api` with proper headers.
   - `HimalayasConnector`: Queries `https://himalayas.app/jobs/api` with country filtering for Egypt/Worldwide.

2. **Public Feeds & Career Boards**:
   - `WeWorkRemotelyConnector`: Parses RSS XML feeds for programming and AI listings.
   - `GreenhouseBoardsConnector`: Parses public Greenhouse boards (e.g., Outlier AI, Alignerr, Scale AI).

3. **Public Web Parsing**:
   - `OneFormaConnector`: Parses verified public job listings on OneForma.
   - `AppenConnector`: Parses CrowdGen public postings.
   - `DataAnnotationConnector`: Inspects public landing and onboarding role opportunities.

4. **Account-Specific Browser Connectors**:
   - `OutlierAccountConnector`: Uses user-authenticated Playwright profile to inspect project allocations.

---

## 3. Resiliency, Rate Limiting & Error Isolation

- **Concurrency Control**: Async gathering with `asyncio.Semaphore(MAX_CONCURRENT_CONNECTORS)`.
- **Per-Connector Timeout**: Configurable timeout (default 30 seconds) prevents slow sources from hanging the search.
- **Circuit Breaker / Health State**: If a connector fails 3 consecutive runs, it is marked as `broken` in the database until manual health check or review.
- **Zero Fabrication**: If a connector fails, an empty list of opportunities is returned with a failure log. Synthetic or fabricated listings are strictly prohibited in production reports.
