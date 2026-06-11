from io import BytesIO
from typing import Optional

import requests
from PIL import Image


def load_image_from_url(url: str) -> Optional[Image.Image]:
    """
    poster_url에서 이미지를 불러와 Pillow Image 객체로 반환.

    반환:
    - 성공: PIL.Image.Image
    - 실패: None
    """
    if not url:
        return None

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        image = Image.open(BytesIO(response.content)).convert("RGB")
        return image

    except Exception:
        return None


def get_image_bytes_from_url(url: str) -> Optional[bytes]:
    """
    poster_url에서 이미지 원본 bytes를 가져옴.
    Poster download button 또는 ZIP download에서 사용.

    반환:
    - 성공: bytes
    - 실패: None
    """
    if not url:
        return None

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.content

    except Exception:
        return None


def image_to_png_bytes(image: Image.Image) -> Optional[bytes]:
    """
    Pillow Image 객체를 PNG bytes로 변환.
    분석된 이미지나 변환된 이미지를 다운로드할 때 사용 가능.
    """
    if image is None:
        return None

    try:
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer.getvalue()

    except Exception:
        return None


def create_safe_filename(title: str, extension: str = "jpg") -> str:
    """
    영화 제목을 파일명으로 사용할 수 있도록 안전하게 변환.

    예:
    'The Batman: Part II' -> 'the_batman_part_ii.jpg'
    """
    if not title:
        title = "poster"

    safe_title = title.lower().strip()

    replace_chars = [
        " ",
        ":",
        "/",
        "\\",
        "?",
        "*",
        '"',
        "<",
        ">",
        "|",
        "'",
        ",",
        ".",
    ]

    for char in replace_chars:
        safe_title = safe_title.replace(char, "_")

    while "__" in safe_title:
        safe_title = safe_title.replace("__", "_")

    safe_title = safe_title.strip("_")

    if not safe_title:
        safe_title = "poster"

    return f"{safe_title}.{extension}"