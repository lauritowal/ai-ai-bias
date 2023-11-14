import enum
from dataclasses import dataclass


class Origin(str, enum.Enum):
    LLM = "LLM"
    Human = "Human"

class Engine(str, enum.Enum):
    gpt35turbo = "gpt-3.5-turbo"
    gpt4 = "gpt-4"

@dataclass
class TextItemDescriptionBatch:
    item_type: str
    title: str
    descriptions: list[str]
    origin: Origin

@dataclass
class HumanTextItemDescriptionBatch(TextItemDescriptionBatch):
    pass

@dataclass
class LlmGeneratedTextItemDescriptionBatch(TextItemDescriptionBatch):
    item_type: str
    title: str
    descriptions: list[str]
    origin: Origin
    llm_engine: str
    generation_prompt_uid: str
    generation_prompt_nickname: str
    generation_prompt_text: str

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
