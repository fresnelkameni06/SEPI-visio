from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Image
from app.core.rules import classify

FEATURE_KEYS = ["dark_ratio", "bottom_edge_density", "zone_variance", "entropy", "green_ratio"]

ALL_FEATURES = ["file_size", "width", "height", "aspect_ratio", "brightness",
                "contrast", "saturation", "colorfulness", "dark_ratio",
                "edge_density", "texture", "entropy", "green_ratio", "sharpness",
                "max_zone_edges", "zone_variance", "bottom_edge_density", "ground_clutter",
                "green_zone_max", "green_zone_var"]


def evaluate(show_errors=False):
    engine = create_engine("sqlite:///visio.db")
    session = sessionmaker(bind=engine)()
    images = session.query(Image).all()

    tp = tn = fp = fn = 0
    errors = []

    class_means = {}
    for label in ["clean", "dirty"]:
        rows = [i for i in images if i.annotation == label]
        if rows:
            class_means[label] = {
                f: sum(getattr(r, f) for r in rows) / len(rows) for f in ALL_FEATURES
            }

    for img in images:
        features = {k: getattr(img, k) for k in FEATURE_KEYS}
        pred = classify(features)
        img.predicted_label = pred
        truth = img.annotation

        if pred == "dirty" and truth == "dirty":
            tp += 1
        elif pred == "clean" and truth == "clean":
            tn += 1
        elif pred == "dirty" and truth == "clean":
            fp += 1
            errors.append(img)
        else:
            fn += 1
            errors.append(img)

    session.commit()

    total = tp + tn + fp + fn
    accuracy = (tp + tn) / total if total else 0
    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0
    specificity = tn / (tn + fp) if (tn + fp) else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0

    print(f"Images analysees : {total}")
    print(f"Accuracy    : {accuracy:.2%}")
    print(f"Precision   : {precision:.2%}")
    print(f"Recall      : {recall:.2%}")
    print(f"Specificity : {specificity:.2%}")
    print(f"F1-score    : {f1:.2%}")
    print(f"\nMatrice de confusion")
    print(f"                 dirty(pred)  clean(pred)")
    print(f"dirty (reel)     {tp:^11}  {fn:^11}")
    print(f"clean (reel)     {fp:^11}  {tn:^11}")

    if show_errors and errors:
        print(f"\n{'='*60}")
        print(f"IMAGES MAL PREDITES ({len(errors)})")
        print(f"{'='*60}")
        for img in errors:
            print(f"\n>>> {img.filename}")
            print(f"    reel = {img.annotation}  |  predit = {img.predicted_label}")
            print(f"    {'feature':16} {'valeur':>12} {'moy '+img.annotation:>14} {'ecart':>8}")
            for f in ALL_FEATURES:
                val = getattr(img, f)
                mean = class_means[img.annotation][f]
                ecart = val - mean
                flag = "  <-- suspect" if abs(ecart) > abs(mean) * 0.3 else ""
                print(f"    {f:16} {val:>12.3f} {mean:>14.3f} {ecart:>+8.2f}{flag}")

    session.close()


if __name__ == "__main__":
    evaluate()