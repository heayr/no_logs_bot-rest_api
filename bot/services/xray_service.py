# app/bot/services/xray_service.py

import json
from core.config import settings

def add_to_xray(user_uuid: str):
    path = settings.XRAY_CONFIG_PATH
    with open(path, "r+") as f:
        config = json.load(f)

        for inbound in config.get("inbounds", []):
            if inbound.get("tag") == "vpn-in":
                clients = inbound["settings"].setdefault("clients", [])
                clients.append({
                    "id": user_uuid,
                    "flow": "xtls-rprx-vision",
                    "email": f"user_{user_uuid[:8]}@vpn"
                })
                break

        f.seek(0)
        json.dump(config, f, indent=2)
        f.truncate()
