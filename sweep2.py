from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Image

engine = create_engine("sqlite:///visio.db")
session = sessionmaker(bind=engine)()
images = session.query(Image).all()

feats = ["ground_clutter", "dark_ratio", "bottom_edge_density",
         "edge_density", "texture", "max_zone_edges"]

stats = {}
for f in feats:
    vals = [getattr(i, f) for i in images]
    stats[f] = (min(vals), max(vals))

def norm(img, f):
    lo, hi = stats[f]
    return (getattr(img, f) - lo) / (hi - lo) if hi > lo else 0

def dirtiness(img):
    return sum(norm(img, f) for f in feats) / len(feats)

scores = sorted(dirtiness(i) for i in images)
print(f"{'seuil':>7}{'acc':>8}{'prec':>8}{'rec':>8}{'spec':>8}")
best = (0, 0)
for q in [0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60]:
    thr = scores[int(len(scores) * q)]
    tp=tn=fp=fn=0
    for img in images:
        pred = "dirty" if dirtiness(img) > thr else "clean"
        t = img.annotation
        if pred=="dirty" and t=="dirty": tp+=1
        elif pred=="clean" and t=="clean": tn+=1
        elif pred=="dirty" and t=="clean": fp+=1
        else: fn+=1
    total=tp+tn+fp+fn
    acc=(tp+tn)/total
    prec=tp/(tp+fp) if tp+fp else 0
    rec=tp/(tp+fn) if tp+fn else 0
    spec=tn/(tn+fp) if tn+fp else 0
    if acc > best[0]: best = (acc, thr)
    print(f"{thr:>7.3f}{acc:>8.1%}{prec:>8.1%}{rec:>8.1%}{spec:>8.1%}")
print(f"\nmeilleure accuracy : {best[0]:.1%}")

session.close()