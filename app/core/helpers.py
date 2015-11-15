import json
from enum import Enum
from datetime import datetime


class ModelEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        elif isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, datetime):
            return obj.timestamp()
        return json.JSONEncoder.default(self, obj)
