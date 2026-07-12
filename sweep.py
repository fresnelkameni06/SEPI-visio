from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Image

engine = create_engine("sqlite:///visio.db")
session = sessionmaker(bind=engine)()
images = session.query(Image).all()

T = {"ground_clutter": 50.49, "dark_ratio": 0.13,
     "bottom_edge_density": 0.18, "edge_density": 0.21}

def score(img):
    s = 0
    if img.ground_clutter > T["ground_clutter"]: s += 2
    if img.dark_ratio > T["dark_ratio"]: s += 1
    if img.bottom_edge_density > T["bottom_edge_density"]: s += 1
    if img.edge_density > T["edge_density"]: s += 1
    return s

print(f"{'seuil':>6}{'acc':>8}{'prec':>8}{'rec':>8}{'spec':>8}")
for decision in [1, 2, 3, 4]:
    tp=tn=fp=fn=0
    for img in images:
        pred = "dirty" if score(img) >= decision else "clean"
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
    print(f"{decision:>6}{acc:>8.1%}{prec:>8.1%}{rec:>8.1%}{spec:>8.1%}")

session.close()