import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
import colorsys


def calculate_brightness(image: Image.Image) -> float:
    """
    이미지 평균 밝기 계산.
    값이 클수록 밝은 포스터.
    """
    img_array = np.array(image)

    r = img_array[:, :, 0]
    g = img_array[:, :, 1]
    b = img_array[:, :, 2]

    brightness = 0.299 * r + 0.587 * g + 0.114 * b

    return round(float(np.mean(brightness)), 2)


def calculate_saturation(image: Image.Image) -> float:
    """
    이미지 평균 채도 계산.
    값이 클수록 색이 강하고 선명함.
    """
    img_array = np.array(image.resize((100, 100)))
    pixels = img_array.reshape(-1, 3) / 255.0

    saturation_values = []

    for r, g, b in pixels:
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        saturation_values.append(s)

    return round(float(np.mean(saturation_values)), 3)


def rgb_to_hex(rgb: tuple) -> str:
    """
    RGB 값을 HEX 색상 코드로 변환.
    """
    return "#{:02x}{:02x}{:02x}".format(int(rgb[0]), int(rgb[1]), int(rgb[2]))


def extract_dominant_colors(image: Image.Image, num_colors: int = 5) -> list:
    """
    KMeans를 사용해 대표 색상 팔레트 추출.
    """
    small_image = image.resize((120, 180))
    img_array = np.array(small_image)

    pixels = img_array.reshape(-1, 3)

    kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init=10)
    kmeans.fit(pixels)

    colors = kmeans.cluster_centers_
    labels = kmeans.labels_

    counts = np.bincount(labels)
    sorted_indices = np.argsort(counts)[::-1]

    dominant_colors = []

    for idx in sorted_indices:
        rgb = colors[idx]
        dominant_colors.append(rgb_to_hex(tuple(rgb)))

    return dominant_colors


def analyze_poster(image: Image.Image) -> dict:
    """
    포스터 이미지 하나에 대해 색상 분석 결과 반환.
    """
    if image is None:
        return {
            "brightness": None,
            "saturation": None,
            "dominant_colors": [],
            "dominant_color": None,
        }

    dominant_colors = extract_dominant_colors(image)

    return {
        "brightness": calculate_brightness(image),
        "saturation": calculate_saturation(image),
        "dominant_colors": dominant_colors,
        "dominant_color": dominant_colors[0] if dominant_colors else None,
    }