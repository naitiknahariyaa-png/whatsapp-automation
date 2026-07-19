"""
MinIO Integration - FREE S3-Compatible Storage
===============================================
Self-hosted object storage

Based on: https://github.com/minio/minio

Features:
- S3-compatible
- 10TB storage FREE
- Self-hosted
- Perfect for media files

Setup:
    docker run -d -p 9000:9000 -p 9001:9001 \\
      minio/minio server /data --console-address ":9001"
"""

import os
import logging
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from typing import Optional, List

logger = logging.getLogger(__name__)


class MinIOClient:
    """
    MinIO Storage Client - S3 Compatible
    
    Use Cases:
    - Store images/videos
    - Backup files
    - Media hosting
    - Document storage
    - WhatsApp media cache
    
    Setup:
    1. Docker (FREE):
       docker run -d -p 9000:9000 -p 9001:9001 \\
         minio/minio server /data --console-address ":9001"
    
    2. Get credentials from console (port 9001)
    
    Environment:
    - MINIO_ENDPOINT=localhost:9000
    - MINIO_ACCESS_KEY=xxx
    - MINIO_SECRET_KEY=xxx
    - MINIO_BUCKET=my-bucket
    """
    
    def __init__(
        self,
        endpoint: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        bucket: Optional[str] = None
    ):
        self.endpoint = endpoint or os.getenv("MINIO_ENDPOINT", "localhost:9000")
        self.access_key = access_key or os.getenv("MINIO_ACCESS_KEY", "")
        self.secret_key = secret_key or os.getenv("MINIO_SECRET_KEY", "")
        self.bucket = bucket or os.getenv("MINIO_BUCKET", "whatsapp-media")
        self.enabled = bool(self.access_key and self.secret_key)
        
        if self.enabled:
            self._init_client()
            logger.info(f"✅ MinIO configured: {self.endpoint}")
        else:
            logger.warning("⚠️ MinIO not configured")
    
    def _init_client(self):
        """Initialize S3 client"""
        self.client = boto3.client(
            "s3",
            endpoint_url=f"http://{self.endpoint}",
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=Config(signature_version="s3v4"),
            region_name="us-east-1"
        )
    
    def create_bucket(self, bucket_name: Optional[str] = None) -> bool:
        """Create bucket"""
        name = bucket_name or self.bucket
        try:
            self.client.create_bucket(Bucket=name)
            return True
        except ClientError:
            return False
    
    def upload_file(
        self,
        file_path: str,
        object_name: Optional[str] = None
    ) -> Optional[str]:
        """
        Upload file
        
        Returns: URL of uploaded file
        """
        if not self.enabled:
            return None
        
        from pathlib import Path
        object_name = object_name or Path(file_path).name
        
        try:
            self.client.upload_file(file_path, self.bucket, object_name)
            return f"http://{self.endpoint}/{self.bucket}/{object_name}"
        except ClientError as e:
            logger.error(f"MinIO upload error: {e}")
            return None
    
    def download_file(self, object_name: str, file_path: str) -> bool:
        """Download file"""
        if not self.enabled:
            return False
        
        try:
            self.client.download_file(self.bucket, object_name, file_path)
            return True
        except ClientError as e:
            logger.error(f"MinIO download error: {e}")
            return False
    
    def delete_file(self, object_name: str) -> bool:
        """Delete file"""
        if not self.enabled:
            return False
        
        try:
            self.client.delete_object(Bucket=self.bucket, Key=object_name)
            return True
        except ClientError as e:
            logger.error(f"MinIO delete error: {e}")
            return False
    
    def list_files(self, prefix: str = "") -> List[str]:
        """List files in bucket"""
        if not self.enabled:
            return []
        
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=prefix
            )
            return [obj["Key"] for obj in response.get("Contents", [])]
        except ClientError as e:
            logger.error(f"MinIO list error: {e}")
            return []
    
    def get_presigned_url(self, object_name: str, expiration: int = 3600) -> Optional[str]:
        """Generate temporary download URL"""
        if not self.enabled:
            return None
        
        try:
            url = self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": object_name},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.error(f"MinIO presigned error: {e}")
            return None


def setup_minio():
    """Setup guide for MinIO"""
    print("\n" + "="*50)
    print("🗄️ MinIO Storage Setup")
    print("="*50 + "\n")
    
    print("Run with Docker (FREE - 10TB):")
    print("-" * 40)
    print("docker run -d -p 9000:9000 -p 9001:9001 \\")
    print("  -v /mnt/data:/data \\")
    print("  minio/minio server /data \\")
    print("  --console-address ':9001'")
    print("\nConsole: http://localhost:9001")
    print("Default credentials: minioadmin / minioadmin\n")
    
    endpoint = input("Endpoint (localhost:9000): ").strip()
    if not endpoint:
        endpoint = "localhost:9000"
    
    access = input("Access Key: ").strip()
    secret = input("Secret Key: ").strip()
    bucket = input("Bucket name: ").strip()
    
    if access and secret:
        with open(".env", "a") as f:
            f.write(f"\n# MinIO (S3-Compatible Storage)\n")
            f.write(f"MINIO_ENDPOINT={endpoint}\n")
            f.write(f"MINIO_ACCESS_KEY={access}\n")
            f.write(f"MINIO_SECRET_KEY={secret}\n")
            if bucket:
                f.write(f"MINIO_BUCKET={bucket}\n")
        print("✅ Saved to .env!")
    else:
        print("❌ Access Key and Secret Key required!")


if __name__ == "__main__":
    setup_minio()
