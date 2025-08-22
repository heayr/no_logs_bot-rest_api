# bot/services/xray_service.py




import logging
import subprocess
import json
import os
from core.config import settings

def add_client(uuid: str) -> bool:
    """
    Добавляет клиента в конфигурацию Xray.
    """
    try:
        config_path = "/etc/xray/config.json"
        with open(config_path, 'r') as f:
            config = json.load(f)

        for inbound in config.get('inbounds', []):
            if inbound.get('tag') == 'vpn-in':
                # Формируем email в формате user_<первые_8_символов_uuid>@vpn
                email = f"user_{uuid[:8]}@vpn"
                inbound['settings']['clients'].append({
                    "id": uuid,
                    "flow": "xtls-rprx-vision",
                    "email": email,
                    "limitIp": 4
                })
                break

        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        logging.info(f"Добавление клиента в Xray: uuid={uuid}, email={email}")
        result = restart_xray()
        if result:
            logging.info(f"Клиент успешно добавлен в Xray: uuid={uuid}")
            return True
        else:
            logging.error(f"Не удалось перезапустить Xray после добавления клиента: uuid={uuid}")
            return False
    except Exception as e:
        logging.error(f"Ошибка при добавлении клиента в Xray: uuid={uuid}, {str(e)}")
        return False

def remove_client(uuid: str) -> bool:
    """
    Удаляет клиента из конфигурации Xray.
    """
    try:
        config_path = "/etc/xray/config.json"
        with open(config_path, 'r') as f:
            config = json.load(f)

        for inbound in config.get('inbounds', []):
            if inbound.get('tag') == 'vpn-in':
                inbound['settings']['clients'] = [
                    client for client in inbound['settings']['clients']
                    if client['id'] != uuid
                ]
                break

        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        logging.info(f"Удаление клиента из Xray: uuid={uuid}")
        result = restart_xray()
        if result:
            logging.info(f"Клиент успешно удалён из Xray: uuid={uuid}")
            return True
        else:
            logging.error(f"Не удалось перезапустить Xray после удаления клиента: uuid={uuid}")
            return False
    except Exception as e:
        logging.error(f"Ошибка при удалении клиента из Xray: uuid={uuid}, {str(e)}")
        return False

def restart_xray() -> bool:
    """
    Перезапускает Xray для применения изменений конфигурации.
    """
    try:
        subprocess.run(["pkill", "-SIGHUP", "xray"], check=True)
        logging.info("Xray перезапущен через SIGHUP")
        return True
    except subprocess.CalledProcessError:
        logging.warning("SIGHUP не сработал. Перезапускаю контейнер")
        try:
            subprocess.run(["docker", "restart", "xray"], check=True)
            logging.info("Контейнер Xray перезапущен: xray")
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Ошибка при перезапуске Xray: {str(e)}")
            return False