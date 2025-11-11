from .LLMEnums import LLMEnums
from .providers import OpenAIProvider, CohereProvider

class LLMProviderFactory:

    def __init__(self, config: dict):
        self.config = config
    
    def create(self, provider: str):

        if provider == LLMEnums.OPENAI.value:
            return OpenAIProvider(
                api_key=self.config.OPENAI_API_KEY,
                api_url=self.config.OPENAI_API_URL,
                default_input_max_characters=self.config.DAFAULT_INPUT_MAX_CHARACTERS,
                default_output_max_tokens=self.config.DAFAULT_OUTPUT_MAX_TOKENS,
                default_temperature=self.config.DAFAULT_TEMPERATURE
            )
        
        if provider == LLMEnums.COHERE.value:
            return CohereProvider(
                api_key=self.config.COHERE_API_KEY,
                default_input_max_characters=self.config.DAFAULT_INPUT_MAX_CHARACTERS,
                default_output_max_tokens=self.config.DAFAULT_OUTPUT_MAX_TOKENS,
                default_temperature=self.config.DAFAULT_TEMPERATURE
            )
        
        return None