from typing import Any, Dict, List

import pandas as pd
import streamlit as st


def init_cart() -> None:
    """
    Cart는 flag 기반으로 관리.

    cart_flags:
    - key: tmdb_id 문자열
    - value: True

    cart_extra_items:
    - Movie Search처럼 Dashboard analysis_df에 없는 개별 영화 저장용
    """
    if "cart_flags" not in st.session_state:
        st.session_state["cart_flags"] = {}

    if "cart_extra_items" not in st.session_state:
        st.session_state["cart_extra_items"] = {}


def normalize_id(tmdb_id: Any) -> str:
    """
    tmdb_id를 session_state key로 쓰기 위해 문자열로 통일.
    """
    return str(tmdb_id)


def add_to_cart_flag(movie_data: Dict[str, Any]) -> bool:
    """
    Cart에 item 전체를 바로 append하지 않고,
    tmdb_id flag만 켜는 방식.

    Movie Search에서 온 개별 영화처럼 analysis_df에 없을 수도 있으므로
    extra item도 함께 저장해둠.
    """
    init_cart()

    if not movie_data:
        return False

    tmdb_id = movie_data.get("tmdb_id")

    if tmdb_id is None:
        return False

    key = normalize_id(tmdb_id)

    if st.session_state["cart_flags"].get(key):
        return False

    st.session_state["cart_flags"][key] = True

    # Dashboard analysis_df에 없는 영화일 수 있으므로 백업 데이터 저장
    st.session_state["cart_extra_items"][key] = movie_data

    return True


def remove_from_cart(tmdb_id: Any) -> bool:
    """
    Cart flag 제거.
    """
    init_cart()

    key = normalize_id(tmdb_id)

    existed = key in st.session_state["cart_flags"]

    if key in st.session_state["cart_flags"]:
        del st.session_state["cart_flags"][key]

    if key in st.session_state["cart_extra_items"]:
        del st.session_state["cart_extra_items"][key]

    if "cart_zip_data" in st.session_state:
        del st.session_state["cart_zip_data"]

    return existed


def clear_cart() -> None:
    """
    Cart 전체 초기화.
    """
    st.session_state["cart_flags"] = {}
    st.session_state["cart_extra_items"] = {}

    if "cart_zip_data" in st.session_state:
        del st.session_state["cart_zip_data"]


def is_in_cart(tmdb_id: Any) -> bool:
    """
    특정 영화가 cart에 들어있는지 확인.
    """
    init_cart()

    if tmdb_id is None:
        return False

    key = normalize_id(tmdb_id)

    return bool(st.session_state["cart_flags"].get(key))


def get_cart_count() -> int:
    """
    Sidebar Cart 숫자 표시용.
    """
    init_cart()
    return len(st.session_state["cart_flags"])


def get_cart_ids() -> List[str]:
    """
    Cart에 담긴 tmdb_id 목록 반환.
    """
    init_cart()
    return list(st.session_state["cart_flags"].keys())


def build_cart_dataframe_from_flags(
    analysis_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Cart 페이지에 진입했을 때만 실행.

    1. cart_flags에 저장된 tmdb_id 확인
    2. 현재 analysis_df에서 해당 영화 정보 필터링
    3. analysis_df에 없는 개별 Movie Search item은 cart_extra_items에서 보충
    """
    init_cart()

    cart_ids = get_cart_ids()

    if not cart_ids:
        return pd.DataFrame()

    rows = []

    # 1. Dashboard analysis_df에서 찾기
    if analysis_df is not None and not analysis_df.empty and "tmdb_id" in analysis_df.columns:
        temp_df = analysis_df.copy()
        temp_df["tmdb_id_str"] = temp_df["tmdb_id"].astype(str)

        matched_df = temp_df[temp_df["tmdb_id_str"].isin(cart_ids)]

        if not matched_df.empty:
            matched_df = matched_df.drop(columns=["tmdb_id_str"])
            rows.extend(matched_df.to_dict("records"))

    # 2. analysis_df에 없는 Movie Search item 보충
    existing_ids = {str(item.get("tmdb_id")) for item in rows}

    for cart_id in cart_ids:
        if cart_id not in existing_ids:
            extra_item = st.session_state["cart_extra_items"].get(cart_id)

            if extra_item:
                rows.append(extra_item)

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(rows)


def get_cart_items_for_download(
    analysis_df: pd.DataFrame,
) -> List[Dict[str, Any]]:
    """
    ZIP / CSV 다운로드용 cart item list.
    """
    cart_df = build_cart_dataframe_from_flags(analysis_df)

    if cart_df.empty:
        return []

    return cart_df.to_dict("records")