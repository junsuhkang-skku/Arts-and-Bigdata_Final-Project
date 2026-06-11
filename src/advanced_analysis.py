from typing import Dict

import pandas as pd


def create_genre_average_df(analysis_df: pd.DataFrame) -> pd.DataFrame:
    """
    장르별 평균 brightness, saturation, color diversity 계산.

    하나의 영화가 여러 장르를 가질 수 있으므로
    'Action, Adventure, Fantasy' 같은 문자열을 분리해서 처리.
    """
    if analysis_df is None or analysis_df.empty:
        return pd.DataFrame()

    if "genres" not in analysis_df.columns:
        return pd.DataFrame()

    genre_rows = []

    for _, row in analysis_df.iterrows():
        genres = row.get("genres", "")

        if not isinstance(genres, str):
            continue

        genre_list = [genre.strip() for genre in genres.split(",")]

        for genre in genre_list:
            if not genre or genre == "Unknown":
                continue

            genre_rows.append({
                "genre": genre,
                "brightness": row.get("brightness"),
                "saturation": row.get("saturation"),
                "color_diversity": row.get("color_diversity"),
                "rating": row.get("rating"),
                "title": row.get("title"),
            })

    genre_df = pd.DataFrame(genre_rows)

    if genre_df.empty:
        return pd.DataFrame()

    numeric_columns = [
        "brightness",
        "saturation",
        "color_diversity",
        "rating",
    ]

    for column in numeric_columns:
        genre_df[column] = pd.to_numeric(genre_df[column], errors="coerce")

    genre_average_df = genre_df.groupby(
        "genre",
        as_index=False,
    ).agg(
        movie_count=("title", "count"),
        average_brightness=("brightness", "mean"),
        average_saturation=("saturation", "mean"),
        average_color_diversity=("color_diversity", "mean"),
        average_rating=("rating", "mean"),
    )

    genre_average_df["average_brightness"] = genre_average_df["average_brightness"].round(2)
    genre_average_df["average_saturation"] = genre_average_df["average_saturation"].round(3)
    genre_average_df["average_color_diversity"] = genre_average_df["average_color_diversity"].round(3)
    genre_average_df["average_rating"] = genre_average_df["average_rating"].round(2)

    genre_average_df = genre_average_df.sort_values(
        by="movie_count",
        ascending=False,
    )

    return genre_average_df


def create_decade_summary_df(analysis_df: pd.DataFrame) -> pd.DataFrame:
    """
    Decade Trend Analysis용 DataFrame 생성.

    예:
    1994 -> 1990s
    2008 -> 2000s
    2025 -> 2020s
    """
    if analysis_df is None or analysis_df.empty:
        return pd.DataFrame()

    if "year" not in analysis_df.columns:
        return pd.DataFrame()

    df = analysis_df.copy()

    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df = df.dropna(subset=["year"])
    df["year"] = df["year"].astype(int)

    if df.empty:
        return pd.DataFrame()

    df["decade"] = (df["year"] // 10) * 10
    df["decade_label"] = df["decade"].astype(str) + "s"

    numeric_columns = [
        "brightness",
        "saturation",
        "color_diversity",
        "rating",
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    decade_summary_df = df.groupby(
        ["decade", "decade_label"],
        as_index=False,
    ).agg(
        movie_count=("title", "count"),
        average_brightness=("brightness", "mean"),
        average_saturation=("saturation", "mean"),
        average_color_diversity=("color_diversity", "mean"),
        average_rating=("rating", "mean"),
    )

    decade_summary_df["average_brightness"] = decade_summary_df["average_brightness"].round(2)
    decade_summary_df["average_saturation"] = decade_summary_df["average_saturation"].round(3)
    decade_summary_df["average_color_diversity"] = decade_summary_df["average_color_diversity"].round(3)
    decade_summary_df["average_rating"] = decade_summary_df["average_rating"].round(2)

    decade_summary_df = decade_summary_df.sort_values("decade")

    return decade_summary_df


def create_ranking_tables(
    analysis_df: pd.DataFrame,
    top_n: int = 5,
) -> Dict[str, pd.DataFrame]:
    """
    포스터 분석 결과 기반 ranking tables 생성.

    반환:
    - darkest
    - brightest
    - most_saturated
    - least_saturated
    - most_diverse
    - highest_rated
    """
    if analysis_df is None or analysis_df.empty:
        return {}

    df = analysis_df.copy()

    numeric_columns = [
        "brightness",
        "saturation",
        "color_diversity",
        "rating",
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    display_columns = [
        "title",
        "genres",
        "year",
        "rating",
        "dominant_color",
        "brightness",
        "saturation",
        "color_diversity",
        "color_mood",
    ]

    available_columns = [
        column for column in display_columns if column in df.columns
    ]

    rankings = {}

    if "brightness" in df.columns:
        rankings["darkest"] = (
            df.sort_values("brightness", ascending=True)
            .head(top_n)[available_columns]
        )

        rankings["brightest"] = (
            df.sort_values("brightness", ascending=False)
            .head(top_n)[available_columns]
        )

    if "saturation" in df.columns:
        rankings["most_saturated"] = (
            df.sort_values("saturation", ascending=False)
            .head(top_n)[available_columns]
        )

        rankings["least_saturated"] = (
            df.sort_values("saturation", ascending=True)
            .head(top_n)[available_columns]
        )

    if "color_diversity" in df.columns:
        rankings["most_diverse"] = (
            df.sort_values("color_diversity", ascending=False)
            .head(top_n)[available_columns]
        )

    if "rating" in df.columns:
        rankings["highest_rated"] = (
            df.sort_values("rating", ascending=False)
            .head(top_n)[available_columns]
        )

    return rankings


def create_color_mood_summary_df(analysis_df: pd.DataFrame) -> pd.DataFrame:
    """
    color_mood 분포 요약.

    예:
    Dark / Moody: 12
    Vivid / Energetic: 8
    Neutral / Minimal: 5
    """
    if analysis_df is None or analysis_df.empty:
        return pd.DataFrame()

    if "color_mood" not in analysis_df.columns:
        return pd.DataFrame()

    mood_summary = analysis_df["color_mood"].value_counts().reset_index()
    mood_summary.columns = ["color_mood", "movie_count"]

    return mood_summary


def create_decade_mood_summary_df(analysis_df: pd.DataFrame) -> pd.DataFrame:
    """
    decade별 color mood 분포 요약.

    Advanced Analysis에서 decade trend와 mood를 함께 보고 싶을 때 사용.
    """
    if analysis_df is None or analysis_df.empty:
        return pd.DataFrame()

    if "year" not in analysis_df.columns or "color_mood" not in analysis_df.columns:
        return pd.DataFrame()

    df = analysis_df.copy()

    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df = df.dropna(subset=["year"])
    df["year"] = df["year"].astype(int)

    df["decade"] = (df["year"] // 10) * 10
    df["decade_label"] = df["decade"].astype(str) + "s"

    decade_mood_df = df.groupby(
        ["decade_label", "color_mood"],
        as_index=False,
    ).agg(
        movie_count=("title", "count"),
    )

    return decade_mood_df