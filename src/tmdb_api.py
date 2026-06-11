import os
from typing import Optional, Dict, List, Any

import pandas as pd
import requests
from dotenv import load_dotenv

try:
    import streamlit as st
except ImportError:
    st = None


load_dotenv()

BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"


def get_api_key() -> Optional[str]:
    """
    TMDB API key를 가져오는 함수.

    로컬 실행:
    - .env 파일의 TMDB_API_KEY 사용

    Streamlit Cloud 실행:
    - st.secrets["TMDB_API_KEY"] 사용
    """
    api_key = os.getenv("TMDB_API_KEY")

    if api_key:
        return api_key

    if st is not None:
        try:
            return st.secrets.get("TMDB_API_KEY", None)
        except Exception:
            return None

    return None


def request_tmdb(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    TMDB API에 GET 요청을 보내고 JSON 응답을 반환.
    """
    api_key = get_api_key()

    if not api_key:
        raise ValueError(
            "TMDB_API_KEY가 설정되지 않았습니다. "
            "로컬에서는 .env 파일을, Streamlit Cloud에서는 Secrets를 확인하세요."
        )

    if params is None:
        params = {}

    params["api_key"] = api_key

    url = f"{BASE_URL}{endpoint}"

    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()

    return response.json()


def make_poster_url(poster_path: Optional[str]) -> Optional[str]:
    """
    TMDB poster_path를 실제 이미지 URL로 변환.
    """
    if not poster_path:
        return None

    return f"{IMAGE_BASE_URL}{poster_path}"


def get_genre_map(language: str = "en-US") -> Dict[int, str]:
    """
    TMDB 장르 ID를 장르 이름으로 변환하는 딕셔너리 생성.
    예: {28: "Action", 35: "Comedy"}
    """
    data = request_tmdb(
        endpoint="/genre/movie/list",
        params={"language": language},
    )

    genres = data.get("genres", [])

    return {genre["id"]: genre["name"] for genre in genres}


def movie_item_to_row(movie: Dict[str, Any], genre_map: Dict[int, str]) -> Dict[str, Any]:
    """
    TMDB movie list item을 DataFrame row 형태로 변환.
    """
    genre_ids = movie.get("genre_ids", [])
    genre_names = [genre_map.get(genre_id, "Unknown") for genre_id in genre_ids]

    release_date = movie.get("release_date") or ""
    year = release_date[:4] if release_date else None

    poster_path = movie.get("poster_path")

    return {
        "tmdb_id": movie.get("id"),
        "title": movie.get("title"),
        "genres": ", ".join(genre_names),
        "year": year,
        "release_date": release_date,
        "rating": movie.get("vote_average"),
        "vote_count": movie.get("vote_count"),
        "popularity": movie.get("popularity"),
        "overview": movie.get("overview"),
        "adult": movie.get("adult"),
        "poster_path": poster_path,
        "poster_url": make_poster_url(poster_path),
    }


def movie_detail_to_row(movie: Dict[str, Any]) -> Dict[str, Any]:
    """
    TMDB movie detail 응답을 DataFrame row 형태로 변환.
    Movie Title Search의 개별 상세 페이지에서 사용.
    """
    genres = movie.get("genres", [])
    genre_names = [genre.get("name", "Unknown") for genre in genres]

    release_date = movie.get("release_date") or ""
    year = release_date[:4] if release_date else None

    poster_path = movie.get("poster_path")

    return {
        "tmdb_id": movie.get("id"),
        "title": movie.get("title"),
        "genres": ", ".join(genre_names),
        "year": year,
        "release_date": release_date,
        "rating": movie.get("vote_average"),
        "vote_count": movie.get("vote_count"),
        "popularity": movie.get("popularity"),
        "overview": movie.get("overview"),
        "runtime": movie.get("runtime"),
        "status": movie.get("status"),
        "adult": movie.get("adult"),
        "poster_path": poster_path,
        "poster_url": make_poster_url(poster_path),
    }


def movies_to_dataframe(movies: List[Dict[str, Any]], genre_map: Dict[int, str]) -> pd.DataFrame:
    """
    TMDB 영화 목록 응답을 Pandas DataFrame으로 변환.
    """
    rows = []

    for movie in movies:
        rows.append(movie_item_to_row(movie, genre_map))

    df = pd.DataFrame(rows)

    if df.empty:
        return df

    df = df.drop_duplicates(subset=["tmdb_id"])
    df = filter_safe_movies_df(df)
    return df


def get_popular_movies(page: int = 1, language: str = "en-US") -> List[Dict[str, Any]]:
    """
    TMDB Popular Movies endpoint에서 인기 영화 목록을 가져옴.
    """
    data = request_tmdb(
        endpoint="/movie/popular",
        params={
            "language": language,
            "page": page,
            "include_adult": "false",
        },
    )

    return data.get("results", [])


def fetch_popular_movies_dataframe(
    pages: int = 1,
    language: str = "en-US",
) -> pd.DataFrame:
    """
    여러 페이지의 인기 영화를 가져와 DataFrame으로 반환.
    """
    genre_map = get_genre_map(language=language)
    all_movies = []

    for page in range(1, pages + 1):
        movies = get_popular_movies(page=page, language=language)
        all_movies.extend(movies)

    return movies_to_dataframe(all_movies, genre_map)


def discover_movies_by_year_range(
    start_year: int,
    end_year: int,
    page: int = 1,
    language: str = "en-US",
) -> List[Dict[str, Any]]:
    """
    연도 범위를 API 요청 단계에 직접 적용하여 영화 목록을 가져옴.
    """
    data = request_tmdb(
        endpoint="/discover/movie",
        params={
            "language": language,
            "page": page,
            "sort_by": "popularity.desc",
            "include_adult": "false",
            "include_video": "false",
            "primary_release_date.gte": f"{start_year}-01-01",
            "primary_release_date.lte": f"{end_year}-12-31",
        },
    )

    return data.get("results", [])


def fetch_movies_by_year_range_dataframe(
    start_year: int,
    end_year: int,
    pages: int = 1,
    language: str = "en-US",
) -> pd.DataFrame:
    """
    연도 범위 검색 결과를 여러 페이지 가져와 DataFrame으로 반환.
    """
    genre_map = get_genre_map(language=language)
    all_movies = []

    for page in range(1, pages + 1):
        movies = discover_movies_by_year_range(
            start_year=start_year,
            end_year=end_year,
            page=page,
            language=language,
        )
        all_movies.extend(movies)

    return movies_to_dataframe(all_movies, genre_map)


def search_movies_by_title(
    query: str,
    page: int = 1,
    language: str = "en-US",
) -> pd.DataFrame:
    """
    영화 제목으로 TMDB 검색.
    Movie Search 페이지에서 사용.

    예:
    query="Batman"
    """
    if not query or not query.strip():
        return pd.DataFrame()

    genre_map = get_genre_map(language=language)

    data = request_tmdb(
        endpoint="/search/movie",
        params={
            "language": language,
            "query": query.strip(),
            "page": page,
            "include_adult": "false",
        },
    )

    movies = data.get("results", [])

    return movies_to_dataframe(movies, genre_map)


def get_movie_detail(
    movie_id: int,
    language: str = "en-US",
) -> Dict[str, Any]:
    """
    TMDB movie_id를 이용해 영화 상세 정보 가져오기.
    """
    return request_tmdb(
        endpoint=f"/movie/{movie_id}",
        params={"language": language},
    )


def get_movie_detail_dataframe(
    movie_id: int,
    language: str = "en-US",
) -> pd.DataFrame:
    """
    영화 상세 정보를 DataFrame 1행으로 반환.
    성인/외설적 콘텐츠는 빈 DataFrame으로 반환.
    """
    detail = get_movie_detail(movie_id=movie_id, language=language)
    row = movie_detail_to_row(detail)

    df = pd.DataFrame([row])
    df = filter_safe_movies_df(df)

    return df

def filter_safe_movies_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    성인/외설적 영화가 검색 결과에 나오지 않도록 후처리 필터링.

    1. TMDB adult=True 제거
    2. 제목, overview, 장르에 포함된 위험 키워드 제거
    """
    if df is None or df.empty:
        return pd.DataFrame()

    safe_df = df.copy()

    # 1. TMDB adult flag 제거
    if "adult" in safe_df.columns:
        safe_df = safe_df[safe_df["adult"] != True]

    # 2. 키워드 기반 추가 필터
    blocked_keywords = [
        "sex",
        "sexual",
        "erotic",
        "erotica",
        "porn",
        "porno",
        "pornographic",
        "xxx",
        "adult",
        "nude",
        "nudity",
        "strip",
        "stripper",
        "prostitute",
        "brothel",
    ]

    text_columns = [
        column for column in ["title", "overview", "genres"]
        if column in safe_df.columns
    ]

    if text_columns:
        combined_text = safe_df[text_columns].fillna("").agg(
            " ".join,
            axis=1,
        ).str.lower()

        blocked_pattern = "|".join(blocked_keywords)

        safe_df = safe_df[
            ~combined_text.str.contains(
                blocked_pattern,
                case=False,
                na=False,
                regex=True,
            )
        ]

    return safe_df.reset_index(drop=True)