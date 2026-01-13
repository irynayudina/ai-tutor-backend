from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
from typing import Dict, Any, Optional, List
from app.config import settings
import json

class LLMService:
    """Service for interacting with LLM providers"""
    
    def __init__(self):
        self.provider = settings.llm_provider
        self.model = settings.llm_model
        
        if self.provider == "openai":
            self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        elif self.provider == "anthropic":
            self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    async def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        response_format: Optional[Dict] = None
    ) -> str:
        """Generate response from LLM"""
        
        if self.provider == "openai":
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            if response_format:
                kwargs["response_format"] = response_format
            
            response = await self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        
        elif self.provider == "anthropic":
            system = system_prompt if system_prompt else ""
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
    
    async def generate_structured_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        schema: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Generate structured JSON response"""
        
        if self.provider == "openai" and schema:
            # Use JSON mode for OpenAI
            response_format = {"type": "json_object"}
            system_with_schema = f"{system_prompt}\n\nRespond in valid JSON matching this schema: {json.dumps(schema)}"
            
            response = await self.generate_response(
                prompt,
                system_prompt=system_with_schema,
                response_format=response_format
            )
        else:
            # For other providers or no schema, ask for JSON in prompt
            json_prompt = f"{prompt}\n\nRespond with valid JSON only."
            response = await self.generate_response(
                json_prompt,
                system_prompt=system_prompt
            )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback: try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            raise ValueError("Failed to parse JSON response")