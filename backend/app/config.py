import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load standard .env if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "config.json"

class Config:
    def __init__(self):
        self.config_data = {
            "MOCK_MODE": True,
            "GEMINI_API_KEY": "",
            "OPENAI_API_KEY": "",
            "PROVIDER": "gemini",
            "GEMINI_MODEL": "gemini-1.5-flash",
            "OPENAI_MODEL": "gpt-4o-mini"
        }
        self.load()

    def load(self):
        # 1. Start with defaults, check env variables
        self.config_data["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY", os.getenv("GOOGLE_API_KEY", ""))
        self.config_data["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")
        
        # If any key is in env, we can default MOCK_MODE to False
        if self.config_data["GEMINI_API_KEY"] or self.config_data["OPENAI_API_KEY"]:
            self.config_data["MOCK_MODE"] = False
            if self.config_data["OPENAI_API_KEY"] and not self.config_data["GEMINI_API_KEY"]:
                self.config_data["PROVIDER"] = "openai"

        # 2. Override with config.json if it exists (for runtime updates from UI)
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r") as f:
                    saved = json.load(f)
                    self.config_data.update(saved)
            except Exception:
                pass
        
        # Double check: if keys are empty and MOCK_MODE is False, force MOCK_MODE = True
        key_exists = (
            (self.config_data["PROVIDER"] == "gemini" and self.config_data["GEMINI_API_KEY"]) or
            (self.config_data["PROVIDER"] == "openai" and self.config_data["OPENAI_API_KEY"])
        )
        if not key_exists:
            self.config_data["MOCK_MODE"] = True

    def save(self, new_settings: dict):
        self.config_data.update(new_settings)
        
        # Validate keys vs mock mode
        key_exists = (
            (self.config_data["PROVIDER"] == "gemini" and self.config_data["GEMINI_API_KEY"]) or
            (self.config_data["PROVIDER"] == "openai" and self.config_data["OPENAI_API_KEY"])
        )
        if not key_exists:
            self.config_data["MOCK_MODE"] = True
            
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config_data, f, indent=4)
            
        # Update os.environ so LangChain picks them up
        if self.config_data["GEMINI_API_KEY"]:
            os.environ["GEMINI_API_KEY"] = self.config_data["GEMINI_API_KEY"]
            os.environ["GOOGLE_API_KEY"] = self.config_data["GEMINI_API_KEY"]
        if self.config_data["OPENAI_API_KEY"]:
            os.environ["OPENAI_API_KEY"] = self.config_data["OPENAI_API_KEY"]

    @property
    def mock_mode(self) -> bool:
        return self.config_data.get("MOCK_MODE", True)

    @property
    def gemini_api_key(self) -> str:
        return self.config_data.get("GEMINI_API_KEY", "")

    @property
    def openai_api_key(self) -> str:
        return self.config_data.get("OPENAI_API_KEY", "")

    @property
    def provider(self) -> str:
        return self.config_data.get("PROVIDER", "gemini")

    @property
    def gemini_model(self) -> str:
        return self.config_data.get("GEMINI_MODEL", "gemini-1.5-flash")

    @property
    def openai_model(self) -> str:
        return self.config_data.get("OPENAI_MODEL", "gpt-4o-mini")

# Global configuration instance
config = Config()
