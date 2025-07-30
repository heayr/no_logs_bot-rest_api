from io import BytesIO
from PIL import Image
import qrcode

async def generate_qr_code(data: str) -> BytesIO:
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_io = BytesIO()
    qr_img.save(qr_io, format="PNG")
    qr_io.seek(0)
    return qr_io