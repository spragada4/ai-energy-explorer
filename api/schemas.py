# api/schemas.py
from pydantic import BaseModel

class EnergyPredictRequest(BaseModel):
    organization: str          # e.g. "OpenAI", "Anthropic", "Google DeepMind", "Meta AI", "DeepSeek"
    input_tokens: int
    output_tokens: int
    is_long_prompt: bool
    is_reasoning_or_heavy: bool = False

class EnergyPredictResponse(BaseModel):
    estimated_wh: float
    model_version: str
    confidence_note: str