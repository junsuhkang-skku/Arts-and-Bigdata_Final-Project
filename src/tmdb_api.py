import os
import requests
import pandas as pd
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"


def get_genre_map(language: str = "en-US") -> dict:
    """
    TMDB 장르 ID를 장르 이름으로 변환하기 위한 딕셔너리 생성.
    예: {28: "Action", 35: "Comedy"}
    """
    url = f"{BASE_URL}/genre/movie/list"

    params = {
        "api_key": TMDB_API_KEY,
        "language": language,
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()
    genres = data.get("genres", [])

    return {genre["id"]: genre["name"] for genre in genres}


def get_popular_movies(page: int = 1, language: str = "en-US") -> list:
    """
    인기 영화 목록을 TMDB API에서 가져옴.
    """
    url = f"{BASE_URL}/movie/popular"

    params = {
        "api_key": TMDB_API_KEY,
        "language": language,
        "page": page,
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()
    return data.get("results", [])


def get_movies_by_genre(genre_id: int, page: int = 1, language: str = "en-US") -> list:
    """
    특정 장르의 영화 목록을 가져옴.
    """
    url = f"{BASE_URL}/discover/movie"

    params = {
        "api_key": TMDB_API_KEY,
        "language": language,
        "page": page,
        "sort_by": "popularity.desc",
        "include_adult": "false",
        "include_video": "false",
        "with_genres": genre_id,
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()
    return data.get("results", [])


def make_poster_url(poster_path: str) -> Optional[str]:
    """
    poster_path를 실제 포스터 이미지 URL로 변환.
    """
    if not poster_path:
        return None

    return f"{IMAGE_BASE_URL}{poster_path}"


def movies_to_dataframe(movies: list, genre_map: dict) -> pd.DataFrame:
    """
    TMDB API 응답 데이터를 Streamlit에서 쓰기 쉬운 DataFrame으로 변환.
    """
    rows = []

    for movie in movies:
        genre_ids = movie.get("genre_ids", [])
        genre_names = [genre_map.get(gid, "Unknown") for gid in genre_ids]

        release_date = movie.get("release_date", "")
        year = release_date[:4] if release_date else None

        rows.append({
            "tmdb_id": movie.get("id"),
            "title": movie.get("title"),
            "genres": ", ".join(genre_names),
            "year": year,
            "rating": movie.get("vote_average"),
            "popularity": movie.get("popularity"),
            "poster_path": movie.get("poster_path"),
            "poster_url": make_poster_url(movie.get("poster_path")),
            "overview": movie.get("overview"),
        })

    return pd.DataFrame(rows)


def fetch_popular_movies_dataframe(pages: int = 1) -> pd.DataFrame:
    """
    여러 페이지의 인기 영화를 가져와 하나의 DataFrame으로 반환.
    """
    if not TMDB_API_KEY:
        raise ValueError("TMDB_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")

    genre_map = get_genre_map()
    all_movies = []

    for page in range(1, pages + 1):
        movies = get_popular_movies(page=page)
        all_movies.extend(movies)

    return movies_to_dataframe(all_movies, genre_map)


def discover_movies_by_year_range(
    start_year: int,
    end_year: int,
    page: int = 1,
    language: str = "en-US",
) -> list:
    """
    연도 범위를 TMDB API 요청에 직접 넣어서 영화 목록을 가져옴.
    """
    url = f"{BASE_URL}/discover/movie"

    params = {
        "api_key": TMDB_API_KEY,
        "language": language,
        "page": page,
        "sort_by": "popularity.desc",
        "include_adult": "false",
        "include_video": "false",
        "primary_release_date.gte": f"{start_year}-01-01",
        "primary_release_date.lte": f"{end_year}-12-31",
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()
    return data.get("results", [])


def fetch_movies_by_year_range_dataframe(
    start_year: int,
    end_year: int,
    pages: int = 1,
) -> pd.DataFrame:
    """
    연도 범위 조건을 적용한 영화 데이터를 여러 페이지 가져와 DataFrame으로 변환.
    """
    if not TMDB_API_KEY:
        raise ValueError("TMDB_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")

    genre_map = get_genre_map()
    all_movies = []

    for page in range(1, pages + 1):
        movies = discover_movies_by_year_range(
            start_year=start_year,
            end_year=end_year,
            page=page,
        )
        all_movies.extend(movies)

    return movies_to_dataframe(all_movies, genre_map)