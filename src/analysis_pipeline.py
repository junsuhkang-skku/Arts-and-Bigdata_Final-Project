from typing import Dict, Any, Optional

import pandas as pd

from src.poster_fetcher import load_image_from_url
from src.color_analysis import analyze_poster


def analyze_single_movie_row(movie_row: Dict[str, Any]) -> Dict[str, Any]:
    """
    영화 1개 row에 대해 포스터 색상 분석을 수행.

    입력:
    - movie_row: TMDB 영화 정보 dict

    반환:
    - 기존 영화 정보 + 색상 분석 결과 dict
    """
    poster_url = movie_row.get("poster_url")

    image = load_image_from_url(poster_url)
    analysis_result = analyze_poster(image)

    result = dict(movie_row)
    result.update(analysis_result)

    return result


def analyze_single_movie_dataframe(movie_df: pd.DataFrame) -> pd.DataFrame:
    """
    영화 1개 또는 소수의 영화 DataFrame을 분석.
    Movie Title Search의 detail page에서 주로 사용.
    """
    if movie_df is None or movie_df.empty:
        return pd.DataFrame()

    rows = []

    for _, row in movie_df.iterrows():
        movie_dict = row.to_dict()
        analyzed_row = analyze_single_movie_row(movie_dict)
        rows.append(analyzed_row)

    return pd.DataFrame(rows)


def analyze_movie_dataframe(
    movie_df: pd.DataFrame,
    max_movies: Optional[int] = None,
) -> pd.DataFrame:
    """
    여러 영화 DataFrame에 대해 포스터 색상 분석을 수행.

    입력:
    - movie_df: TMDB API에서 받은 영화 DataFrame
    - max_movies: 분석 개수 제한. None이면 전체 분석.

    반환:
    - 분석 결과가 추가된 DataFrame

    추가되는 컬럼:
    - dominant_color
    - dominant_colors
    - brightness
    - saturation
    - color_diversity
    - color_mood
    """
    if movie_df is None or movie_df.empty:
        return pd.DataFrame()

    df = movie_df.copy()

    if "poster_url" not in df.columns:
        return pd.DataFrame()

    df = df.dropna(subset=["poster_url"])

    if max_movies is not None:
        df = df.head(max_movies)

    analyzed_rows = []

    for _, row in df.iterrows():
        movie_dict = row.to_dict()
        analyzed_row = analyze_single_movie_row(movie_dict)
        analyzed_rows.append(analyzed_row)

    analysis_df = pd.DataFrame(analyzed_rows)

    if analysis_df.empty:
        return analysis_df

    analysis_df = clean_analysis_dataframe(analysis_df)

    return analysis_df


def clean_analysis_dataframe(analysis_df: pd.DataFrame) -> pd.DataFrame:
    """
    분석 결과 DataFrame 정리.

    - year 숫자 변환
    - rating/popularity 숫자 변환
    - brightness/saturation 숫자 변환
    - 분석 불가능한 row 제거
    """
    if analysis_df is None or analysis_df.empty:
        return pd.DataFrame()

    df = analysis_df.copy()

    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce")

    numeric_columns = [
        "rating",
        "vote_count",
        "popularity",
        "brightness",
        "saturation",
        "color_diversity",
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    required_columns = [
        "poster_url",
        "dominant_color",
        "brightness",
        "saturation",
    ]

    existing_required_columns = [
        column for column in required_columns if column in df.columns
    ]

    if existing_required_columns:
        df = df.dropna(subset=existing_required_columns)

    if "year" in df.columns:
        df["year"] = df["year"].fillna(0).astype(int)

    return df


def filter_movie_dataframe(
    movie_df: pd.DataFrame,
    min_rating: float = 0.0,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
) -> pd.DataFrame:
    """
    영화 DataFrame 필터링.

    Dashboard에서 API 결과를 받은 뒤,
    rating / year 조건을 한 번 더 안전하게 적용.
    """
    if movie_df is None or movie_df.empty:
        return pd.DataFrame()

    df = movie_df.copy()

    if "rating" in df.columns:
        df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
        df = df[df["rating"] >= min_rating]

    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce")
        df = df.dropna(subset=["year"])
        df["year"] = df["year"].astype(int)

        if start_year is not None:
            df = df[df["year"] >= start_year]

        if end_year is not None:
            df = df[df["year"] <= end_year]

    if "poster_url" in df.columns:
        df = df.dropna(subset=["poster_url"])

    return df


def get_analysis_summary(analysis_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Dataset Overview에 표시할 요약 정보 생성.
    """
    if analysis_df is None or analysis_df.empty:
        return {
            "movies_found": 0,
            "average_rating": 0,
            "average_popularity": 0,
            "poster_images": 0,
            "average_brightness": 0,
            "average_saturation": 0,
        }

    df = analysis_df.copy()

    summary = {
        "movies_found": len(df),
        "average_rating": round(df["rating"].mean(), 2) if "rating" in df.columns else 0,
        "average_popularity": round(df["popularity"].mean(), 2) if "popularity" in df.columns else 0,
        "poster_images": int(df["poster_url"].notna().sum()) if "poster_url" in df.columns else 0,
        "average_brightness": round(df["brightness"].mean(), 2) if "brightness" in df.columns else 0,
        "average_saturation": round(df["saturation"].mean(), 3) if "saturation" in df.columns else 0,
    }

    return summary