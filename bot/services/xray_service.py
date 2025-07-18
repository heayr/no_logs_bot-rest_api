# app/bot/services/xray_service.py

import json
from core.config import settings
import json, subprocess, logging, os, signal
from datetime import datetime, timedelta
from uuid import uuid4
from pathlib import Path
from core.config import settings

def _load_config() -> dict:
    path = Path(settings.XRAY_CONFIG_PATH)
    if not path.exists():
        raise FileNotFoundError(f"{path} not found")
    with path.open("r") as f:
        return json.load(f)

def _save_config(data: dict) -> None:
    path = Path(settings.XRAY_CONFIG_PATH)
    with path.open("w") as f:
        json.dump(data, f, indent=2)

def add_client(uuid: str) -> None:
    cfg = _load_config()

    # ищем инбаунд с тегом 'vpn-in'
    inbound = next((i for i in cfg.get("inbounds", []) if i.get("tag") == "vpn-in"), None)
    if inbound is None:
        raise RuntimeError("Inbound with tag 'vpn-in' not found")

    clients = inbound["settings"].setdefault("clients", [])
    clients.append({
        "id": uuid,
        "flow": "xtls-rprx-vision",
        "email": f"user_{uuid[:8]}@vpn"
    })

    _save_config(cfg)
    _reload_xray()

def _reload_xray():
    """Перезапустить контейнер Xray через docker CLI."""
    try:
        subprocess.run(
            ["docker", "exec", settings.XRAY_CONTAINER, "pkill", "-HUP", "xray"],
            check=True,
            capture_output=True
        )
        logging.info("Xray reloaded (SIGHUP)")
    except subprocess.CalledProcessError:
        logging.warning("SIGHUP не сработал, перезапускаю контейнер")
        try:
            subprocess.run(["docker", "restart", settings.XRAY_CONTAINER], check=True)
            logging.info("Xray container restarted")
        except subprocess.CalledProcessError as e:
            logging.error(f"Не удалось перезапустить контейнер Xray: {e}")
       
