from dataclasses import dataclass
import enum


class Origin(str, enum.Enum):
    LLM = "LLM"
    Human = "Human"

@dataclass
class Description:
    origin: Origin
    text: str