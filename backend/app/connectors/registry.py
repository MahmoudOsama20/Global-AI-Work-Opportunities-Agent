from typing import Dict, List, Optional, Type
from app.connectors.base import BaseConnector
from app.connectors.job_boards.remotive import RemotiveConnector
from app.connectors.job_boards.remoteok import RemoteOKConnector
from app.connectors.job_boards.himalayas import HimalayasConnector
from app.connectors.job_boards.wwr import WeWorkRemotelyConnector
from app.connectors.outlier.public_outlier import OutlierPublicConnector
from app.connectors.evaluation.alignerr import AlignerrPublicConnector

class ConnectorRegistry:
    """Registry maintaining active connectors."""

    def __init__(self):
        self._connectors: Dict[str, BaseConnector] = {}
        self._register_default_connectors()

    def _register_default_connectors(self):
        default_classes = [
            RemotiveConnector,
            RemoteOKConnector,
            HimalayasConnector,
            WeWorkRemotelyConnector,
            OutlierPublicConnector,
            AlignerrPublicConnector,
        ]
        for cls in default_classes:
            instance = cls()
            self._connectors[instance.source_id] = instance

    def register(self, connector: BaseConnector):
        self._connectors[connector.source_id] = connector

    def get(self, source_id: str) -> Optional[BaseConnector]:
        return self._connectors.get(source_id)

    def get_all(self, enabled_ids: Optional[List[str]] = None) -> List[BaseConnector]:
        if enabled_ids is not None:
            return [c for sid, c in self._connectors.items() if sid in enabled_ids]
        return list(self._connectors.values())


connector_registry = ConnectorRegistry()

