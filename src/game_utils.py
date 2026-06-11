from typing import Dict, Any, Optional, Tuple
import random
import math

import pandas as pd


def hex_to_rgb(hex_color: str) -> Optional[Tuple[int, int, int]]:
    """
    HEX color code를 RGB tuple로 변환.

    예:
    #ff0000 -> (255, 0, 0)
    """
    if not isinstance(hex_color, str):
        return None

    hex_color = hex_color.strip().lstrip("#")

    if len(hex_color) != 6:
        return None

    try:
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

    except ValueError:
        return None


def calculate_color_similarity(
    user_hex: str,
    answer_hex: str,
) -> float:
    """
    두 HEX 색상의 RGB 거리 기반 유사도 계산.

    반환값:
    - 0 ~ 100
    - 100에 가까울수록 정답 색상과 유사함
    """
    user_rgb = hex_to_rgb(user_hex)
    answer_rgb = hex_to_rgb(answer_hex)

    if user_rgb is None or answer_rgb is None:
        return 0.0

    distance = math.sqrt(
        (user_rgb[0] - answer_rgb[0]) ** 2
        + (user_rgb[1] - answer_rgb[1]) ** 2
        + (user_rgb[2] - answer_rgb[2]) ** 2
    )

    max_distance = math.sqrt(255 ** 2 + 255 ** 2 + 255 ** 2)

    similarity = 1 - (distance / max_distance)
    similarity_percent = max(0, similarity * 100)

    return round(similarity_percent, 2)


def evaluate_guess(
    user_hex: str,
    answer_hex: str,
    success_threshold: float = 80.0,
) -> Dict[str, Any]:
    """
    사용자의 색상 선택 결과 평가.

    반환:
    - similarity
    - is_success
    - feedback_label
    """
    similarity = calculate_color_similarity(
        user_hex=user_hex,
        answer_hex=answer_hex,
    )

    is_success = similarity >= success_threshold

    if similarity >= 90:
        feedback_label = "Excellent"
    elif similarity >= 80:
        feedback_label = "Success"
    elif similarity >= 65:
        feedback_label = "Close"
    else:
        feedback_label = "Try Again"

    return {
        "similarity": similarity,
        "is_success": is_success,
        "feedback_label": feedback_label,
    }


def pick_random_game_movie(
    analysis_df: pd.DataFrame,
    used_ids=None,
) -> Optional[Dict[str, Any]]:
    """
    분석 완료된 영화 중 게임에 사용할 포스터 하나를 랜덤 선택.

    이미 출제된 tmdb_id는 제외.
    """
    if analysis_df is None or analysis_df.empty:
        return None

    required_columns = ["poster_url", "dominant_color", "tmdb_id"]

    for column in required_columns:
        if column not in analysis_df.columns:
            return None

    valid_df = analysis_df.dropna(subset=required_columns)

    if valid_df.empty:
        return None

    if used_ids is None:
        used_ids = []

    valid_df = valid_df[~valid_df["tmdb_id"].isin(used_ids)]

    if valid_df.empty:
        return None

    random_index = random.choice(valid_df.index.tolist())

    return valid_df.loc[random_index].to_dict()


def init_game_state(session_state) -> None:
    """
    Streamlit session_state에 game 관련 상태 초기화.

    app.py에서:
    init_game_state(st.session_state)
    """
    if "game_movie" not in session_state:
        session_state["game_movie"] = None

    if "game_score" not in session_state:
        session_state["game_score"] = 0

    if "game_total" not in session_state:
        session_state["game_total"] = 0

    if "game_last_result" not in session_state:
        session_state["game_last_result"] = None

    if "game_user_color" not in session_state:
        session_state["game_user_color"] = "#000000"

    if "game_used_ids" not in session_state:
        session_state["game_used_ids"] = []


def reset_game_state(session_state) -> None:
    """
    게임 상태 전체 초기화.
    """
    session_state["game_movie"] = None
    session_state["game_score"] = 0
    session_state["game_total"] = 0
    session_state["game_last_result"] = None
    session_state["game_user_color"] = "#000000"
    session_state["game_used_ids"] = []
    session_state["game_answer_submitted"] = False


def start_new_question(session_state, analysis_df: pd.DataFrame) -> bool:
    """
    새로운 랜덤 문제 시작.

    이미 나온 포스터는 다시 나오지 않음.
    """
    used_ids = session_state.get("game_used_ids", [])

    movie = pick_random_game_movie(
        analysis_df=analysis_df,
        used_ids=used_ids,
    )

    if movie is None:
        return False

    movie_id = movie.get("tmdb_id")

    if movie_id is not None:
        session_state["game_used_ids"].append(movie_id)

    session_state["game_movie"] = movie
    session_state["game_last_result"] = None
    session_state["game_user_color"] = "#000000"
    session_state["game_answer_submitted"] = False

    return True


def submit_game_answer(
    session_state,
    user_color: str,
    success_threshold: float = 80.0,
) -> Optional[Dict[str, Any]]:
    """
    현재 game_movie에 대해 사용자의 답안을 제출하고 점수 업데이트.
    """
    game_movie = session_state.get("game_movie")

    if not game_movie:
        return None

    answer_color = game_movie.get("dominant_color")

    if not answer_color:
        return None

    result = evaluate_guess(
        user_hex=user_color,
        answer_hex=answer_color,
        success_threshold=success_threshold,
    )

    session_state["game_total"] += 1

    if result["is_success"]:
        session_state["game_score"] += 1

    session_state["game_last_result"] = result
    session_state["game_user_color"] = user_color
    session_state["game_answer_submitted"] = True

    return result