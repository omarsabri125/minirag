from ..LLMInterface import LLMInterface
from ..LLMEnums import OpenAIEnums
from logger import logger
from openai import OpenAI
from typing import Union, List

class OpenAIProvider(LLMInterface):

    def __init__(self, api_key: str,
                 api_url: str = None,
                 default_input_max_characters: int = 1000,
                 default_output_max_tokens: int = 1000,
                 default_temperature: float = 0.1):

        self.api_key = api_key
        self.api_url = api_url

        self.default_input_max_characters = default_input_max_characters
        self.default_output_max_tokens = default_output_max_tokens
        self.default_temperature = default_temperature

        self.generation_model_id = None

        self.embedding_model_id = None
        self.embedding_size = None

        self.client = OpenAI(
            api_key=self.api_key,
            base_url = self.api_url if self.api_url and len(self.api_url) else None
        )

        self.enums = OpenAIEnums

        self.logger = logger

    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_dimension: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_dimension

    def generate_text(self, prompt: str, chat_history=[], max_output_tokens: int = None, temperature: float = None):

        if not self.client:
            logger.error("OpenAI client is not initialized.")
            return None

        if not self.generation_model_id:
            logger.error("Generation model is not set.")
            return None

        max_output_tokens = max_output_tokens if max_output_tokens is not None else self.default_output_max_tokens
        temperature = temperature if temperature is not None else self.default_temperature

        chat_history.append(
            self.construt_prompt(prompt, role=OpenAIEnums.USER.value)
        )

        response = self.client.chat.completions.create(
            model=self.generation_model_id,
            messages=chat_history,
            max_tokens=max_output_tokens,
            temperature=temperature
        )
        if not response or 'choices' not in response or len(response['choices']) == 0 or response.choices[0].message.content is None:
            logger.error("No response returned from OpenAI.")
            return None

        generated_text = response.choices[0].message.content
        return generated_text

    def embed_text(self, text: Union[str, List[str]], document_type: str = None):

        if not self.client:
            logger.error("OpenAI client is not initialized.")
            return None

        if not self.embedding_model_id:
            logger.error("Embedding model is not set.")
            return None
        
        if isinstance(text, str):
            text = [text]

        response = self.client.embeddings.create(
            input=text,
            model=self.embedding_model_id
        )

        if not response or 'data' not in response or len(response['data']) == 0 or response.data[0].embedding is None:
            logger.error("No embedding returned from OpenAI.")
            return None
        
        return [rec.embedding for rec in response.data]

    def construt_prompt(self, prompt: str, role: str):

        return {
            "role": role,
            "content": prompt
        }
