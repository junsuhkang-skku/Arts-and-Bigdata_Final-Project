from typing import List, Tuple, Optional, Dict, Any
import colorsys

import numpy as np
from PIL import Image
from sklearn.cluster import KMeans


def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """
    RGB tuple을 HEX color code로 변환.

    예:
    (255, 0, 0) -> #ff0000
    """
    r, g, b = rgb

    return "#{:02x}{:02x}{:02x}".format(
        int(r),
        int(g),
        int(b),
    )


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


def calculate_brightness(image: Image.Image) -> Optional[float]:
    """
    이미지 평균 밝기 계산.

    RGB 기반 밝기 공식:
    brightness = 0.299R + 0.587G + 0.114B

    반환값:
    - 0에 가까울수록 어두움
    - 255에 가까울수록 밝음
    """
    if image is None:
        return None

    try:
        rgb_image = image.convert("RGB")
        img_array = np.array(rgb_image)

        r = img_array[:, :, 0]
        g = img_array[:, :, 1]
        b = img_array[:, :, 2]

        brightness = 0.299 * r + 0.587 * g + 0.114 * b

        return round(float(np.mean(brightness)), 2)

    except Exception:
        return None


def calculate_saturation(image: Image.Image) -> Optional[float]:
    """
    이미지 평균 채도 계산.

    방식:
    - RGB 값을 HSV 색공간으로 변환
    - HSV 중 S, 즉 saturation 값을 평균냄

    반환값:
    - 0에 가까울수록 무채색에 가까움
    - 1에 가까울수록 색이 선명함
    """
    if image is None:
        return None

    try:
        rgb_image = image.convert("RGB").resize((100, 100))
        img_array = np.array(rgb_image)

        pixels = img_array.reshape(-1, 3) / 255.0

        saturation_values = []

        for r, g, b in pixels:
            _, saturation, _ = colorsys.rgb_to_hsv(r, g, b)
            saturation_values.append(saturation)

        return round(float(np.mean(saturation_values)), 3)

    except Exception:
        return None


def extract_dominant_colors(
    image: Image.Image,
    num_colors: int = 5,
) -> List[str]:
    """
    KMeans clustering을 사용해 이미지의 대표 색상 팔레트 추출.

    반환:
    - HEX color list
    - 가장 많이 등장한 색상이 첫 번째
    """
    if image is None:
        return []

    try:
        rgb_image = image.convert("RGB").resize((120, 180))
        img_array = np.array(rgb_image)

        pixels = img_array.reshape(-1, 3)

        kmeans = KMeans(
            n_clusters=num_colors,
            random_state=42,
            n_init=10,
        )

        kmeans.fit(pixels)

        colors = kmeans.cluster_centers_
        labels = kmeans.labels_

        counts = np.bincount(labels)
        sorted_indices = np.argsort(counts)[::-1]

        dominant_colors = []

        for index in sorted_indices:
            rgb = colors[index]
            rgb_tuple = (
                int(rgb[0]),
                int(rgb[1]),
                int(rgb[2]),
            )
            dominant_colors.append(rgb_to_hex(rgb_tuple))

        return dominant_colors

    except Exception:
        return []


def calculate_color_diversity(dominant_colors: List[str]) -> Optional[float]:
    """
    Color Diversity Score 계산.

    방식:
    - 팔레트 색상들 사이의 RGB 거리 평균을 계산
    - 0~1 사이 값으로 정규화
    - 값이 클수록 색상 차이가 큼

    이 기능은 advanced analysis에서 사용할 수 있음.
    """
    if not dominant_colors or len(dominant_colors) < 2:
        return None

    rgb_values = []

    for color in dominant_colors:
        rgb = hex_to_rgb(color)
        if rgb is not None:
            rgb_values.append(rgb)

    if len(rgb_values) < 2:
        return None

    distances = []

    for i in range(len(rgb_values)):
        for j in range(i + 1, len(rgb_values)):
            r1, g1, b1 = rgb_values[i]
            r2, g2, b2 = rgb_values[j]

            distance = np.sqrt(
                (r1 - r2) ** 2
                + (g1 - g2) ** 2
                + (b1 - b2) ** 2
            )

            distances.append(distance)

    max_distance = np.sqrt(255 ** 2 + 255 ** 2 + 255 ** 2)

    diversity = np.mean(distances) / max_distance

    return round(float(diversity), 3)


def classify_color_mood(
    brightness: Optional[float],
    saturation: Optional[float],
    dominant_color: Optional[str],
) -> str:
    """
    포스터 색상 분위기를 간단히 분류.

    기준:
    - 밝기 낮음: Dark / Moody
    - 채도 높음: Vivid / Energetic
    - 따뜻한 hue: Warm
    - 차가운 hue: Cold
    """
    if brightness is None or saturation is None or dominant_color is None:
        return "Unknown"

    rgb = hex_to_rgb(dominant_color)

    if rgb is None:
        return "Unknown"

    r, g, b = [value / 255.0 for value in rgb]
    hue, _, _ = colorsys.rgb_to_hsv(r, g, b)
    hue_degree = hue * 360

    if brightness < 60:
        return "Dark / Moody"

    if saturation > 0.6:
        return "Vivid / Energetic"

    if 0 <= hue_degree <= 60 or 330 <= hue_degree <= 360:
        return "Warm"

    if 180 <= hue_degree <= 260:
        return "Cold / Mysterious"

    if saturation < 0.2:
        return "Neutral / Minimal"

    return "Balanced"


def analyze_poster(
    image: Image.Image,
    num_colors: int = 5,
) -> Dict[str, Any]:
    """
    포스터 이미지 하나에 대해 전체 색상 분석 수행.

    반환:
    - dominant_color
    - dominant_colors
    - brightness
    - saturation
    - color_diversity
    - color_mood
    """
    if image is None:
        return {
            "dominant_color": None,
            "dominant_colors": [],
            "brightness": None,
            "saturation": None,
            "color_diversity": None,
            "color_mood": "Unknown",
        }

    dominant_colors = extract_dominant_colors(
        image=image,
        num_colors=num_colors,
    )

    dominant_color = dominant_colors[0] if dominant_colors else None
    brightness = calculate_brightness(image)
    saturation = calculate_saturation(image)
    color_diversity = calculate_color_diversity(dominant_colors)
    color_mood = classify_color_mood(
        brightness=brightness,
        saturation=saturation,
        dominant_color=dominant_color,
    )

    return {
        "dominant_color": dominant_color,
        "dominant_colors": dominant_colors,
        "brightness": brightness,
        "saturation": saturation,
        "color_diversity": color_diversity,
        "color_mood": color_mood,
    }