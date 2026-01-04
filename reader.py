from typing import Dict, Any, Callable

import json
from functools import partial


def read_json(filepath:str) -> Dict[str, Any]:
    decoder = partial(json.loads)
    return _read(filepath, decoder)

def _read(filepath: str, decoder: Callable[[bytes], Any]) -> Any:
    with open(filepath, 'rb') as f:
        return decoder(f.read())
