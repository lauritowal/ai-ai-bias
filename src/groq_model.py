import functools
import logging
import os
import random
import time
import typing as t

import interlab


@functools.lru_cache(maxsize=None)
class GroqModel(interlab.lang_models.LangModelBase):
    def __init__(self, model_name: str, min_delay=1.0, timeout=120.0):
        self.model_name = model_name
        self.min_delay = min_delay
        self.timeout = timeout
        import groq
        self.client = groq.Groq(api_key=os.environ.get("GROQ_API_KEY"))
        logging.info(
            f"Instantiated GroqModel {model_name} and key {self.client.api_key[:8]}...{self.client.api_key[-6:]}")

    def _query(self, prompt: str, conf: dict[str, t.Any]) -> str:
        import groq
        start = time.time()
        delay = self.min_delay * random.uniform(0.8, 1.2)

        while True:
            try:
                chat_completion = self.client.with_options(max_retries=1).chat.completions.create(
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
            except (groq.APIError) as e:
                if time.time() - start > self.timeout:
                    raise e
                logging.info(f"Query failed, retrying after a delay: {e}")
                time.sleep(delay)
                delay *= 2
                

    def prepare_conf(self, max_tokens=1024, temperature=1.0) -> tuple[str, dict[str, t.Any]]:
        name = f"query interlab {__class__.__qualname__} ({self.model_name})"
        conf = {
            "model_name": self.model_name,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        return name, conf
