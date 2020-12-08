from typing import Dict, Any, Type, TypeVar
from dataclasses import dataclass, fields

@dataclass
class Video:
    aid: int
    bvid: str
    author: str
    duration: str
    pic: str
    pts: int
    title: str


T = TypeVar('T')
def build_data_model(data: Dict[str, Any], klass: Type[T]) -> T:
    field_names = {f.name for f in fields(klass)}
    init_data = {d: v for d, v in data.items() if d in field_names}
    return klass(**init_data)
