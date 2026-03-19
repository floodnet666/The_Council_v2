import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from utils.logging_config import logger

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat() + "Z"

class ArtifactStore:
    """
    Lightweight persistence layer for computed artifacts (derived columns,
    SQL/ML results, chart payloads) for v2.
    """

    def __init__(self, work_dir: str = "data/artifacts"):
        self.work_dir = work_dir
        self.path = os.path.join(self.work_dir, "session_artifacts.json")
        self.state: Dict[str, Any] = {
            "dataset": {},
            "column_types": {},
            "derived_columns": [],
            "results": [],
            "last_updated": None,
        }
        self._load()

    def _load(self):
        try:
            if os.path.exists(self.path):
                with open(self.path, "r", encoding="utf-8") as f:
                    self.state.update(json.load(f))
        except json.JSONDecodeError as e:
            logger.warning(f"[ArtifactStore] Corrupt JSON detected in {self.path}: {e}")
            backup_path = self.path + ".corrupt"
            try:
                if os.path.exists(self.path):
                     os.rename(self.path, backup_path)
                     logger.info(f"[ArtifactStore] Backed up corrupt file to {backup_path}")
            except Exception as backup_err:
                 logger.error(f"[ArtifactStore] Failed to back up corrupt file: {backup_err}")
        except Exception as e:
            logger.error(f"[ArtifactStore] load error: {e}")

    def _persist(self):
        try:
            os.makedirs(self.work_dir, exist_ok=True)
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"[ArtifactStore] persist error: {e}")

    def record_schema(self, source_path: str, column_types: Dict[str, str], derived_columns: List[str]):
        """
        Persist dataset schema (including derived columns).
        """
        self.state["dataset"] = {
            "source": source_path,
            "file_name": os.path.basename(source_path) if source_path else "",
        }
        self.state["column_types"] = column_types or {}
        self.state["derived_columns"] = derived_columns or []
        self.state["last_updated"] = _now_iso()
        self._persist()

    def record_result(
        self,
        title: str,
        data: Optional[List[Dict[str, Any]]],
        chart: Optional[Dict[str, Any]] = None,
        meta: Optional[Dict[str, Any]] = None,
        limit: int = 150,
    ):
        """
        Store a result set (SQL or simulation/analysis).
        """
        if not data:
            return

        if isinstance(data, dict):
            sample = [data]
            data_len = 1
        else:
            sample = data[:limit]
            data_len = len(data)

        columns = list(sample[0].keys()) if sample and isinstance(sample[0], dict) else []
        result_entry = {
            "id": uuid.uuid4().hex[:8],
            "title": title or "Untitled Result",
            "rows": data_len,
            "columns": columns,
            "sample": sample,
            "chart": chart,
            "meta": meta or {},
            "created_at": _now_iso(),
        }

        # Keep only the most recent 25 artifacts
        self.state["results"] = (self.state.get("results", []) + [result_entry])[-25:]
        self.state["last_updated"] = _now_iso()
        self._persist()

    def snapshot(self) -> Dict[str, Any]:
        """
        Return an in-memory copy.
        """
        return dict(self.state)

# Singleton for the backend
artifact_store = ArtifactStore()
