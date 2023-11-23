import enum
import typing as t

from pydantic.dataclasses import dataclass, Field

class Origin(str, enum.Enum):
    LLM = "LLM"
    Human = "Human"

class Engine(str, enum.Enum):
    gpt35turbo = "gpt-3.5-turbo"
    gpt4 = "gpt-4"
    gpt4turbo = "gpt-4-1106-preview"

class PromptDescriptionSource(str, enum.Enum):
    Human = "human"
    LLM_JSON_Summary = "llm_json_summary"


@dataclass
class ProductDetailsJson:
    product_name: str
    product_details: dict = Field(description="Key details of this product described in a valid JSON string")

DescriptionTextOrJson = t.Union[str, dict]

@dataclass
class TextItemDescriptionBatch:
    item_type: str
    title: str
    descriptions: list[DescriptionTextOrJson]
    origin: Origin

@dataclass
class HumanTextItemDescriptionBatch(TextItemDescriptionBatch):
    pass

@dataclass
class LlmGeneratedTextItemDescriptionBatch(TextItemDescriptionBatch):
    item_type: str
    title: str
    descriptions: list[DescriptionTextOrJson]
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
    include_descriptions: bool
    description_source: PromptDescriptionSource
    output_description_type: t.Optional[t.Any] = None

@dataclass
class TextItemGenerationPrompt:
    item_type: str
    item_title: str
    prompt_text: str
    prompt_uid: str
    prompt_nickname: str
