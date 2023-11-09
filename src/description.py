from dataclasses import dataclass
import enum


class Origin(enum.Enum):
    Ai = "Ai"
    Human = "Human"

@dataclass
class Description:
    origin: Origin
    text: str