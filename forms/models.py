import dataclasses
from typing import Optional, List, cast
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
        return dataclasses.asdict(self)

    @classmethod
    def from_config(cls, data: dict):
        return cls(**data)


# pylint: disable=E1101
@dataclasses.dataclass
class Form:
    bot: dataclasses.InitVar[discord.Client]
    output: discord.TextChannel = None
    output_id: dataclasses.InitVar[int] = 0
    questions: List[Question] = dataclasses.field(default_factory=list, init=False)
    _bot_ref: discord.Client = dataclasses.field(init=False, repr=False)

    def __post_init__(self, bot, output_id):
        self._bot_ref = bot
        if output_id:
            self.output = bot.get_channel(output_id)

    async def interactive_for(self, user: discord.User):
        raise NotImplementedError

    def to_config(self):
        return {
            "output_id": self.output.id if self.output else None,
            "questions": [q.to_config() for q in self.questions]
        }

    @classmethod
    def from_config(cls, bot: discord.Client, data: dict):
        questions = data.pop("questions", [])
        x = cls(bot=bot, **data)
        for question in questions:
            x.questions.append(Question.from_config(question))