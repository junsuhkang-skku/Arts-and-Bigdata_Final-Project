from typing import List, Optional

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from src.poster_fetcher import get_image_bytes_from_url, create_safe_filename


def show_dominant_color(color: Optional[str], height: int = 42) -> None:
    """
    dominant color를 색상 박스와 HEX 코드로 표시.
    """
    if not color or not isinstance(color, str):
        st.caption("No dominant color")
        return

    st.markdown(
        f"""
        <div style="
            width: 100%;
            height: {height}px;
            background-color: {color};
            border-radius: 8px;
            border: 1px solid #aaaaaa;
            margin-bottom: 4px;">
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(f"Dominant Color: {color}")


def show_color_palette(colors: List[str]) -> None:
    """
    color palette를 Streamlit columns 기반으로 표시.
    """
    if not colors or not isinstance(colors, list):
        st.caption("No color palette")
        return

    palette_cols = st.columns(len(colors))

    for col, color in zip(palette_cols, colors):
        with col:
            st.markdown(
                f"""
                <div style="
                    width: 100%;
                    height: 36px;
                    background-color: {color};
                    border-radius: 7px;
                    border: 1px solid #aaaaaa;
                    margin-bottom: 3px;">
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.caption(color)


def render_metric_overview(summary: dict) -> None:
    """
    Dataset Overview metric cards 표시.
    """
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Movies Found", summary.get("movies_found", 0))
    col2.metric("Average Rating", summary.get("average_rating", 0))
    col3.metric("Average Popularity", summary.get("average_popularity", 0))
    col4.metric("Poster Images", summary.get("poster_images", 0))

    col5, col6 = st.columns(2)
    col5.metric("Average Brightness", summary.get("average_brightness", 0))
    col6.metric("Average Saturation", summary.get("average_saturation", 0))


def make_color_square_html(color: Optional[str]) -> str:
    """
    테이블 안에서 dominant color를 작은 정사각형 + HEX 코드로 표시하기 위한 HTML.
    """
    if not color or not isinstance(color, str) or not color.startswith("#"):
        return ""

    return (
        f'<div class="color-cell">'
        f'<div class="color-box" style="background-color:{color};"></div>'
        f'<span>{color}</span>'
        f'</div>'
    )


def make_palette_squares_html(colors: List[str]) -> str:
    """
    테이블 안에서 color palette를 작은 정사각형들로 표시하기 위한 HTML.
    """
    if not colors or not isinstance(colors, list):
        return ""

    squares = ""

    for color in colors:
        if isinstance(color, str) and color.startswith("#"):
            squares += (
                f'<div class="palette-box" '
                f'title="{color}" '
                f'style="background-color:{color};"></div>'
            )

    return f'<div class="palette-cell">{squares}</div>'


def render_result_table(analysis_df: pd.DataFrame, height: int = 620) -> None:
    """
    분석 결과 테이블 표시.

    st.dataframe에 HTML을 넣으면 깨질 수 있으므로
    components.html을 사용해 직접 렌더링.
    """
    if analysis_df is None or analysis_df.empty:
        st.warning("No analysis result available.")
        return

    required_columns = [
        "title",
        "genres",
        "year",
        "rating",
        "dominant_color",
        "dominant_colors",
        "brightness",
        "saturation",
        "color_diversity",
        "color_mood",
    ]

    available_columns = [
        column for column in required_columns if column in analysis_df.columns
    ]

    table_df = analysis_df[available_columns].copy()

    if "dominant_color" in table_df.columns:
        table_df["dominant_color"] = table_df["dominant_color"].apply(
            make_color_square_html
        )

    if "dominant_colors" in table_df.columns:
        table_df["dominant_colors"] = table_df["dominant_colors"].apply(
            make_palette_squares_html
        )

    rename_map = {
        "title": "Title",
        "genres": "Genres",
        "year": "Year",
        "rating": "Rating",
        "dominant_color": "Dominant Color",
        "dominant_colors": "Color Palette",
        "brightness": "Brightness",
        "saturation": "Saturation",
        "color_diversity": "Color Diversity",
        "color_mood": "Color Mood",
    }

    table_df = table_df.rename(columns=rename_map)

    table_html = table_df.to_html(
        escape=False,
        index=False,
        border=0,
        classes="color-result-table",
    )

    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    body {{
        margin: 0;
        padding: 0;
        background-color: transparent;
        font-family: Arial, sans-serif;
    }}

    .table-wrapper {{
        width: 100%;
        overflow-x: auto;
    }}

    .color-result-table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 14px;
        color: #f5f5f5;
    }}

    .color-result-table th {{
        background-color: #262b33;
        color: #ffffff;
        text-align: left;
        padding: 10px;
        border-bottom: 1px solid #444;
        white-space: nowrap;
    }}

    .color-result-table td {{
        padding: 10px;
        border-bottom: 1px solid #333;
        vertical-align: middle;
    }}

    .color-result-table tr:nth-child(even) {{
        background-color: #161a20;
    }}

    .color-result-table tr:nth-child(odd) {{
        background-color: #101318;
    }}

    .color-cell {{
        display: flex;
        align-items: center;
        gap: 8px;
        white-space: nowrap;
    }}

    .color-box {{
        width: 22px;
        height: 22px;
        border: 1px solid #aaaaaa;
        border-radius: 5px;
        flex-shrink: 0;
    }}

    .palette-cell {{
        display: flex;
        align-items: center;
        gap: 5px;
        min-width: 120px;
    }}

    .palette-box {{
        width: 20px;
        height: 20px;
        border: 1px solid #aaaaaa;
        border-radius: 4px;
        flex-shrink: 0;
    }}
    </style>
    </head>

    <body>
        <div class="table-wrapper">
            {table_html}
        </div>
    </body>
    </html>
    """

    components.html(
        full_html,
        height=height,
        scrolling=True,
    )


def render_movie_gallery(
    analysis_df: pd.DataFrame,
    columns: int = 3,
    enable_cart: bool = False,
    enable_download: bool = True,
) -> None:
    """
    Poster Gallery with Palette 표시.

    enable_cart=True이면 각 카드에 Add to Cart 버튼 표시.
    enable_download=True이면 각 카드에 Poster Download 버튼 표시.
    """
    if analysis_df is None or analysis_df.empty:
        st.warning("No poster gallery available.")
        return

    if enable_cart:
        from src.cart_utils import add_to_cart_flag, is_in_cart

    gallery_cols = st.columns(columns)

    for index, row in analysis_df.reset_index(drop=True).iterrows():
        movie_data = row.to_dict()

        with gallery_cols[index % columns]:
            with st.container(border=True):
                poster_url = row.get("poster_url")
                title = row.get("title", "Unknown Title")
                year = row.get("year", "Unknown")
                rating = row.get("rating", "N/A")
                color_mood = row.get("color_mood", "Unknown")
                tmdb_id = row.get("tmdb_id")

                if poster_url:
                    st.markdown(
                        f"""
                        <div style="
                            width: 100%;
                            height: 420px;
                            overflow: hidden;
                            border-radius: 10px;
                            margin-bottom: 12px;
                            background-color: #111;">
                            <img src="{poster_url}" style="
                                width: 100%;
                                height: 100%;
                                object-fit: contain;">
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                st.markdown(f"### {title}")
                st.caption(f"{year} | Rating: {rating}")
                st.caption(f"Mood: {color_mood}")

                st.markdown("**Dominant Color**")
                show_dominant_color(row.get("dominant_color"))

                st.markdown("**Color Palette**")
                show_color_palette(row.get("dominant_colors", []))

                metric_col1, metric_col2 = st.columns(2)

                with metric_col1:
                    st.metric("Brightness", row.get("brightness", 0))

                with metric_col2:
                    st.metric("Saturation", row.get("saturation", 0))

                if "color_diversity" in row:
                    st.metric("Color Diversity", row.get("color_diversity", 0))

                button_col1, button_col2 = st.columns(2)

                with button_col1:
                    if enable_download and poster_url:
                        image_bytes = get_image_bytes_from_url(poster_url)

                        if image_bytes:
                            filename = create_safe_filename(title)

                            st.download_button(
                                label="Download",
                                data=image_bytes,
                                file_name=filename,
                                mime="image/jpeg",
                                key=f"download_{tmdb_id}_{index}",
                            )
                        else:
                            st.button(
                                "Download",
                                disabled=True,
                                key=f"download_disabled_{tmdb_id}_{index}",
                            )

                with button_col2:
                    if enable_cart:
                        if is_in_cart(tmdb_id):
                            st.button(
                                "In Cart",
                                disabled=True,
                                key=f"gallery_added_{tmdb_id}_{index}",
                            )
                        else:
                            if st.button(
                                "Add Cart",
                                key=f"gallery_cart_{tmdb_id}_{index}",
                            ):
                                added = add_to_cart_flag(movie_data)

                                if added:
                                    st.success("Added to cart.")
                                else:
                                    st.warning("Could not add this poster.")


def render_single_movie_detail(movie_data: dict) -> None:
    """
    Movie Search에서 선택한 영화 1개 상세 정보 표시.
    movie_data는 분석 결과가 포함된 dict.
    """
    if not movie_data:
        st.warning("No movie detail available.")
        return

    left_col, right_col = st.columns([1, 2])

    with left_col:
        poster_url = movie_data.get("poster_url")

        if poster_url:
            st.image(poster_url, use_container_width=True)

    with right_col:
        st.subheader(movie_data.get("title", "Unknown Title"))

        st.write(f"**Year:** {movie_data.get('year', 'Unknown')}")
        st.write(f"**Genres:** {movie_data.get('genres', 'Unknown')}")
        st.write(f"**Rating:** {movie_data.get('rating', 'N/A')}")
        st.write(f"**Popularity:** {movie_data.get('popularity', 'N/A')}")

        runtime = movie_data.get("runtime")
        if runtime:
            st.write(f"**Runtime:** {runtime} minutes")

        status = movie_data.get("status")
        if status:
            st.write(f"**Status:** {status}")

        overview = movie_data.get("overview")
        if overview:
            st.write("**Overview:**")
            st.write(overview)

        st.markdown("**Dominant Color**")
        show_dominant_color(movie_data.get("dominant_color"))

        st.markdown("**Color Palette**")
        show_color_palette(movie_data.get("dominant_colors", []))

        metric_col1, metric_col2, metric_col3 = st.columns(3)

        with metric_col1:
            st.metric("Brightness", movie_data.get("brightness", 0))

        with metric_col2:
            st.metric("Saturation", movie_data.get("saturation", 0))

        with metric_col3:
            st.metric("Diversity", movie_data.get("color_diversity", 0))

        st.write(f"**Color Mood:** {movie_data.get('color_mood', 'Unknown')}")