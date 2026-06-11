import streamlit as st
import pandas as pd
import plotly.express as px

from src.tmdb_api import (
    fetch_popular_movies_dataframe,
    fetch_movies_by_year_range_dataframe,
    search_movies_by_title,
    get_movie_detail_dataframe,
)

from src.analysis_pipeline import (
    analyze_movie_dataframe,
    analyze_single_movie_dataframe,
    filter_movie_dataframe,
    get_analysis_summary,
)

from src.ui_components import (
    render_metric_overview,
    render_result_table,
    render_movie_gallery,
    render_single_movie_detail,
    show_dominant_color,
    show_color_palette,
)

from src.advanced_analysis import (
    create_genre_average_df,
    create_decade_summary_df,
    create_ranking_tables,
    create_color_mood_summary_df,
)

from src.cart_utils import (
    init_cart,
    add_to_cart_flag,
    remove_from_cart,
    clear_cart,
    get_cart_count,
    is_in_cart,
    build_cart_dataframe_from_flags,
    get_cart_items_for_download,
)

from src.download_utils import (
    prepare_analysis_download_df,
    convert_df_to_csv,
    create_poster_zip,
    create_cart_info_csv,
)

from src.poster_fetcher import (
    get_image_bytes_from_url,
    create_safe_filename,
)

from src.game_utils import (
    init_game_state,
    start_new_question,
    submit_game_answer,
    reset_game_state,
)

@st.fragment
def dashboard_gallery_fragment(analysis_df):
    st.subheader("Poster Gallery with Palette")
    render_movie_gallery(
        analysis_df,
        columns=3,
        enable_cart=True,
        enable_download=False,
    )

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="Movie Poster Color Palette Dashboard",
    page_icon="🎬",
    layout="wide",
)


# -----------------------------
# Session State Init
# -----------------------------
init_cart()
init_game_state(st.session_state)

if "analysis_df" not in st.session_state:
    st.session_state["analysis_df"] = pd.DataFrame()

if "last_movie_df" not in st.session_state:
    st.session_state["last_movie_df"] = pd.DataFrame()

if "selected_movie_detail" not in st.session_state:
    st.session_state["selected_movie_detail"] = None


# -----------------------------
# Cached API / Analysis Functions
# -----------------------------
@st.cache_data(show_spinner=False)
def load_popular_movies(pages):
    return fetch_popular_movies_dataframe(pages=pages)


@st.cache_data(show_spinner=False)
def load_movies_by_year_range(start_year, end_year, pages):
    return fetch_movies_by_year_range_dataframe(
        start_year=start_year,
        end_year=end_year,
        pages=pages,
    )


@st.cache_data(show_spinner=False)
def cached_search_movies_by_title(query):
    return search_movies_by_title(query=query)


@st.cache_data(show_spinner=False)
def cached_get_movie_detail_dataframe(movie_id):
    return get_movie_detail_dataframe(movie_id=movie_id)

# -----------------------------
# Sidebar Navigation
# -----------------------------
st.sidebar.title("🎬 Movie Poster Lab")

cart_count = get_cart_count()

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Movie Search",
        f"Cart ({cart_count})",
        "Game Zone",
        "Advanced Analysis",
    ],
)

st.sidebar.divider()
st.sidebar.caption("Movie Poster Color Palette Analysis Dashboard")


# -----------------------------
# Helper
# -----------------------------
def get_current_analysis_df():
    analysis_df = st.session_state.get("analysis_df", pd.DataFrame())

    if analysis_df is None:
        return pd.DataFrame()

    return analysis_df


def save_analysis_df(analysis_df):
    st.session_state["analysis_df"] = analysis_df


# -----------------------------
# Dashboard Page
# -----------------------------
if page == "Dashboard":
    st.title("🎬 Movie Poster Color Palette Analysis Dashboard")

    st.write(
        """
        This dashboard uses the TMDB API to collect movie poster data and analyze
        dominant color, color palette, brightness, saturation, color diversity, and color mood.
        """
    )

    st.subheader("Search Filters")

    with st.sidebar:
        st.header("Dashboard Filters")

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
        )

        min_rating = st.slider(
            "Minimum Rating",
            min_value=0.0,
            max_value=10.0,
            value=0.0,
            step=0.5,
        )

        analyze_button = st.button("Analyze Filtered Movies")

        clear_analysis_button = st.button("Clear Current Analysis")

        if clear_analysis_button:
            st.session_state["analysis_df"] = pd.DataFrame()
            st.success("Current analysis cleared.")
            st.rerun()

    try:
        if search_mode == "Popular Movies":
            movie_df = load_popular_movies(pages=pages)
            filtered_df = filter_movie_dataframe(
                movie_df=movie_df,
                min_rating=min_rating,
            )

        else:
            movie_df = load_movies_by_year_range(
                start_year=year_range[0],
                end_year=year_range[1],
                pages=pages,
            )
            filtered_df = filter_movie_dataframe(
                movie_df=movie_df,
                min_rating=min_rating,
                start_year=year_range[0],
                end_year=year_range[1],
            )

    except Exception as e:
        st.error(f"Failed to load movie data: {e}")
        st.stop()

    st.session_state["last_movie_df"] = filtered_df

    if filtered_df.empty:
        st.warning("No movies found with the selected filters.")
        st.stop()

    st.info(
        f"Current Mode: {search_mode} | "
        f"Movies Found Before Analysis: {len(filtered_df)} | "
        f"Minimum Rating: {min_rating}"
    )

    st.subheader("Filtered Movie Data")

    preview_columns = [
        "title",
        "genres",
        "year",
        "rating",
        "popularity",
        "poster_url",
    ]

    available_preview_columns = [
        column for column in preview_columns if column in filtered_df.columns
    ]

    st.dataframe(
        filtered_df[available_preview_columns],
        use_container_width=True,
    )

    if analyze_button:
        st.subheader("Poster Color Analysis")

        progress_bar = st.progress(0)
        status_text = st.empty()

        analysis_rows = []
        total_movies = len(filtered_df)

        for idx, (_, row) in enumerate(filtered_df.iterrows()):
            status_text.write(
                f"Analyzing {idx + 1} / {total_movies}: {row.get('title')}"
            )

            single_df = pd.DataFrame([row.to_dict()])
            analyzed_single = analyze_single_movie_dataframe(single_df)

            if not analyzed_single.empty:
                analysis_rows.append(analyzed_single.iloc[0].to_dict())

            progress_bar.progress((idx + 1) / total_movies)

        analysis_df = pd.DataFrame(analysis_rows)

        if analysis_df.empty:
            st.warning("No posters could be analyzed.")
            st.stop()

        save_analysis_df(analysis_df)
        reset_game_state(st.session_state)

        status_text.write("Analysis complete.")
        st.success(f"Analyzed {len(analysis_df)} posters successfully.")

    analysis_df = get_current_analysis_df()

    if analysis_df.empty:
        st.warning("No analysis data yet. Click 'Analyze Filtered Movies' to start.")
        st.stop()

    # Dataset Overview
    st.subheader("Dataset Overview")
    summary = get_analysis_summary(analysis_df)
    render_metric_overview(summary)

    # Result Table
    st.subheader("Analysis Result Table")
    render_result_table(analysis_df)

    # CSV Download
    st.subheader("Download Analysis Data")

    download_df = prepare_analysis_download_df(analysis_df)
    csv_data = convert_df_to_csv(download_df)

    st.download_button(
        label="Download Analysis Result as CSV",
        data=csv_data,
        file_name="movie_poster_color_analysis.csv",
        mime="text/csv",
    )

    # Charts
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

    # Genre Analysis
    st.subheader("Genre-Based Average Color Feature")

    genre_df = create_genre_average_df(analysis_df)

    if genre_df.empty:
        st.warning("No genre analysis available.")
    else:
        st.dataframe(genre_df, use_container_width=True)

        fig_genre_brightness = px.bar(
            genre_df,
            x="genre",
            y="average_brightness",
            color="average_brightness",
            title="Average Brightness by Genre",
        )

        st.plotly_chart(fig_genre_brightness, use_container_width=True)

        fig_genre_saturation = px.bar(
            genre_df,
            x="genre",
            y="average_saturation",
            color="average_saturation",
            title="Average Saturation by Genre",
        )

        st.plotly_chart(fig_genre_saturation, use_container_width=True)

    dashboard_gallery_fragment(analysis_df)

# -----------------------------
# Movie Search Page
# -----------------------------
elif page == "Movie Search":
    st.title("🔎 Movie Title Search")

    st.write(
        """
        Search a movie by title, select one result, and analyze its poster individually.
        """
    )

    query = st.text_input(
        "Enter movie title",
        placeholder="Example: Batman, Avatar, The Matrix",
    )

    search_button = st.button("Search Movie")

    if search_button and query:
        try:
            search_df = cached_search_movies_by_title(query)
            st.session_state["movie_search_results"] = search_df

        except Exception as e:
            st.error(f"Failed to search movies: {e}")
            st.stop()

    search_results = st.session_state.get("movie_search_results", pd.DataFrame())

    if search_results is not None and not search_results.empty:
        st.subheader("Search Results")

        display_df = search_results[
            [
                column for column in [
                    "tmdb_id",
                    "title",
                    "genres",
                    "year",
                    "rating",
                    "popularity",
                ]
                if column in search_results.columns
            ]
        ]

        st.dataframe(display_df, use_container_width=True)

        options = []

        for _, row in search_results.iterrows():
            title = row.get("title", "Unknown Title")
            year = row.get("year", "Unknown")
            tmdb_id = row.get("tmdb_id")
            options.append((f"{title} ({year}) - ID: {tmdb_id}", tmdb_id))

        selected_label = st.selectbox(
            "Select a movie to analyze",
            [option[0] for option in options],
        )

        selected_movie_id = None

        for label, movie_id in options:
            if label == selected_label:
                selected_movie_id = movie_id
                break

        if st.button("Analyze Selected Movie"):
            try:
                detail_df = cached_get_movie_detail_dataframe(selected_movie_id)
                analyzed_detail_df = analyze_single_movie_dataframe(detail_df)

                if analyzed_detail_df.empty:
                    st.warning("Could not analyze selected movie poster.")
                else:
                    st.session_state["selected_movie_detail"] = (
                        analyzed_detail_df.iloc[0].to_dict()
                    )

            except Exception as e:
                st.error(f"Failed to analyze selected movie: {e}")

    selected_movie_detail = st.session_state.get("selected_movie_detail")

    if selected_movie_detail:
        st.subheader("Movie Detail Analysis")

        render_single_movie_detail(selected_movie_detail)

        col1, col2 = st.columns(2)

        with col1:
            poster_url = selected_movie_detail.get("poster_url")
            title = selected_movie_detail.get("title", "poster")

            if poster_url:
                image_bytes = get_image_bytes_from_url(poster_url)
                filename = create_safe_filename(title)

                if image_bytes:
                    st.download_button(
                        label="Download Poster Image",
                        data=image_bytes,
                        file_name=filename,
                        mime="image/jpeg",
                    )

        with col2:
            tmdb_id = selected_movie_detail.get("tmdb_id")

            if is_in_cart(tmdb_id):
                st.button("Already in Cart", disabled=True)
            else:
                if st.button("Add This Poster to Cart"):
                    added = add_to_cart_flag(selected_movie_detail)

                    if added:
                        st.success("Added to cart.")
                    else:
                        st.warning("This poster is already in cart or invalid.")


# -----------------------------
# Cart Page
# -----------------------------
elif page.startswith("Cart"):
    st.title("🛒 Poster Cart")

    analysis_df = get_current_analysis_df()

    cart_df = build_cart_dataframe_from_flags(analysis_df)

    if cart_df.empty:
        st.info("Your cart is empty. Add posters from Dashboard Gallery or Movie Search.")
        st.stop()

    cart_items = cart_df.to_dict("records")

    st.subheader("Cart Gallery")

    render_movie_gallery(
        cart_df,
        columns=3,
        enable_cart=False,
        enable_download=True,
    )

    with st.expander("View Cart Data Table"):
        render_result_table(cart_df, height=500)

    st.subheader("Cart Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        cart_csv = create_cart_info_csv(cart_items)

        st.download_button(
            label="Download Cart Info CSV",
            data=cart_csv,
            file_name="cart_poster_info.csv",
            mime="text/csv",
        )

    with col2:
        if st.button("Prepare Poster ZIP"):
            with st.spinner("Creating ZIP file..."):
                zip_data = create_poster_zip(cart_items)

            if zip_data:
                st.session_state["cart_zip_data"] = zip_data
                st.success("ZIP file is ready.")
            else:
                st.warning("Could not create ZIP file.")

        zip_data = st.session_state.get("cart_zip_data")

        if zip_data:
            st.download_button(
                label="Download All Posters as ZIP",
                data=zip_data,
                file_name="cart_posters.zip",
                mime="application/zip",
            )

    with col3:
        if st.button("Clear Cart"):
            clear_cart()
            st.success("Cart cleared.")
            st.rerun()

    st.subheader("Remove Item")

    remove_options = []

    for item in cart_items:
        label = f"{item.get('title')} ({item.get('year')})"
        remove_options.append((label, item.get("tmdb_id")))

    selected_remove_label = st.selectbox(
        "Select item to remove",
        [option[0] for option in remove_options],
    )

    selected_remove_id = None

    for label, tmdb_id in remove_options:
        if label == selected_remove_label:
            selected_remove_id = tmdb_id
            break

    if st.button("Remove Selected Item"):
        removed = remove_from_cart(selected_remove_id)

        if removed:
            st.success("Item removed.")
            st.rerun()
        else:
            st.warning("Could not remove item.")


# -----------------------------
# Game Zone Page
# -----------------------------
elif page == "Game Zone":
    st.title("🎮 Dominant Color Challenge")

    st.write(
        """
        Guess the dominant color of a randomly selected analyzed poster.
        If your color similarity is 80% or higher, it counts as success.
        """
    )

    analysis_df = get_current_analysis_df()

    if analysis_df.empty:
        st.warning("Please analyze posters in the Dashboard first.")
        st.stop()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Score", st.session_state["game_score"])

    with col2:
        st.metric("Total Attempts", st.session_state["game_total"])

    with col3:
        if st.session_state["game_total"] > 0:
            success_rate = (
                st.session_state["game_score"]
                / st.session_state["game_total"]
                * 100
            )
        else:
            success_rate = 0

        st.metric("Success Rate", f"{success_rate:.1f}%")

    game_col1, game_col2 = st.columns([1, 1])

    with game_col1:
        has_current_movie = st.session_state.get("game_movie") is not None
        answer_submitted = st.session_state.get("game_answer_submitted", False)

        if not has_current_movie:
            if st.button("Start Game"):
                success = start_new_question(st.session_state, analysis_df)

                if not success:
                    st.warning("No valid analyzed poster available.")
                else:
                    st.rerun()
        else:
            if st.button("Next Question", disabled=not answer_submitted):
                success = start_new_question(st.session_state, analysis_df)

                if not success:
                    st.warning("All analyzed posters have already appeared. Reset the game to play again.")
                else:
                    st.rerun()

            if not answer_submitted:
                st.caption("Submit your answer before moving to the next poster.")

        if st.button("Reset Game"):
            reset_game_state(st.session_state)
            st.rerun()

    game_movie = st.session_state.get("game_movie")

    if not game_movie:
        st.info("Click 'Start / Next Question' to begin.")
        st.stop()

    with game_col1:
        st.image(game_movie.get("poster_url"), use_container_width=True)
        st.caption(f"Movie: {game_movie.get('title')}")

    with game_col2:
        st.subheader("Choose the dominant color")

        user_color = st.color_picker(
            "Your color guess",
            value=st.session_state.get("game_user_color", "#000000"),
        )

        show_dominant_color(user_color)

        if st.button("Submit Answer"):
            result = submit_game_answer(
                st.session_state,
                user_color=user_color,
                success_threshold=80.0,
            )

            if result is None:
                st.warning("Could not evaluate your answer.")
            else:
                st.rerun()

        last_result = st.session_state.get("game_last_result")

        if last_result:
            answer_color = game_movie.get("dominant_color")
            user_selected_color = st.session_state.get("game_user_color")

            similarity = last_result["similarity"]
            label = last_result["feedback_label"]

            if last_result["is_success"]:
                st.success(f"{label}! Similarity: {similarity}%")
            elif similarity >= 65:
                st.warning(f"{label}! Similarity: {similarity}%")
            else:
                st.error(f"{label}! Similarity: {similarity}%")

            compare_col1, compare_col2 = st.columns(2)

            with compare_col1:
                st.markdown("**Your Color**")
                show_dominant_color(user_selected_color)

            with compare_col2:
                st.markdown("**Answer Color**")
                show_dominant_color(answer_color)


# -----------------------------
# Advanced Analysis Page
# -----------------------------
elif page == "Advanced Analysis":
    st.title("📊 Advanced Analysis")

    analysis_df = get_current_analysis_df()

    if analysis_df.empty:
        st.warning("Please analyze posters in the Dashboard first.")
        st.stop()

    st.subheader("Decade Trend Analysis")

    decade_df = create_decade_summary_df(analysis_df)

    if decade_df.empty:
        st.warning("No decade data available.")
    else:
        st.dataframe(decade_df, use_container_width=True)

        fig_decade_brightness = px.line(
            decade_df,
            x="decade_label",
            y="average_brightness",
            markers=True,
            title="Average Brightness by Decade",
        )

        st.plotly_chart(fig_decade_brightness, use_container_width=True)

        fig_decade_saturation = px.line(
            decade_df,
            x="decade_label",
            y="average_saturation",
            markers=True,
            title="Average Saturation by Decade",
        )

        st.plotly_chart(fig_decade_saturation, use_container_width=True)

        fig_decade_diversity = px.line(
            decade_df,
            x="decade_label",
            y="average_color_diversity",
            markers=True,
            title="Average Color Diversity by Decade",
        )

        st.plotly_chart(fig_decade_diversity, use_container_width=True)

    st.subheader("Color Mood Distribution")

    mood_df = create_color_mood_summary_df(analysis_df)

    if mood_df.empty:
        st.warning("No color mood data available.")
    else:
        st.dataframe(mood_df, use_container_width=True)

        fig_mood = px.pie(
            mood_df,
            names="color_mood",
            values="movie_count",
            title="Color Mood Distribution",
        )

        st.plotly_chart(fig_mood, use_container_width=True)

    st.subheader("Poster Ranking Analysis")

    top_n = st.slider(
        "Number of posters in each ranking",
        min_value=3,
        max_value=15,
        value=5,
    )

    rankings = create_ranking_tables(
        analysis_df=analysis_df,
        top_n=top_n,
    )

    if not rankings:
        st.warning("No ranking data available.")
    else:
        tabs = st.tabs(
            [
                "Darkest",
                "Brightest",
                "Most Saturated",
                "Least Saturated",
                "Most Diverse",
                "Highest Rated",
            ]
        )

        ranking_keys = [
            "darkest",
            "brightest",
            "most_saturated",
            "least_saturated",
            "most_diverse",
            "highest_rated",
        ]

        for tab, key in zip(tabs, ranking_keys):
            with tab:
                ranking_df = rankings.get(key)

                if ranking_df is None or ranking_df.empty:
                    st.warning("No data available.")
                else:
                    st.dataframe(ranking_df, use_container_width=True)

    st.subheader("Download Advanced Analysis CSV")

    download_df = prepare_analysis_download_df(analysis_df)
    csv_data = convert_df_to_csv(download_df)

    st.download_button(
        label="Download Full Analysis CSV",
        data=csv_data,
        file_name="advanced_movie_poster_analysis.csv",
        mime="text/csv",
    )