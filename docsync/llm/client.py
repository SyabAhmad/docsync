import os
import json
from typing import Optional


class LLMClient:
    def __init__(self, provider: str = "groq", model: str = "meta-llama/llama-4-scout-17b-16e-instruct",
                 temperature: float = 0.3, api_key: Optional[str] = None,
                 base_url: Optional[str] = None):
        self.provider = provider
        self.model = model
        self.temperature = temperature
        self.api_key = api_key or os.environ.get(
            "OPENAI_API_KEY" if provider == "openai" else "GROQ_API_KEY", ""
        )
        self.base_url = base_url

    def complete(self, system_prompt: str, user_prompt: str,
                 max_tokens: int = 2048) -> Optional[str]:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": self.temperature,
            "max_tokens": max_tokens,
        }
        result = self._call_api(payload)
        if result and "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        return None

    def _call_api(self, payload: dict) -> Optional[dict]:
        url = self.base_url or (
            "https://api.openai.com/v1/chat/completions"
            if self.provider == "openai"
            else "https://api.groq.com/openai/v1/chat/completions"
        )
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        try:
            import requests
            resp = requests.post(url, json=payload, headers=headers, timeout=60)
            if resp.ok:
                return resp.json()
            print(f"LLM API error: {resp.status_code} {resp.reason}")
            return None
        except ImportError:
            return self._call_api_urllib(url, payload, headers)
        except Exception as e:
            print(f"LLM request failed: {e}")
            return None

    def _call_api_urllib(self, url: str, payload: dict, headers: dict) -> Optional[dict]:
        import urllib.request
        import urllib.error

        data = json.dumps(payload).encode()
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            print(f"LLM API error: {e.code} {e.reason}")
            return None
        except Exception as e:
            print(f"LLM request failed: {e}")
            return None
