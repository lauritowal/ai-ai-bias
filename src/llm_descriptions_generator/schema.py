import enum
import typing as t

from pydantic.dataclasses import dataclass, Field

class Origin(str, enum.Enum):
    LLM = "LLM"
    Human = "Human"
        
    def __str__(self):
        return self.value

class Engine(str, enum.Enum):
    gpt35turbo = "gpt-3.5-turbo"
    gpt35turbo1106 = "gpt-3.5-turbo-1106"
    # gpt4 = "gpt-4"
    gpt4turbo = "gpt-4-1106-preview"
    # must be served locally via LM studio (see README)
    mistral7binstructv02q4_k_mgguf = "mistral-7b-instruct-v0.2.Q4_K_M.gguf"
    metallama38binstructq4_k_mgguf = "Meta-Llama-3-8B-Instruct-Q4_K_M.gguf"
    # Groq models
    groq_llama3_70b_8192 = "groq-llama3-70b-8192"
    groq_llama3_8b_8192 = "groq-llama3-8b-8192"
    groq_mixtral_8x7b_32768 = "groq-mixtral-8x7b-32768"
    groq_gemma_7b_it = "groq-gemma-7b-it"
    # Together.ai
    together_llama_3_8b_chat = "together-meta-llama/Llama-3-8b-chat-hf"
    together_llama_3_70b_chat = "together-meta-llama/Llama-3-70b-chat-hf"
    together_mixtral_8x7b_instruct = "together-mistralai/Mixtral-8x7B-Instruct-v0.1"
    together_mixtral_8x22b_instruct = "together-mistralai/Mixtral-8x22B-Instruct-v0.1"
    together_qwen15_05b_chat = "together-Qwen/Qwen1.5-0.5B-Chat"
    together_qwen15_4b_chat = "together-Qwen/Qwen1.5-4B-Chat"
    together_gemma_2b_it = "together-google/gemma-2b-it"
    together_phi_2 = "together-microsoft/phi-2"
    together_llama_2_13b_chat = "together-meta-llama/Llama-2-13b-chat-hf"

    def __str__(self):
        return self.value

class PromptDescriptionSource(str, enum.Enum):
    Human = "human"
    AcademicPaperBody = "academic_paper_body"
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
    meta: t.Optional[dict] = None

@dataclass
class LlmGeneratedTextItemDescriptionBatch(TextItemDescriptionBatch):
    item_type: str
    title: str
    descriptions: list[DescriptionTextOrJson]
    origin: Origin
    llm_engine: str
    generation_prompt_uid: str # @deprecated concept. do not use.
    generation_prompt_nickname: str
    generation_prompt_text: str

@dataclass
class TextItemGenerationPromptConfig:
    item_type: str
    prompt_nickname: str
    prompt_base_text: str
    include_descriptions: bool
    description_source: PromptDescriptionSource
    include_title: t.Optional[bool] = True
    output_description_type: t.Optional[t.Any] = None
    match_human_original_length: t.Optional[bool] = None

@dataclass
class TextItemGenerationPrompt:
    item_type: str
    item_title: str
    prompt_text: str
    prompt_uid: str
    prompt_nickname: str
