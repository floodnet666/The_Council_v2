import json
from datetime import date, datetime
from typing import Any

class TheCouncilJSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder that handles date and datetime objects.
    """
    def default(self, obj: Any) -> Any:
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)

def safe_json_dumps(obj: Any, **kwargs) -> str:
    """
    Safely dumps an object to JSON, handling non-standard types like date.
    """
    if "cls" not in kwargs:
        kwargs["cls"] = TheCouncilJSONEncoder
    if "ensure_ascii" not in kwargs:
        kwargs["ensure_ascii"] = False
    return json.dumps(obj, **kwargs)
