import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings:
    # AWS Bedrock Configuration  
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    AWS_PROFILE = os.getenv("AWS_PROFILE", "default")
    BEDROCK_MODEL_ID = os.getenv("LLM_MODEL", "us.anthropic.claude-3-5-haiku-20241022-v1:0")
    
    # LLM Settings
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1000"))
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    
    # Data Configuration
    CACHE_TTL_MINUTES = int(os.getenv("CACHE_TTL_MINUTES", "60"))
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "10"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    
    # NSE Data
    NSE_DATA_PATH = "/home/sagemaker-user/shared/Equity.csv"
    
    # Rate Limiting
    BATCH_DELAY_SECONDS = int(os.getenv("BATCH_DELAY_SECONDS", "2"))
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10"))

settings = Settings()
