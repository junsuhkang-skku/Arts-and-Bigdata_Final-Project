from io import BytesIO

import requests
from PIL import Image
from typing import Optional

def load_image_from_url(url: str) -> Optional[Image.Image]:
    """
    포스터 URL에서 이미지를 불러와 Pillow Image 객체로 반환.
    """
    if not url:
        return None

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        image = Image.open(BytesIO(response.content)).convert("RGB")
        return image

    except Exception:
        return None