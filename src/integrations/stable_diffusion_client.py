"""
Stable Diffusion Integration - FREE Image Generation
===================================================
Generate images from text prompts

Based on: https://github.com/AUTOMATIC1111/stable-diffusion-webui

Features:
- Text to image
- Image to image
- Inpainting
- All FREE!

Setup:
    # Run locally or use cloud API
    SD_API_URL=http://localhost:7860
"""

import os
import logging
import base64
import requests
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class StableDiffusionClient:
    """
    Stable Diffusion Image Generation
    
    Use Cases:
    - Generate product images
    - Create marketing visuals
    - Design assets
    - AI art generation
    
    Setup Options:
    
    1. Local (FREE):
       - Install AUTOMATIC1111 WebUI
       - Run with --api flag
       - SD_API_URL=http://localhost:7860
    
    2. Cloud (PAID):
       - Use Replicate, Modal, etc.
       - Or use free tiers like Modal
    
    Environment:
    - SD_API_URL=http://localhost:7860
    - SD_MODEL=model-name (optional)
    """
    
    def __init__(
        self,
        api_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.api_url = api_url or os.getenv("SD_API_URL", "http://localhost:7860")
        self.model = model or os.getenv("SD_MODEL", "stabilityai/stable-diffusion-xl-base-1.0")
        self.enabled = self._check_connection()
        
        if self.enabled:
            logger.info(f"✅ Stable Diffusion configured: {self.api_url}")
        else:
            logger.warning("⚠️ Stable Diffusion not configured")
    
    def _check_connection(self) -> bool:
        """Check if SD API is available"""
        try:
            response = requests.get(f"{self.api_url}/sdapi/v1/options", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 512,
        height: int = 512,
        steps: int = 20,
        cfg_scale: float = 7.0,
        seed: int = -1
    ) -> Optional[Dict]:
        """
        Generate image from text prompt
        
        Args:
            prompt: Description of image to generate
            negative_prompt: What to avoid
            width: Image width (512, 768, 1024)
            height: Image height
            steps: Quality steps (more = better but slower)
            cfg_scale: How closely to follow prompt (5-15)
            seed: Random seed (-1 for random)
        """
        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "seed": seed if seed >= 0 else -1,
            "sampler_name": "Euler a"
        }
        
        try:
            # Text to image endpoint
            response = requests.post(
                f"{self.api_url}/sdapi/v1/txt2img",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                # Decode base64 image
                image_data = result.get("images", [{}])[0]
                if isinstance(image_data, str):
                    return {
                        "image_base64": image_data,
                        "seed": result.get("parameters", {}).get("seed"),
                        "model": self.model
                    }
            return None
        except Exception as e:
            logger.error(f"SD generate error: {e}")
            return None
    
    def generate_product_image(
        self,
        product_name: str,
        style: str = "professional white background",
        background: str = "clean white"
    ) -> Optional[Dict]:
        """
        Generate product image for e-commerce
        """
        prompt = f"{product_name}, {style}, {background}, high quality product photography, commercial photography, sharp focus, studio lighting"
        negative = "blurry, low quality, distorted, watermark, text, logo"
        
        return self.generate_image(
            prompt=prompt,
            negative_prompt=negative,
            width=768,
            height=768,
            steps=30
        )
    
    def generate_marketing_image(
        self,
        theme: str,
        text_overlay: str = "",
        style: str = "modern, vibrant, professional"
    ) -> Optional[Dict]:
        """
        Generate marketing/social media image
        """
        prompt = f"{theme}, {style}, digital art, high quality, 4k"
        negative = "text, watermark, low quality"
        
        return self.generate_image(
            prompt=prompt,
            negative_prompt=negative,
            width=1024,
            height=512,
            steps=25
        )
    
    def img2img(
        self,
        image_base64: str,
        prompt: str,
        strength: float = 0.75,
        **kwargs
    ) -> Optional[Dict]:
        """
        Transform existing image
        
        Args:
            image_base64: Base64 encoded input image
            prompt: Description of desired output
            strength: How much to transform (0-1)
        """
        payload = {
            "init_images": [image_base64],
            "prompt": prompt,
            "strength": strength,
            "steps": kwargs.get("steps", 20),
            "cfg_scale": kwargs.get("cfg_scale", 7.0)
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/sdapi/v1/img2img",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return {"image_base64": result.get("images", [{}])[0]}
            return None
        except Exception as e:
            logger.error(f"SD img2img error: {e}")
            return None
    
    def inpaint(
        self,
        image_base64: str,
        mask_base64: str,
        prompt: str,
        **kwargs
    ) -> Optional[Dict]:
        """
        Inpaint (edit specific parts of image)
        """
        payload = {
            "init_images": [image_base64],
            "mask": mask_base64,
            "prompt": prompt,
            "inpaint_full_res": False,
            "inpainting_fill": 1,
            "steps": kwargs.get("steps", 20)
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/sdapi/v1/img2img",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return {"image_base64": result.get("images", [{}])[0]}
            return None
        except Exception as e:
            logger.error(f"SD inpaint error: {e}")
            return None
    
    def upscale(self, image_base64: str, scale: int = 2) -> Optional[Dict]:
        """
        Upscale image (2x or 4x)
        """
        payload = {
            "image": image_base64,
            "upscaling_resize_w": 0,
            "upscaling_resize_h": 0,
            "upscaling_crop": True,
            "upscaler_1": "R-ESRGAN 4x+",
            "extras_upscaler_1_visibility": 1,
            "upscale_first": True
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/sdapi/v1/extra-single-image",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return {"image_base64": result.get("image")}
            return None
        except Exception as e:
            logger.error(f"SD upscale error: {e}")
            return None
    
    def save_image(self, image_base64: str, filename: str) -> str:
        """Save base64 image to file"""
        import base64
        from pathlib import Path
        
        output_dir = Path("generated_images")
        output_dir.mkdir(exist_ok=True)
        
        filepath = output_dir / f"{filename}.png"
        
        with open(filepath, "wb") as f:
            f.write(base64.b64decode(image_base64))
        
        return str(filepath)
    
    def get_samplers(self) -> list:
        """Get available samplers"""
        try:
            response = requests.get(f"{self.api_url}/sdapi/v1/samplers", timeout=5)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return []
    
    def get_models(self) -> list:
        """Get available models"""
        try:
            response = requests.get(f"{self.api_url}/sdapi/v1/sd-models", timeout=5)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return []


def setup_stable_diffusion():
    """Setup guide for Stable Diffusion"""
    print("\n" + "="*50)
    print("🎨 Stable Diffusion Setup")
    print("="*50 + "\n")
    
    print("OPTION 1: Local Installation (FREE)")
    print("-" * 40)
    print("1. Install from: https://github.com/AUTOMATIC1111/stable-diffusion-webui")
    print("2. Download a model (SDXL recommended)")
    print("3. Run with --api flag:")
    print("   ./webui-user.bat (Windows)")
    print("   ./webui.sh (Linux/Mac)")
    print("4. Add flag: set COMMANDLINE_ARGS=--api --listen")
    print("\nDefault URL: http://localhost:7860\n")
    
    print("OPTION 2: Use Cloud (PAID)")
    print("-" * 40)
    print("1. Replicate: https://replicate.com")
    print("2. Modal: https://modal.com (has free tier)")
    print("3. Use their API URLs instead\n")
    
    api_url = input("API URL (press Enter for default): ").strip()
    if not api_url:
        api_url = "http://localhost:7860"
    
    with open(".env", "a") as f:
        f.write(f"\n# Stable Diffusion (Image Generation)\n")
        f.write(f"SD_API_URL={api_url}\n")
    
    print(f"✅ Saved! URL: {api_url}")


if __name__ == "__main__":
    setup_stable_diffusion()
