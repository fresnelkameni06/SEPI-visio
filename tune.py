from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Image

engine = create_engine("sqlite:///visio.db")
session = sessionmaker(bind=engine)()
images = session.query(Image).all()

clean = [i for i in images if i.annotation == "clean"]
dirty = [i for i in images if i.annotation == "dirty"]

def best_threshold(feature, direction):
    values = sorted(set(getattr(i, feature) for i in images))
    best_acc, best_t = 0, None
    for t in values:
        if direction == "above":
            correct = sum(1 for i in dirty if getattr(i, feature) > t) + \
                      sum(1 for i in clean if getattr(i, feature) <= t)
        else:
            correct = sum(1 for i in dirty if getattr(i, feature) < t) + \
                      sum(1 for i in clean if getattr(i, feature) >= t)
        acc = correct / len(images)
        if acc > best_acc:
            best_acc, best_t = acc, t
    return best_t, best_acc

features = [
    ("green_zone_max", "below"), ("green_zone_var", "below"),
    ("ground_clutter", "above"), ("dark_ratio", "above"),
    ("bottom_edge_density", "above"), ("zone_variance", "below"),
    ("entropy", "above"), ("green_ratio", "below"),
    ("edge_density", "above"), ("texture", "below"),
]

print(f"{'feature':15} {'seuil':>12} {'accuracy seule':>15}")
for f, d in sorted(features, key=lambda x: -best_threshold(x[0], x[1])[1]):
    t, acc = best_threshold(f, d)
    print(f"{f:15} {t:>12.2f} {acc:>14.0%}  ({d})")

session.close()