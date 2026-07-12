from itertools import combinations
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Image

engine = create_engine("sqlite:///visio.db")
session = sessionmaker(bind=engine)()
images = session.query(Image).all()

feats = ["ground_clutter", "dark_ratio", "bottom_edge_density",
         "zone_variance", "entropy", "green_ratio", "edge_density",
         "texture", "green_zone_max"]

# meilleur seuil + sens pour chaque feature
def best_thr(f):
    vals = sorted(set(getattr(i, f) for i in images))
    best = (0, None, None)
    for t in vals:
        for d in ("above", "below"):
            tp=tn=fp=fn=0
            for i in images:
                v = getattr(i, f)
                pred = "dirty" if (v > t if d=="above" else v < t) else "clean"
                lab = i.annotation
                if pred==lab=="dirty": tp+=1
                elif pred==lab=="clean": tn+=1
                elif pred=="dirty": fp+=1
                else: fn+=1
            acc = (tp+tn)/len(images)
            if acc > best[0]: best = (acc, t, d)
    return best

thr = {f: best_thr(f) for f in feats}

def vote(img, f):
    _, t, d = thr[f]
    v = getattr(img, f)
    return (v > t) if d == "above" else (v < t)

best_overall = (0, None, None)
for k in (3, 4, 5):
    for combo in combinations(feats, k):
        for decision in range(2, k+1):
            tp=tn=fp=fn=0
            for img in images:
                votes = sum(vote(img, f) for f in combo)
                pred = "dirty" if votes >= decision else "clean"
                lab = img.annotation
                if pred==lab=="dirty": tp+=1
                elif pred==lab=="clean": tn+=1
                elif pred=="dirty": fp+=1
                else: fn+=1
            acc = (tp+tn)/len(images)
            if acc > best_overall[0]:
                best_overall = (acc, combo, decision)

acc, combo, dec = best_overall
print(f"Meilleure accuracy : {acc:.1%}")
print(f"Features : {combo}")
print(f"Seuil de decision : >= {dec} votes")
print(f"\nSeuils par feature :")
for f in combo:
    a, t, d = thr[f]
    print(f"  {f:20} {d:6} {t:.3f}   (seule: {a:.0%})")

session.close()