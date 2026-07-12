DEFAULT_THRESHOLDS = {
    "dark_ratio": 0.132,
    "bottom_edge_density": 0.180,
    "zone_variance": 0.003,
    "entropy": 7.624,
    "green_ratio": 0.034,
}


def classify(features, thresholds=None, decision=2):
    t = thresholds or DEFAULT_THRESHOLDS
    score = 0

    if features["dark_ratio"] > t["dark_ratio"]:
        score += 1
    if features["bottom_edge_density"] > t["bottom_edge_density"]:
        score += 1
    if features["zone_variance"] < t["zone_variance"]:
        score += 1
    if features["entropy"] > t["entropy"]:
        score += 1
    if features["green_ratio"] < t["green_ratio"]:
        score += 1

    return "dirty" if score >= decision else "clean"