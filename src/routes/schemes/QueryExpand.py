from pydantic import BaseModel

class SemanticExpansion(BaseModel):
    original_query: str
    expanded_query: str


