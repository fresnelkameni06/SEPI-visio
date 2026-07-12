from app.core.features import extract_features
from app.core.rules import DEFAULT_THRESHOLDS

FEATURE_ORDER = [
    "file_size", "width", "height", "aspect_ratio",
    "avg_r", "avg_g", "avg_b", "brightness", "contrast", "saturation",
    "colorfulness", "dark_ratio", "edge_density", "texture", "entropy",
    "green_ratio", "sharpness", "max_zone_edges", "zone_variance",
    "bottom_edge_density", "ground_clutter", "green_zone_max", "green_zone_var",
]


def analyse_image(filepath, decision=2):
    feats = extract_features(filepath)

    t = DEFAULT_THRESHOLDS
    score = 0
    if feats["dark_ratio"] > t["dark_ratio"]:
        score += 1
    if feats["bottom_edge_density"] > t["bottom_edge_density"]:
        score += 1
    if feats["zone_variance"] < t["zone_variance"]:
        score += 1
    if feats["entropy"] > t["entropy"]:
        score += 1
    if feats["green_ratio"] < t["green_ratio"]:
        score += 1

    label = "dirty" if score >= decision else "clean"
    ai_annotation = "Pleine" if label == "dirty" else "Vide"
    ai_confidence = round(score / 5 * 100, 1)

    return feats, ai_annotation, ai_confidence, score