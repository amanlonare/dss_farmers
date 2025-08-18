import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parents[1]

# MCP Server configurations
MCP_SERVERS = {
    "weather-server": {
        "url": os.getenv("WEATHER_SERVER_URL", "http://127.0.0.1:8000/sse"),
        "command": "python",
        "args": [str(BASE_DIR / "mcp_servers/weather_server.py")],
        "env": {"PORT": "8000", "WEATHER_API": os.getenv("WEATHER_API", "")},
    },
    "document-rag-server": {
        "url": os.getenv("RAG_SERVER_URL", "http://127.0.0.1:8001/sse"),
        "command": "python",
        "args": [str(BASE_DIR / "mcp_servers/document_rag_server.py")],
        "env": {"PORT": "8001"},
    },
}

# LLM Configuration
LLM_CONFIG = {
    # "model_name": "Xianjun/PLLaMa-7b-base",
    # "generation_params": {
    #     "max_new_tokens": 1024,
    #     "temperature": 0.7,
    #     "do_sample": True,
    #     "top_p": 0.9,
    # },
    "model_name": "mrSoul7766/AgriQBot",
    "generation_params": {
        "max_length": 256,  # Use max_length for Seq2Seq models
        "do_sample": True,
        "top_p": 0.9,
    },
}
