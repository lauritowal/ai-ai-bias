import os
import typing as t

import interlab


class GroqModel(interlab.lang_models.LangModelBase):
    def __init__(self, model_name: str):
        self.model_name = model_name
        import groq
        self.client = groq.Groq(api_key=os.environ.get("GROQ_API_KEY"))

    def _query(self, prompt: str, conf: dict[str, t.Any]) -> str:
        chat_completion = self.client.with_options(max_retries=0).chat.completions.create(
            max_tokens=conf["max_tokens"],
            temperature=conf["temperature"],
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=conf["model_name"],
        )
        return chat_completion.choices[0].message.content

    def prepare_conf(self, max_tokens=1024, temperature=1.0) -> tuple[str, dict[str, t.Any]]:
        name = f"query interlab {__class__.__qualname__} ({self.model_name})"
        conf = {
            "model_name": self.model_name,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        return name, conf
