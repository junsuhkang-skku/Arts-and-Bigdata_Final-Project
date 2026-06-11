from io import BytesIO
from typing import List, Dict, Any, Optional
import zipfile

import pandas as pd

from src.poster_fetcher import get_image_bytes_from_url, create_safe_filename


def convert_df_to_csv(df: pd.DataFrame) -> bytes:
    """
    DataFrame을 CSV bytes로 변환.

    utf-8-sig를 사용해서 Excel에서 열 때 한글/특수문자 깨짐을 줄임.
    """
    if df is None or df.empty:
        return b""

    export_df = df.copy()

    if "dominant_colors" in export_df.columns:
        export_df["dominant_colors"] = export_df["dominant_colors"].apply(
            lambda colors: " / ".join(colors) if isinstance(colors, list) else colors
        )

    csv_data = export_df.to_csv(index=False).encode("utf-8-sig")

    return csv_data


def prepare_analysis_download_df(analysis_df: pd.DataFrame) -> pd.DataFrame:
    """
    다운로드용 분석 DataFrame 정리.

    너무 긴 overview나 내부용 poster_path 등을 제외하고
    사용자가 분석 결과로 보기 좋은 컬럼만 남김.
    """
    if analysis_df is None or analysis_df.empty:
        return pd.DataFrame()

    preferred_columns = [
        "tmdb_id",
        "title",
        "genres",
        "year",
        "release_date",
        "rating",
        "vote_count",
        "popularity",
        "poster_url",
        "dominant_color",
        "dominant_colors",
        "brightness",
        "saturation",
        "color_diversity",
        "color_mood",
    ]

    available_columns = [
        column for column in preferred_columns if column in analysis_df.columns
    ]

    return analysis_df[available_columns].copy()


def get_poster_file_extension(poster_url: str) -> str:
    """
    poster_url에서 파일 확장자 추정.

    TMDB poster URL은 보통 jpg이지만,
    URL 구조가 바뀌어도 기본값 jpg로 안전하게 처리.
    """
    if not poster_url or not isinstance(poster_url, str):
        return "jpg"

    clean_url = poster_url.split("?")[0].lower()

    if clean_url.endswith(".jpg"):
        return "jpg"

    if clean_url.endswith(".jpeg"):
        return "jpeg"

    if clean_url.endswith(".png"):
        return "png"

    if clean_url.endswith(".webp"):
        return "webp"

    return "jpg"


def create_poster_zip(cart_items: List[Dict[str, Any]]) -> Optional[bytes]:
    """
    Cart에 담긴 poster 이미지들을 ZIP 파일 bytes로 생성.

    입력:
    - cart_items: poster_url과 title이 포함된 dict list

    반환:
    - 성공: zip bytes
    - 실패 또는 cart empty: None
    """
    if not cart_items:
        return None

    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        used_filenames = set()

        for index, item in enumerate(cart_items, start=1):
            poster_url = item.get("poster_url")
            title = item.get("title", f"poster_{index}")

            if not poster_url:
                continue

            image_bytes = get_image_bytes_from_url(poster_url)

            if image_bytes is None:
                continue

            extension = get_poster_file_extension(poster_url)
            filename = create_safe_filename(title, extension=extension)

            # 중복 파일명 방지
            if filename in used_filenames:
                name_part = filename.rsplit(".", 1)[0]
                filename = f"{name_part}_{index}.{extension}"

            used_filenames.add(filename)

            zip_file.writestr(filename, image_bytes)

    zip_buffer.seek(0)

    zip_bytes = zip_buffer.getvalue()

    if len(zip_bytes) == 0:
        return None

    return zip_bytes


def create_cart_info_csv(cart_items: List[Dict[str, Any]]) -> bytes:
    """
    Cart에 담긴 포스터 정보만 CSV로 다운로드하기 위한 함수.
    """
    if not cart_items:
        return b""

    df = pd.DataFrame(cart_items)

    preferred_columns = [
        "tmdb_id",
        "title",
        "genres",
        "year",
        "rating",
        "poster_url",
        "dominant_color",
        "dominant_colors",
        "brightness",
        "saturation",
        "color_diversity",
        "color_mood",
    ]

    available_columns = [
        column for column in preferred_columns if column in df.columns
    ]

    export_df = df[available_columns].copy()

    return convert_df_to_csv(export_df)