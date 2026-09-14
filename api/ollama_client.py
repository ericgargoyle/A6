import os
import requests
import json
from typing import Dict, Any

def ask_ollama(prompt: str, json_format: bool = False) -> str:
    """
    Centralized client to communicate with the local Ollama instance.
    """
    model = os.getenv("OLLAMA_MODEL", "llama3.2")
    base_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    url = f"{base_url}/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    if json_format:
        payload["format"] = "json"
        
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Ollama: {e}")
        return ""
