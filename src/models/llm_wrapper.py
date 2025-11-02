"""
Unified LLM Wrapper for multiple API providers
Supports: Gemini, Groq, HuggingFace, OpenAI (optional), Anthropic (optional)
All with FREE tier support
"""

import json
import time
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """Standardized response from any LLM"""
    text: str
    model: str
    provider: str
    tokens_used: int
    latency: float
    metadata: Dict[str, Any]


class RateLimiter:
    """Simple rate limiter for API calls"""
    
    def __init__(self, max_calls_per_minute: int):
        self.max_calls = max_calls_per_minute
        self.calls = []
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        now = time.time()
        # Remove calls older than 1 minute
        self.calls = [t for t in self.calls if now - t < 60]
        
        if len(self.calls) >= self.max_calls:
            sleep_time = 60 - (now - self.calls[0])
            if sleep_time > 0:
                logger.info(f"Rate limit reached. Waiting {sleep_time:.2f}s")
                time.sleep(sleep_time)
                self.calls = []
        
        self.calls.append(now)


class LLMWrapper:
    """
    Unified interface for multiple LLM providers
    Handles API calls, rate limiting, and response formatting
    """
    
    def __init__(self, config_path: str = "configs/api_keys.json"):
        """
        Initialize LLM wrapper with API credentials
        
        Args:
            config_path: Path to API keys configuration file
        """
        self.config = self._load_config(config_path)
        self.rate_limiters = {}
        self._initialize_clients()
    
    def _load_config(self, config_path: str) -> Dict:
        """Load API configuration"""
        if not os.path.exists(config_path):
            raise FileNotFoundError(
                f"Config file not found: {config_path}\n"
                f"Please copy configs/api_keys.example.json to configs/api_keys.json "
                f"and add your API keys."
            )
        
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def _initialize_clients(self):
        """Initialize API clients for enabled providers"""
        self.clients = {}
        
        # Initialize Gemini
        if self.config.get('gemini', {}).get('api_key'):
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.config['gemini']['api_key'])
                self.clients['gemini'] = genai
                rpm = self.config['gemini'].get('rate_limit_rpm', 15)
                self.rate_limiters['gemini'] = RateLimiter(rpm)
                logger.info("✓ Gemini initialized")
            except ImportError:
                logger.warning("google-generativeai not installed. Install with: pip install google-generativeai")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini: {e}")
        
        # Initialize Groq
        if self.config.get('groq', {}).get('api_key'):
            try:
                from groq import Groq
                self.clients['groq'] = Groq(api_key=self.config['groq']['api_key'])
                rpm = self.config['groq'].get('rate_limit_rpm', 30)
                self.rate_limiters['groq'] = RateLimiter(rpm)
                logger.info("✓ Groq initialized")
            except ImportError:
                logger.warning("groq not installed. Install with: pip install groq")
            except Exception as e:
                logger.warning(f"Failed to initialize Groq: {e}")
        
        # Initialize HuggingFace
        if self.config.get('huggingface', {}).get('api_key'):
            try:
                from huggingface_hub import InferenceClient
                self.clients['huggingface'] = InferenceClient(
                    token=self.config['huggingface']['api_key']
                )
                rpm = self.config['huggingface'].get('rate_limit_rpm', 10)
                self.rate_limiters['huggingface'] = RateLimiter(rpm)
                logger.info("✓ HuggingFace initialized")
            except ImportError:
                logger.warning("huggingface-hub not installed. Install with: pip install huggingface-hub")
            except Exception as e:
                logger.warning(f"Failed to initialize HuggingFace: {e}")
        
        # Initialize OpenAI (optional)
        if self.config.get('openai', {}).get('api_key'):
            try:
                from openai import OpenAI
                self.clients['openai'] = OpenAI(api_key=self.config['openai']['api_key'])
                rpm = self.config['openai'].get('rate_limit_rpm', 3)
                self.rate_limiters['openai'] = RateLimiter(rpm)
                logger.info("✓ OpenAI initialized")
            except ImportError:
                logger.warning("openai not installed. Install with: pip install openai")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI: {e}")
        
        if not self.clients:
            raise ValueError("No LLM providers configured! Please add API keys to configs/api_keys.json")
    
    def generate(
        self,
        prompt: str,
        provider: str = "gemini",
        temperature: float = 0.7,
        max_tokens: int = 512,
        **kwargs
    ) -> LLMResponse:
        """
        Generate text using specified LLM provider
        
        Args:
            prompt: Input prompt
            provider: LLM provider (gemini, groq, huggingface, openai)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters
        
        Returns:
            LLMResponse object with standardized output
        """
        if provider not in self.clients:
            raise ValueError(f"Provider '{provider}' not initialized. Available: {list(self.clients.keys())}")
        
        # Apply rate limiting
        if provider in self.rate_limiters:
            self.rate_limiters[provider].wait_if_needed()
        
        # Route to appropriate provider
        start_time = time.time()
        
        if provider == "gemini":
            response = self._generate_gemini(prompt, temperature, max_tokens, **kwargs)
        elif provider == "groq":
            response = self._generate_groq(prompt, temperature, max_tokens, **kwargs)
        elif provider == "huggingface":
            response = self._generate_huggingface(prompt, temperature, max_tokens, **kwargs)
        elif provider == "openai":
            response = self._generate_openai(prompt, temperature, max_tokens, **kwargs)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        response.latency = time.time() - start_time
        return response
    
    def _generate_gemini(self, prompt: str, temperature: float, max_tokens: int, **kwargs) -> LLMResponse:
        """Generate using Google Gemini"""
        model_name = self.config['gemini'].get('model', 'gemini-1.5-flash')
        model = self.clients['gemini'].GenerativeModel(model_name)
        
        generation_config = {
            'temperature': temperature,
            'max_output_tokens': max_tokens,
        }
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        return LLMResponse(
            text=response.text,
            model=model_name,
            provider="gemini",
            tokens_used=response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0,
            latency=0,  # Will be set by caller
            metadata={'raw_response': response}
        )
    
    def _generate_groq(self, prompt: str, temperature: float, max_tokens: int, **kwargs) -> LLMResponse:
        """Generate using Groq"""
        model_name = self.config['groq'].get('model', 'llama3-70b-8192')
        
        response = self.clients['groq'].chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        return LLMResponse(
            text=response.choices[0].message.content,
            model=model_name,
            provider="groq",
            tokens_used=response.usage.total_tokens,
            latency=0,
            metadata={'raw_response': response}
        )
    
    def _generate_huggingface(self, prompt: str, temperature: float, max_tokens: int, **kwargs) -> LLMResponse:
        """Generate using HuggingFace Inference API (Free tier)"""
        # Use a reliable free model - google/flan-t5-large works well without auth
        model_name = self.config['huggingface'].get('model', 'google/flan-t5-large')
        
        try:
            # Try with authentication if token provided
            response = self.clients['huggingface'].text_generation(
                prompt,
                model=model_name,
                max_new_tokens=max_tokens,
                temperature=temperature,
                return_full_text=False
            )
        except Exception as e:
            # Fallback: try without complex parameters
            try:
                response = self.clients['huggingface'].text_generation(
                    prompt,
                    model=model_name,
                    max_new_tokens=max_tokens
                )
            except Exception as e2:
                # If all fails, provide error message
                raise Exception(f"HuggingFace API error: {e2}")
        
        return LLMResponse(
            text=response if isinstance(response, str) else str(response),
            model=model_name,
            provider="huggingface",
            tokens_used=0,  # Not provided by HF Inference API
            latency=0,
            metadata={'raw_response': response}
        )
    
    def _generate_openai(self, prompt: str, temperature: float, max_tokens: int, **kwargs) -> LLMResponse:
        """Generate using OpenAI (optional, if user has credits)"""
        model_name = self.config['openai'].get('model', 'gpt-3.5-turbo')
        
        response = self.clients['openai'].chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        return LLMResponse(
            text=response.choices[0].message.content,
            model=model_name,
            provider="openai",
            tokens_used=response.usage.total_tokens,
            latency=0,
            metadata={'raw_response': response}
        )
    
    def batch_generate(
        self,
        prompts: List[str],
        provider: str = "gemini",
        **kwargs
    ) -> List[LLMResponse]:
        """
        Generate responses for multiple prompts
        
        Args:
            prompts: List of prompts
            provider: LLM provider to use
            **kwargs: Additional generation parameters
        
        Returns:
            List of LLMResponse objects
        """
        responses = []
        for i, prompt in enumerate(prompts):
            logger.info(f"Processing prompt {i+1}/{len(prompts)}")
            try:
                response = self.generate(prompt, provider=provider, **kwargs)
                responses.append(response)
            except Exception as e:
                logger.error(f"Error generating response {i+1}: {e}")
                # Add error response
                responses.append(LLMResponse(
                    text="",
                    model="",
                    provider=provider,
                    tokens_used=0,
                    latency=0,
                    metadata={'error': str(e)}
                ))
        
        return responses
    
    def get_available_providers(self) -> List[str]:
        """Get list of initialized providers"""
        return list(self.clients.keys())


# Example usage
if __name__ == "__main__":
    # Test the wrapper
    try:
        llm = LLMWrapper()
        print(f"Available providers: {llm.get_available_providers()}")
        
        # Test with a simple prompt
        if llm.get_available_providers():
            provider = llm.get_available_providers()[0]
            response = llm.generate(
                "What is the capital of France?",
                provider=provider,
                temperature=0.7,
                max_tokens=50
            )
            print(f"\nTest generation with {provider}:")
            print(f"Response: {response.text}")
            print(f"Tokens: {response.tokens_used}")
            print(f"Latency: {response.latency:.2f}s")
    except Exception as e:
        print(f"Error: {e}")
        print("\nPlease configure your API keys in configs/api_keys.json")
