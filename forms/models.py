import dataclasses
from typing import Optional, List
import discord


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

    def to_config(self):
        return {
            "prompt": self.prompt,
            "min_response": self.min_response,
            "max_response": self.max_response,
            "timeout": self.timeout,
        }

    @classmethod
    def from_config(cls, data: dict):
        return cls(**data)


@dataclasses.dataclass
class Form:
    bot: dataclasses.InitVar[discord.Client]
    output: discord.TextChannel
    questions: List[Question] = dataclasses.field(default_factory=list)
    _bot_ref: discord.Client = dataclasses.field(init=False, repr=False)

    def __post_init__(self, bot):
        self._bot_ref = bot

    async def interactive_for(self, user: discord.User):
        raise NotImplementedError
