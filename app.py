import streamlit as st
import pandas as pd
import plotly.express as px

from src.tmdb_api import (
    fetch_popular_movies_dataframe,
    fetch_movies_by_year_range_dataframe,
)
from src.poster_fetcher import load_image_from_url
from src.color_analysis import analyze_poster


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

table_df["color_palette"] = table_df["dominant_colors"].apply(
    lambda colors: " / ".join(colors) if isinstance(colors, list) else ""
)

result_table = table_df[
    [
        "title",
        "genres",
        "year",
        "rating",
        "dominant_color",
        "color_palette",
        "brightness",
        "saturation",
    ]
]


def color_square_style(value):
    """
    dominant_color 컬럼의 배경색을 실제 색상으로 표시.
    """
    if isinstance(value, str) and value.startswith("#"):
        return (
            f"background-color: {value}; "
            "color: white; "
            "font-weight: bold; "
            "text-align: center;"
        )
    return ""


styled_result_table = result_table.style.applymap(
    color_square_style,
    subset=["dominant_color"],
)

st.dataframe(
    styled_result_table,
    use_container_width=True,
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