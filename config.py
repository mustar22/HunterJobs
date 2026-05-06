import json
import os

SETTINGS_PATH = "settings.json"

def load_settings():
    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, "r") as f:
            return json.load(f)
    return {}

_s = load_settings()

PROFILE = _s.get("profile", "")
HARD_REJECT = [x.strip() for x in _s.get("hard_reject", "").split("\n") if x.strip()]
SEARCH_TERMS = [x.strip() for x in _s.get("search_terms", "").split("\n") if x.strip()]
GEMMA_API_KEY = _s.get("gemma_api_key", "")
TELEGRAM_TOKEN = _s.get("telegram_token", "")
TELEGRAM_CHAT_ID = _s.get("telegram_chat_id", "")
HOURS_OLD = int(_s.get("hours_old", 48))
CUSTOM_INSTRUCTIONS = _s.get("custom_instructions", "")
SCORING_RUBRIC = """
SCORING RUBRIC — follow this strictly:

AUTO-FAIL (Score 1-3):
- Building internal enterprise tools only
- Heavy emphasis on enterprise MLOps, Kubernetes
- Staffing/recruitment agency hiding end client
- Pure data science or analytics role
- Requires 5+ years with no flexibility

NEUTRAL (Score 4-6):
- Standard API work, general Python backend
- Interesting domain but significant stack mismatch

FAST-TRACK (Score 7-10):
- Image/video/audio generation involved
- Mentions ComfyUI, Stable Diffusion, Flux, RVC, PyTorch, WAN, LTX
- B2B, contractor, or global remote explicitly mentioned
- Startup culture, shipping fast, portfolio over degree
- 0-3 years experience acceptable
"""