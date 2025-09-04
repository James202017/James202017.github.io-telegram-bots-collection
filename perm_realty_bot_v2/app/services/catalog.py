import json, os
from typing import List, Dict, Any

BASE = os.path.dirname(os.path.dirname(__file__))

def load_developers() -> List[Dict[str, Any]]:
    path = os.path.join(BASE, "data", "developers.json")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_sample_properties() -> List[Dict[str, Any]]:
    path = os.path.join(BASE, "data", "sample_properties.json")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
