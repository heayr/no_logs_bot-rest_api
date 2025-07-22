# utils/formatters.py

def generate_vless_link(uuid: str, host: str, port: int, pbk: str, sid: str, sni: str) -> str:
    label = f"VPN-{port}"
    return (
        f"vless://{uuid}@{host}:{port}"
        f"?encryption=none"
        f"&flow=xtls-rprx-vision"
        f"&security=reality"
        f"&sni={sni}"
        f"&fp=chrome"
        f"&pbk={pbk}"
        f"&sid={sid}"
        f"&type=tcp"
        f"&headerType=none"
        f"#{label}"
    )


def format_expiration_message(link: str, days: int) -> str:
    if days == 1:
        day_str = "1 день"
    elif 2 <= days <= 4:
        day_str = f"{days} дня"
    else:
        day_str = f"{days} дней"

    return (
        f"🔒 Ваш VPN-конфиг готов!\n"
        f"⏳ Срок действия: {day_str}\n\n"
        f"📌 Скопируйте эту ссылку:\n<code>{link}</code>\n\n"
        f"📲 Как использовать:\n"
        f"1. Отсканируйте QR-код\n"
        f"2. Или вставьте ссылку вручную\n"
        f"3. Для v2RayTun нажмите кнопку ниже"
    )

