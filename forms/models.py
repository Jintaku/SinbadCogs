import dataclasses
from typing import Optional


@dataclasses.dataclass
class Question:
    """
    Holds info about a question
    """
    prompt: str = ""
    min_response: int = 0
    max_response: int = 2000
    timeout: Optional[int] = None

    def __post_init__(self):
        self.min_response = max(0, self.min_response)
        self.max_response = min(self.max_response, 2000)
        self.timeout = max(self.timeout, 300) if self.timeout is not None else None

@dataclasses.dataclass
class Form:
    pass
