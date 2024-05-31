import json
from dataclasses import asdict, is_dataclass, fields
from typing import Any
from tree.ast_nodes import *

def dataclass_to_dict(obj: Any) -> Any:
    if is_dataclass(obj):
        result = {}
        result[obj.__class__.__name__] = {}
        for field in fields(obj):
            value = getattr(obj, field.name)
            result[obj.__class__.__name__][field.name] = dataclass_to_dict(value)
        return result
    elif isinstance(obj, list):
        return [dataclass_to_dict(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: dataclass_to_dict(value) for key, value in obj.items()}
    else:
        return obj


def convert_ast_to_json(ast: ASTNode) -> str:
    return json.dumps(dataclass_to_dict(ast), indent=2)

