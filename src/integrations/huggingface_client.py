"""
HuggingFace Integration - FREE AI Models
========================================
Access thousands of free AI models

Based on: https://github.com/huggingface/transformers

Features:
- Text generation models
- Image classification
- Sentiment analysis
- Translation
- All FREE!

Setup:
    pip install transformers torch
    HF_API_KEY=your-key
"""

import os
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class HuggingFaceClient:
    """
    HuggingFace AI Models Client
    
    Use Cases:
    - Text generation (LLMs)
    - Sentiment analysis
    - Text classification
    - Translation
    - Image generation
    
    Setup:
    1. Get API key: https://huggingface.co/settings/tokens
    2. pip install transformers torch
    3. Add HF_API_KEY to .env
    
    Environment:
    - HF_API_KEY=hf_xxx
    - HF_MODEL=model-name (optional)
    """
    
    BASE_URL = "https://api-inference.huggingface.co/models"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.api_key = api_key or os.getenv("HF_API_KEY", "")
        self.default_model = model or os.getenv("HF_MODEL", "gpt2")
        self.enabled = bool(self.api_key)
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        
        if self.enabled:
            logger.info("✅ HuggingFace configured")
        else:
            logger.warning("⚠️ HuggingFace not configured (set HF_API_KEY)")
    
    def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_length: int = 100,
        temperature: float = 0.8
    ) -> Optional[str]:
        """
        Generate text from prompt
        
        Popular free models:
        - gpt2 (English)
        - bigscience/bloom-560m (multilingual)
        - meta-llama/Llama-2-7b-hf (requires approval)
        """
        if not self.enabled:
            return None
        
        model = model or self.default_model
        
        import requests
        data = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_length,
                "temperature": temperature,
                "return_full_text": False
            }
        }
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/{model}",
                headers=self.headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "")
            return None
        except Exception as e:
            logger.error(f"HuggingFace generate error: {e}")
            return None
    
    def sentiment_analysis(self, text: str) -> Optional[Dict]:
        """
        Analyze sentiment of text
        
        Returns: {"label": "POSITIVE/NEGATIVE", "score": 0.95}
        """
        if not self.enabled:
            return None
        
        model = "distilbert-base-uncased-finetuned-sst-2-english"
        
        import requests
        data = {"inputs": text}
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/{model}",
                headers=self.headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    # Get the label with highest score
                    labels = result[0]
                    return max(labels, key=lambda x: x.get("score", 0))
            return None
        except Exception as e:
            logger.error(f"Sentiment error: {e}")
            return None
    
    def classify_text(self, text: str, model: str = "facebook/bart-large-mnli") -> Optional[Dict]:
        """
        Zero-shot text classification
        
        Classify text into categories without training
        """
        if not self.enabled:
            return None
        
        import requests
        data = {
            "inputs": text,
            "parameters": {
                "candidate_labels": ["urgent", "important", "casual"]
            }
        }
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/{model}",
                headers=self.headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Classification error: {e}")
            return None
    
    def summarize_text(self, text: str, model: str = "facebook/bart-large-cnn") -> Optional[str]:
        """
        Summarize long text
        """
        if not self.enabled:
            return None
        
        import requests
        data = {"inputs": text}
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/{model}",
                headers=self.headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("summary_text", "")
            return None
        except Exception as e:
            logger.error(f"Summarize error: {e}")
            return None
    
    def translate(
        self,
        text: str,
        source_lang: str = "en",
        target_lang: str = "hi",
        model: str = "facebook/mbart-large-50-many-to-many-mmt"
    ) -> Optional[str]:
        """
        Translate text between languages
        
        For Hindi: use model="unicamp-dl/mt5-ptt5-base-ptt5-sft"
        """
        if not self.enabled:
            return None
        
        # Use Helsinki NLP models for better translations
        model_map = {
            ("en", "hi"): "Helsinki-NLP/opus-mt-en-hi",
            ("hi", "en"): "Helsinki-NLP/opus-mt-hi-en",
            ("en", "es"): "Helsinki-NLP/opus-mt-en-es",
            ("es", "en"): "Helsinki-NLP/opus-mt-es-en",
        }
        
        actual_model = model_map.get((source_lang, target_lang), model)
        
        import requests
        data = {"inputs": text}
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/{actual_model}",
                headers=self.headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("translation_text", "")
            return None
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return None
    
    def image_to_text(self, image_url: str, model: str = "Salesforce/blip-image-captioning-base") -> Optional[str]:
        """
        Generate caption from image URL
        """
        if not self.enabled:
            return None
        
        import requests
        data = {"inputs": image_url}
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/{model}",
                headers=self.headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "")
            return None
        except Exception as e:
            logger.error(f"Image to text error: {e}")
            return None
    
    def extract_keywords(self, text: str) -> List[str]:
        """
        Extract keywords from text
        """
        if not self.enabled:
            return []
        
        model = "ml6team/keyword-extraction-distilbert"
        
        import requests
        data = {"inputs": text}
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/{model}",
                headers=self.headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result and "answer" in result:
                    return [kw.strip() for kw in result["answer"].split(";") if kw.strip()]
            return []
        except Exception as e:
            logger.error(f"Keyword extraction error: {e}")
            return []
    
    def chat(self, message: str, history: List[Dict] = None) -> str:
        """
        Simple chat with context
        """
        if not self.enabled:
            return "HuggingFace not configured"
        
        # Build context
        context = ""
        if history:
            for h in history[-5:]:  # Last 5 messages
                context += f"User: {h.get('user', '')}\n"
                context += f"Bot: {h.get('bot', '')}\n"
        
        prompt = f"{context}User: {message}\nBot:"
        
        response = self.generate_text(prompt, max_length=150)
        return response or "I couldn't generate a response"


def setup_huggingface():
    """Interactive setup for HuggingFace"""
    print("\n" + "="*50)
    print("🤗 HuggingFace Setup")
    print("="*50 + "\n")
    
    print("Get your free API key:")
    print("1. Go to https://huggingface.co/settings/tokens")
    print("2. Create new token")
    print("3. Copy the token (hf_xxx)\n")
    
    api_key = input("HuggingFace API Key: ").strip()
    
    if api_key:
        with open(".env", "a") as f:
            f.write(f"\n# HuggingFace AI (FREE)\n")
            f.write(f"HF_API_KEY={api_key}\n")
            f.write(f"HF_MODEL=gpt2\n")
        print("✅ Saved to .env!")
        print("\nFree models to try:")
        print("- gpt2 (English text generation)")
        print("- bigscience/bloom-560m (multilingual)")
        print("- distilbert-base-uncased-finetuned-sst-2-english (sentiment)")
    else:
        print("❌ API Key required!")


if __name__ == "__main__":
    setup_huggingface()
