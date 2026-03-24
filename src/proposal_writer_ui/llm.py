from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Protocol


class TextGenerationClient(Protocol):
    def generate_text(self, instructions: str, prompt: str, model: str) -> str:
        ...


class FallbackClient:
    def generate_text(self, instructions: str, prompt: str, model: str) -> str:
        del instructions, model
        return (
            "LLM integration is not configured. "
            "Set OPENAI_API_KEY to enable live generation.\n\n"
            f"Prompt preview:\n{prompt[:1800]}"
        )


@dataclass
class OpenAIResponsesClient:
    api_key: str

    def generate_text(self, instructions: str, prompt: str, model: str) -> str:
        from openai import OpenAI

        client = OpenAI(api_key=self.api_key)
        response = client.responses.create(
            model=model,
            instructions=instructions,
            input=prompt,
        )
        return response.output_text


def build_client() -> TextGenerationClient:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return OpenAIResponsesClient(api_key=api_key)
    return FallbackClient()
