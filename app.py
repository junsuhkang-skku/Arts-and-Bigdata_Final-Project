import streamlit as st
import pandas as pd
import plotly.express as px

from src.tmdb_api import (
    fetch_popular_movies_dataframe,
    fetch_movies_by_year_range_dataframe,
)
from src.poster_fetcher import load_image_from_url
from src.color_analysis import analyze_poster

import streamlit.components.v1 as components


st.set_page_config(
    page_title="Movie Poster Color Palette Dashboard",
    page_icon="🎬",
    layout="wide",
)


@st.cache_data(show_spinner=False)
def load_movies(search_mode, pages, start_year, end_year):
    if search_mode == "Popular Movies":
        return fetch_popular_movies_dataframe(pages=pages)

    return fetch_movies_by_year_range_dataframe(
        start_year=start_year,
        end_year=end_year,
        pages=pages,
    )


@st.cache_data(show_spinner=False)
def analyze_poster_by_url(poster_url):
    image = load_image_from_url(poster_url)
    return analyze_poster(image)


def show_color_palette(colors):
    """
    HEX 색상 리스트를 Streamlit 컬럼 기반 컬러 팔레트 UI로 표시.
    HTML이 텍스트로 보이는 문제를 피하기 위한 방식.
    """
    if not colors:
        st.caption("No color data")
        return

    palette_cols = st.columns(len(colors))

    for col, color in zip(palette_cols, colors):
        with col:
            st.markdown(
                f"""
                <div style="
                    width: 100%;
                    height: 42px;
                    background-color: {color};
                    border-radius: 8px;
                    border: 1px solid #cccccc;
                    margin-bottom: 4px;">
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.caption(color)


def show_dominant_color(color):
    """
    대표 색상 1개를 크게 표시.
    """
    if not color:
        st.caption("No dominant color")
        return

    st.markdown(
        f"""
        <div style="
            width: 100%;
            height: 45px;
            background-color: {color};
            border-radius: 10px;
            border: 1px solid #cccccc;
            margin-bottom: 6px;">
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(f"Dominant Color: {color}")


# -----------------------------
# Sidebar Filters
# -----------------------------
with st.sidebar:
    st.header("Search Filters")

    search_mode = st.radio(
        "Search Mode",
        ["Popular Movies", "Year Range Search"],
    )

    pages = st.slider(
        "TMDB pages to load",
        min_value=1,
        max_value=10,
        value=1,
        help="1 page usually contains about 20 movies.",
    )

    year_range = st.slider(
        "Release Year Range",
        min_value=1950,
        max_value=2026,
        value=(2000, 2026),
        disabled=(search_mode == "Popular Movies"),
        help="Only used in Year Range Search mode.",
    )

    min_rating = st.slider(
        "Minimum Rating",
        min_value=0.0,
        max_value=10.0,
        value=0.0,
        step=0.5,
    )

    analyze_button = st.button("Analyze Filtered Movies")


# -----------------------------
# Load TMDB Data
# -----------------------------
try:
    df = load_movies(
        search_mode=search_mode,
        pages=pages,
        start_year=year_range[0],
        end_year=year_range[1],
    )

except Exception as e:
    st.error(f":Error occured while loading data{e}")
    st.stop()


df = df.dropna(subset=["poster_url"])
df = df.dropna(subset=["year"])

df["year"] = pd.to_numeric(df["year"], errors="coerce")
df = df.dropna(subset=["year"])
df["year"] = df["year"].astype(int)

if search_mode == "Popular Movies":
    df = df[df["rating"] >= min_rating]

else:
    df = df[
        (df["year"] >= year_range[0])
        & (df["year"] <= year_range[1])
        & (df["rating"] >= min_rating)
    ]


# -----------------------------
# Dataset Overview
# -----------------------------
st.subheader("Dataset Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Movies Found", len(df))
col2.metric("Average Rating", round(df["rating"].mean(), 2))
col3.metric("Average Popularity", round(df["popularity"].mean(), 2))
col4.metric("Poster Images", df["poster_url"].notna().sum())


st.subheader("Filtered Movie Data")

st.dataframe(
    df[["title", "genres", "year", "rating", "popularity", "poster_url"]],
    use_container_width=True,
)


# -----------------------------
# Analyze All Filtered Movies
# -----------------------------
st.subheader("Poster Color Analysis")

if search_mode == "Year Range Search":
    st.info(
        f"Current Search Mode: {search_mode} | "
        f"Year: {year_range[0]}-{year_range[1]} | "
        f"Pages: {pages} | "
        f"Minimum Rating: {min_rating}"
    )
else:
    st.info(
        f"Current Search Mode: {search_mode} | "
        f"Pages: {pages} | "
        f"Minimum Rating: {min_rating}"
    )

if not analyze_button:
    st.stop()


analysis_rows = []

progress_bar = st.progress(0)
status_text = st.empty()

total_movies = len(df)

for idx, (_, row) in enumerate(df.iterrows()):
    status_text.write(f"Analyzing {idx + 1} / {total_movies}: {row['title']}")

    result = analyze_poster_by_url(row["poster_url"])

    analysis_rows.append({
        "title": row["title"],
        "genres": row["genres"],
        "year": row["year"],
        "rating": row["rating"],
        "popularity": row["popularity"],
        "poster_url": row["poster_url"],
        "dominant_color": result["dominant_color"],
        "dominant_colors": result["dominant_colors"],
        "brightness": result["brightness"],
        "saturation": result["saturation"],
    })

    progress_bar.progress((idx + 1) / total_movies)

status_text.write("Analysis complete.")

analysis_df = pd.DataFrame(analysis_rows)

analysis_df = analysis_df.dropna(subset=["brightness", "saturation"])

if analysis_df.empty:
    st.warning("None posters to analysis.")
    st.stop()


# -----------------------------
# Analysis Table
# -----------------------------
st.subheader("Analysis Result Table")

table_df = analysis_df.copy()


def make_color_square(color):
    if not isinstance(color, str) or not color.startswith("#"):
        return ""

    return (
        f'<div style="display:flex; align-items:center; gap:8px;">'
        f'<div style="width:18px; height:18px; background-color:{color}; '
        f'border:1px solid #999; border-radius:4px;"></div>'
        f'<span>{color}</span>'
        f'</div>'
    )


def make_palette_squares(colors):
    if not isinstance(colors, list) or len(colors) == 0:
        return ""

    squares = ""

    for color in colors:
        if isinstance(color, str) and color.startswith("#"):
            squares += (
                f'<div title="{color}" style="width:16px; height:16px; '
                f'background-color:{color}; border:1px solid #999; '
                f'border-radius:3px;"></div>'
            )

    return f'<div style="display:flex; align-items:center; gap:4px;">{squares}</div>'


html_df = table_df[
    [
        "title",
        "genres",
        "year",
        "rating",
        "dominant_color",
        "dominant_colors",
        "brightness",
        "saturation",
    ]
].copy()

html_df["dominant_color"] = html_df["dominant_color"].apply(make_color_square)
html_df["dominant_colors"] = html_df["dominant_colors"].apply(make_palette_squares)

html_df = html_df.rename(
    columns={
        "title": "Title",
        "genres": "Genres",
        "year": "Year",
        "rating": "Rating",
        "dominant_color": "Dominant Color",
        "dominant_colors": "Color Palette",
        "brightness": "Brightness",
        "saturation": "Saturation",
    }
)

table_html = html_df.to_html(
    escape=False,
    index=False,
    border=0,
)

st.markdown(
    f"""
    <style>
    table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 14px;
    }}
    th {{
        background-color: #f5f5f5;
        text-align: left;
        padding: 8px;
        border-bottom: 1px solid #ddd;
    }}
    td {{
        padding: 8px;
        border-bottom: 1px solid #eee;
        vertical-align: middle;
    }}
    </style>

    <div style="overflow-x:auto;">
        {table_html}
    </div>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# Charts
# -----------------------------
st.subheader("Brightness by Movie")

fig_brightness = px.bar(
    analysis_df,
    x="title",
    y="brightness",
    color="brightness",
    title="Poster Brightness by Movie",
)

st.plotly_chart(fig_brightness, use_container_width=True)


st.subheader("Saturation by Movie")

fig_saturation = px.bar(
    analysis_df,
    x="title",
    y="saturation",
    color="saturation",
    title="Poster Saturation by Movie",
)

st.plotly_chart(fig_saturation, use_container_width=True)


# -----------------------------
# Genre-based Analysis
# -----------------------------
st.subheader("Genre-based Average Color Features")

genre_rows = []

for _, row in analysis_df.iterrows():
    genre_list = [g.strip() for g in row["genres"].split(",")]

    for genre in genre_list:
        if genre and genre != "Unknown":
            genre_rows.append({
                "genre": genre,
                "brightness": row["brightness"],
                "saturation": row["saturation"],
            })

genre_df = pd.DataFrame(genre_rows)

if not genre_df.empty:
    genre_avg = genre_df.groupby("genre", as_index=False).agg({
        "brightness": "mean",
        "saturation": "mean",
    })

    genre_avg["brightness"] = genre_avg["brightness"].round(2)
    genre_avg["saturation"] = genre_avg["saturation"].round(3)

    fig_genre_brightness = px.bar(
        genre_avg,
        x="genre",
        y="brightness",
        color="brightness",
        title="Average Brightness by Genre",
    )

    st.plotly_chart(fig_genre_brightness, use_container_width=True)

    fig_genre_saturation = px.bar(
        genre_avg,
        x="genre",
        y="saturation",
        color="saturation",
        title="Average Saturation by Genre",
    )

    st.plotly_chart(fig_genre_saturation, use_container_width=True)

    st.dataframe(genre_avg, use_container_width=True)


# -----------------------------
# Poster Gallery with Palette
# -----------------------------
st.subheader("Poster Gallery with Color Palette")

gallery_cols = st.columns(4)

for index, row in analysis_df.iterrows():
    with gallery_cols[index % 4]:
        st.image(row["poster_url"], use_container_width=True)

        st.markdown(f"**{row['title']}**")
        st.caption(f"{row['year']} | Rating: {row['rating']}")

        show_dominant_color(row["dominant_color"])

        st.write("Color Palette")
        show_color_palette(row["dominant_colors"])

        st.write(f"Brightness: {row['brightness']}")
        st.write(f"Saturation: {row['saturation']}")
        st.divider()
