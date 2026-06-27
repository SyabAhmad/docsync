import os
import json
from typing import Optional, List, Dict, Any


class LLMClient:
    def __init__(self, provider: str = "openai", model: str = "gpt-4o-mini",
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
        if self.provider == "openai":
            return self._complete_openai(system_prompt, user_prompt, max_tokens)
        elif self.provider == "groq":
            return self._complete_groq(system_prompt, user_prompt, max_tokens)
        else:
            return self._complete_openai(system_prompt, user_prompt, max_tokens)

    def _call_api(self, payload: dict) -> Optional[dict]:
        import urllib.request
        import urllib.error

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        data = json.dumps(payload).encode()
        url = self.base_url or (
            "https://api.openai.com/v1/chat/completions"
            if self.provider == "openai"
            else "https://api.groq.com/openai/v1/chat/completions"
        )
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            print(f"LLM API error: {e.code} {e.reason}")
            return None
        except Exception as e:
            print(f"LLM request failed: {e}")
            return None

    def _complete_openai(self, system: str, user: str, max_tokens: int) -> Optional[str]:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": self.temperature,
            "max_tokens": max_tokens,
        }
        result = self._call_api(payload)
        if result and "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        return None

    def _complete_groq(self, system: str, user: str, max_tokens: int) -> Optional[str]:
        return self._complete_openai(system, user, max_tokens)
