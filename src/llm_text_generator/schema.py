import enum
from dataclasses import dataclass


class Origin(enum.Enum):
    Ai = "Ai"
    Human = "Human"

@dataclass
class HumanTextItemDescriptionBatch:
    item_type: str
    title: str
    descriptions: list[str]
    origin: Origin

@dataclass
class LlmGeneratedTextItemDescriptionBatch:
    item_type: str
    title: str
    descriptions: list[str]
    origin: Origin
    generation_engine: str
    generation_prompt_uid: str
    generation_prompt_nickname: str
    generation_prompt_text: str
    generation_started_at: str
    generation_completed_at: str

@dataclass
class TextItemGenerationPromptConfig:
    item_type: str
    prompt_nickname: str
    prompt_base_text: str
    include_human_descriptions: bool

@dataclass
class TextItemGenerationPrompt:
    item_type: str
    item_title: str
    prompt_text: str
    prompt_uid: str
    prompt_nickname: str
