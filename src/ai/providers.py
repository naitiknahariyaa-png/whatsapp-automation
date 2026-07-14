"""
AI Providers Module
Handles multiple AI provider integrations (Ollama, OpenAI, Claude, Gemini, DeepSeek)
"""

import os
import time
from typing import Optional, Dict, List


class AIProviderRouter:
    """
    Router that manages multiple AI providers
    Provides automatic fallback between providers
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.provider_name = config.get('provider', 'ollama')
        self.providers = {}
        
        # Initialize all providers
        self._init_providers()
        
    def _init_providers(self):
        """Initialize all available AI providers"""
        
        # Ollama (Local)
        try:
            from .ollama_client import OllamaClient
            self.providers['ollama'] = OllamaClient(self.config.get('ollama', {}))
        except ImportError:
            pass
            
        # OpenAI
        try:
            from .openai_client import OpenAIClient
            self.providers['openai'] = OpenAIClient(self.config.get('openai', {}))
        except ImportError:
            pass
            
        # Claude
        try:
            from .claude_client import ClaudeClient
            self.providers['claude'] = ClaudeClient(self.config.get('claude', {}))
        except ImportError:
            pass
            
        # Gemini
        try:
            from .gemini_client import GeminiClient
            self.providers['gemini'] = GeminiClient(self.config.get('gemini', {}))
        except ImportError:
            pass
            
        # DeepSeek
        try:
            from .deepseek_client import DeepSeekClient
            self.providers['deepseek'] = DeepSeekClient(self.config.get('deepseek', {}))
        except ImportError:
            pass
    
    def get_provider(self, name: str = None):
        """Get a specific provider or current default"""
        name = name or self.provider_name
        return self.providers.get(name)
    
    def check_status(self) -> Dict:
        """Check status of all AI providers"""
        status = {
            'default': self.provider_name,
            'providers': {}
        }
        
        for name, provider in self.providers.items():
            try:
                is_available = provider.check_connection()
                status['providers'][name] = {
                    'available': is_available,
                    'model': getattr(provider, 'model', 'unknown')
                }
            except Exception as e:
                status['providers'][name] = {
                    'available': False,
                    'error': str(e)
                }
                
        return status
    
    def generate_response(
        self, 
        message: str, 
        context: str = None,
        sender: str = None,
        temperature: float = None,
        max_tokens: int = None
    ) -> str:
        """
        Generate response using the configured provider
        with fallback to other providers if needed
        """
        # Try default provider first
        provider = self.get_provider()
        
        if provider:
            try:
                return provider.generate(
                    message=message,
                    context=context,
                    sender=sender,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            except Exception as e:
                print(f"Provider {self.provider_name} failed: {e}")
                
        # Fallback to other providers
        for name, fallback_provider in self.providers.items():
            if name != self.provider_name:
                try:
                    return fallback_provider.generate(
                        message=message,
                        context=context,
                        sender=sender,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                except Exception:
                    continue
                    
        return "Sorry, AI is currently unavailable. Please try again later."
    
    def set_provider(self, provider_name: str):
        """Change the default AI provider"""
        if provider_name in self.providers:
            self.provider_name = provider_name
            return True
        return False


# ──────────────────────────────────────────────
# Base Provider Class
# ──────────────────────────────────────────────

class BaseProvider:
    """Base class for all AI providers"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.model = config.get('model', 'unknown')
        self.temperature = config.get('temperature', 0.7)
        self.max_tokens = config.get('max_tokens', 500)
        self.system_prompt = config.get(
            'system_prompt',
            "You are a helpful AI assistant for a business. Keep responses short and friendly."
        )
        
    def generate(
        self, 
        message: str, 
        context: str = None,
        sender: str = None,
        temperature: float = None,
        max_tokens: int = None
    ) -> str:
        """Generate a response - must be implemented by subclasses"""
        raise NotImplementedError
        
    def check_connection(self) -> bool:
        """Check if provider is available - must be implemented by subclasses"""
        raise NotImplementedError
        
    def build_prompt(self, message: str, context: str = None, sender: str = None) -> str:
        """Build the full prompt with context"""
        prompt = self.system_prompt
        
        if context:
            prompt += f"\n\n{context}"
            
        if sender:
            prompt += f"\n\nCustomer ({sender}) says: {message}"
        else:
            prompt += f"\n\nUser says: {message}"
            
        prompt += "\n\nAssistant:"
        
        return prompt


# ──────────────────────────────────────────────
# Ollama Client (Local - Free)
# ──────────────────────────────────────────────

class OllamaProvider(BaseProvider):
    """Ollama local AI provider"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.base_url = config.get('base_url', 'http://localhost:11434')
        self.model = config.get('model', 'llama3.2:latest')
        
    def check_connection(self) -> bool:
        """Check if Ollama is running"""
        try:
            import requests
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
            
    def generate(
        self, 
        message: str, 
        context: str = None,
        sender: str = None,
        temperature: float = None,
        max_tokens: int = None
    ) -> str:
        """Generate response using Ollama"""
        try:
            import requests
            
            prompt = self.build_prompt(message, context, sender)
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature or self.temperature,
                    "num_predict": max_tokens or self.max_tokens
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json().get('response', '').strip()
            else:
                raise Exception(f"Ollama returned status {response.status_code}")
                
        except ImportError:
            return "Ollama library not installed. Run: pip install ollama"
        except Exception as e:
            raise Exception(f"Ollama error: {e}")
    
    def list_models(self) -> List[str]:
        """List available Ollama models"""
        try:
            import requests
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [m['name'] for m in models]
        except:
            pass
        return []


# ──────────────────────────────────────────────
# OpenAI Client
# ──────────────────────────────────────────────

class OpenAIProvider(BaseProvider):
    """OpenAI GPT-4/3.5 provider"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.api_key = config.get('api_key', os.getenv('OPENAI_API_KEY', ''))
        self.model = config.get('model', 'gpt-4')
        
    def check_connection(self) -> bool:
        """Check if OpenAI API is accessible"""
        if not self.api_key:
            return False
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            # Just verify key works
            client.models.list()
            return True
        except:
            return False
            
    def generate(
        self, 
        message: str, 
        context: str = None,
        sender: str = None,
        temperature: float = None,
        max_tokens: int = None
    ) -> str:
        """Generate response using OpenAI"""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.api_key)
            
            messages = [{"role": "system", "content": self.system_prompt}]
            
            if context:
                messages.append({"role": "system", "content": f"Context:\n{context}"})
            
            user_content = message
            if sender:
                user_content = f"[From: {sender}]\n{message}"
                
            messages.append({"role": "user", "content": user_content})
            
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens
            )
            
            return response.choices[0].message.content.strip()
            
        except ImportError:
            return "OpenAI library not installed. Run: pip install openai"
        except Exception as e:
            raise Exception(f"OpenAI error: {e}")


# ──────────────────────────────────────────────
# Claude Client (Anthropic)
# ──────────────────────────────────────────────

class ClaudeProvider(BaseProvider):
    """Anthropic Claude provider"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.api_key = config.get('api_key', os.getenv('ANTHROPIC_API_KEY', ''))
        self.model = config.get('model', 'claude-3-haiku-20240307')
        
    def check_connection(self) -> bool:
        """Check if Claude API is accessible"""
        if not self.api_key:
            return False
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=self.api_key)
            return True
        except:
            return False
            
    def generate(
        self, 
        message: str, 
        context: str = None,
        sender: str = None,
        temperature: float = None,
        max_tokens: int = None
    ) -> str:
        """Generate response using Claude"""
        try:
            from anthropic import Anthropic
            
            client = Anthropic(api_key=self.api_key)
            
            user_content = message
            if sender:
                user_content = f"[From: {sender}]\n{message}"
            
            messages = []
            
            if context:
                messages.append({
                    "role": "assistant",
                    "content": f"Context:\n{context}"
                })
                
            messages.append({
                "role": "user",
                "content": user_content
            })
            
            response = client.messages.create(
                model=self.model,
                system=self.system_prompt,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens
            )
            
            return response.content[0].text.strip()
            
        except ImportError:
            return "Anthropic library not installed. Run: pip install anthropic"
        except Exception as e:
            raise Exception(f"Claude error: {e}")


# ──────────────────────────────────────────────
# Gemini Client (Google)
# ──────────────────────────────────────────────

class GeminiProvider(BaseProvider):
    """Google Gemini provider"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.api_key = config.get('api_key', os.getenv('GEMINI_API_KEY', ''))
        self.model_name = config.get('model', 'gemini-pro')
        
    def check_connection(self) -> bool:
        """Check if Gemini API is accessible"""
        if not self.api_key:
            return False
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            genai.list_models()
            return True
        except:
            return False
            
    def generate(
        self, 
        message: str, 
        context: str = None,
        sender: str = None,
        temperature: float = None,
        max_tokens: int = None
    ) -> str:
        """Generate response using Gemini"""
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=self.system_prompt
            )
            
            prompt = message
            if context:
                prompt = f"Context:\n{context}\n\n{prompt}"
            if sender:
                prompt = f"[From: {sender}]\n{prompt}"
            
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": temperature or self.temperature,
                    "max_output_tokens": max_tokens or self.max_tokens
                }
            )
            
            return response.text.strip()
            
        except ImportError:
            return "Google Generative AI library not installed. Run: pip install google-generativeai"
        except Exception as e:
            raise Exception(f"Gemini error: {e}")


# ──────────────────────────────────────────────
# DeepSeek Client
# ──────────────────────────────────────────────

class DeepSeekProvider(BaseProvider):
    """DeepSeek AI provider"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.api_key = config.get('api_key', os.getenv('DEEPSEEK_API_KEY', ''))
        self.model = config.get('model', 'deepseek-chat')
        
    def check_connection(self) -> bool:
        """Check if DeepSeek API is accessible"""
        if not self.api_key:
            return False
        try:
            import requests
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.get("https://api.deepseek.com/v1/models", headers=headers, timeout=5)
            return response.status_code == 200
        except:
            return False
            
    def generate(
        self, 
        message: str, 
        context: str = None,
        sender: str = None,
        temperature: float = None,
        max_tokens: int = None
    ) -> str:
        """Generate response using DeepSeek"""
        try:
            import requests
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            messages = [{"role": "system", "content": self.system_prompt}]
            
            if context:
                messages.append({"role": "system", "content": f"Context:\n{context}"})
            
            user_content = message
            if sender:
                user_content = f"[From: {sender}]\n{message}"
                
            messages.append({"role": "user", "content": user_content})
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature or self.temperature,
                "max_tokens": max_tokens or self.max_tokens
            }
            
            response = requests.post(
                "https://api.deepseek.com/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content'].strip()
            else:
                raise Exception(f"DeepSeek returned status {response.status_code}")
                
        except ImportError:
            return "Requests library not installed. Run: pip install requests"
        except Exception as e:
            raise Exception(f"DeepSeek error: {e}")
