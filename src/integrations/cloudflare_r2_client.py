"""
Cloudflare R2 Integration - Object Storage
Store files, images, and media (S3-compatible, FREE!)
"""

import os
import logging
import boto3
import requests
from botocore.config import Config
from botocore.exceptions import ClientError
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class CloudflareR2Client:
    """
    Cloudflare R2 Storage Client (S3-compatible)
    
    Perfect for:
    - Store WhatsApp media/images
    - Host files for sharing
    - Backup data
    - Serve static assets
    
    FREE: 10GB storage, 1M Class A requests, 10M Class B requests/month
    
    Setup:
    1. Sign up at https://dash.cloudflare.com
    2. Create R2 bucket
    3. Go to R2 → Manage API Tokens
    4. Create custom token with Object Read/Write
    5. Add to .env
    
    Environment:
    - R2_ACCOUNT_ID=xxx
    - R2_ACCESS_KEY_ID=xxx
    - R2_SECRET_ACCESS_KEY=xxx
    - R2_BUCKET_NAME=my-bucket
    - R2_PUBLIC_URL=https://xxx.r2.dev
    """
    
    def __init__(
        self,
        account_id: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        bucket_name: Optional[str] = None,
        public_url: Optional[str] = None
    ):
        self.account_id = account_id or os.getenv("R2_ACCOUNT_ID", "")
        self.access_key = access_key or os.getenv("R2_ACCESS_KEY_ID", "")
        self.secret_key = secret_key or os.getenv("R2_SECRET_ACCESS_KEY", "")
        self.bucket_name = bucket_name or os.getenv("R2_BUCKET_NAME", "")
        self.public_url = public_url or os.getenv("R2_PUBLIC_URL", "")
        self.enabled = bool(self.account_id and self.access_key and self.secret_key and self.bucket_name)
        
        if self.enabled:
            self._init_client()
            logger.info(f"✅ Cloudflare R2 configured: {self.bucket_name}")
        else:
            logger.warning("⚠️ Cloudflare R2 not configured")
    
    def _init_client(self):
        """Initialize S3 client for R2"""
        try:
            self.client = boto3.client(
                "s3",
                endpoint_url=f"https://{self.account_id}.r2.cloudflarestorage.com",
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name="auto",
                config=Config(signature_version="s3v4")
            )
        except Exception as e:
            logger.error(f"R2 client init error: {e}")
            self.enabled = False
    
    def upload_file(
        self,
        file_path: str,
        object_name: Optional[str] = None,
        content_type: Optional[str] = None
    ) -> Optional[str]:
        """
        Upload file to R2
        
        Args:
            file_path: Local file path
            object_name: S3 object name (default: filename)
            content_type: MIME type
            
        Returns:
            Public URL of uploaded file
        """
        if not self.enabled:
            return None
        
        import os
        from pathlib import Path
        
        if not object_name:
            object_name = Path(file_path).name
        
        extra_args = {}
        if content_type:
            extra_args["ContentType"] = content_type
        
        try:
            self.client.upload_file(
                file_path,
                self.bucket_name,
                object_name,
                ExtraArgs=extra_args
            )
            
            return f"{self.public_url}/{object_name}"
            
        except ClientError as e:
            logger.error(f"Upload error: {e}")
            return None
    
    def upload_bytes(
        self,
        data: bytes,
        object_name: str,
        content_type: Optional[str] = None
    ) -> Optional[str]:
        """
        Upload bytes data
        
        Args:
            data: Bytes data
            object_name: S3 object name
            content_type: MIME type
        """
        if not self.enabled:
            return None
        
        extra_args = {}
        if content_type:
            extra_args["ContentType"] = content_type
        
        try:
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=object_name,
                Body=data,
                **extra_args
            )
            
            return f"{self.public_url}/{object_name}"
            
        except ClientError as e:
            logger.error(f"Upload bytes error: {e}")
            return None
    
    def download_file(self, object_name: str, file_path: str) -> bool:
        """Download file from R2"""
        if not self.enabled:
            return False
        
        try:
            self.client.download_file(self.bucket_name, object_name, file_path)
            return True
        except ClientError as e:
            logger.error(f"Download error: {e}")
            return False
    
    def delete_file(self, object_name: str) -> bool:
        """Delete file from R2"""
        if not self.enabled:
            return False
        
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=object_name)
            return True
        except ClientError as e:
            logger.error(f"Delete error: {e}")
            return False
    
    def generate_presigned_url(
        self,
        object_name: str,
        expiration: int = 3600
    ) -> Optional[str]:
        """
        Generate presigned URL (for temporary access)
        
        Args:
            object_name: S3 object name
            expiration: URL expiration in seconds
        """
        if not self.enabled:
            return None
        
        try:
            url = self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": object_name},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.error(f"Presigned URL error: {e}")
            return None
    
    def list_files(self, prefix: str = "") -> list:
        """List files in bucket with optional prefix"""
        if not self.enabled:
            return []
        
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            return response.get("Contents", [])
        except ClientError as e:
            logger.error(f"List files error: {e}")
            return []


def setup_cloudflare_r2():
    """Interactive setup for Cloudflare R2"""
    print("\n" + "="*50)
    print("☁️ Cloudflare R2 Storage Setup")
    print("="*50 + "\n")
    
    print("How to get R2 credentials:")
    print("1. Sign up at https://dash.cloudflare.com")
    print("2. Go to R2 → Create Bucket")
    print("3. Go to R2 → Manage API Tokens")
    print("4. Create Custom Token with:")
    print("   - Account: Edit")
    print("   - Bucket: Object Read/Write")
    print("5. Copy Account ID, Access Key, Secret Key")
    print("6. For public URL, enable Custom Domain or use R2.dev\n")
    
    account_id = input("Account ID: ").strip()
    access_key = input("Access Key ID: ").strip()
    secret_key = input("Secret Access Key: ").strip()
    bucket_name = input("Bucket Name: ").strip()
    public_url = input("Public URL (e.g., https://xxx.r2.dev): ").strip()
    
    if all([account_id, access_key, secret_key, bucket_name]):
        with open(".env", "a") as f:
            f.write(f"\n# Cloudflare R2 Storage\n")
            f.write(f"R2_ACCOUNT_ID={account_id}\n")
            f.write(f"R2_ACCESS_KEY_ID={access_key}\n")
            f.write(f"R2_SECRET_ACCESS_KEY={secret_key}\n")
            f.write(f"R2_BUCKET_NAME={bucket_name}\n")
            if public_url:
                f.write(f"R2_PUBLIC_URL={public_url}\n")
        print("✅ Saved to .env!")
    else:
        print("❌ All fields required!")


if __name__ == "__main__":
    setup_cloudflare_r2()
