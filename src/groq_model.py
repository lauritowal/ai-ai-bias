import functools
import logging
import os
import time
import typing as t

import interlab


@functools.lru_cache(maxsize=None)
class GroqModel(interlab.lang_models.LangModelBase):
    def __init__(self, model_name: str, min_delay=2.1):
        self.model_name = model_name
        self.min_delay = min_delay
        self.last_query_time = 0
        import groq
        self.client = groq.Groq(api_key=os.environ.get("GROQ_API_KEY"))
        logging.info(
            f"Instantiated GroqModel {model_name} and key {self.client.api_key[:8]}...{self.client.api_key[-6:]}")

    def _query(self, prompt: str, conf: dict[str, t.Any]) -> str:
        passed = time.time() - self.last_query_time
        # Note: this may be in the future if we're running multiple queries in parallel
        # OFC this is a bit of a hack, but it's simple and works well enough
        if passed < self.min_delay:
            self.last_query_time = self.last_query_time + self.min_delay
            logging.info(f"Sleeping for {self.min_delay - passed:.2f} seconds to respect Groq API rate limits.")
            time.sleep(self.min_delay - passed)
        else:
            self.last_query_time = time.time()

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
