from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Image

engine = create_engine("sqlite:///visio.db")
session = sessionmaker(bind=engine)()

features = ["file_size", "width", "height", "aspect_ratio",
            "avg_r", "avg_g", "avg_b", "brightness", "contrast",
            "saturation", "colorfulness", "dark_ratio", "edge_density",
            "texture", "entropy", "green_ratio", "sharpness"]

for label in ["clean", "dirty"]:
    rows = session.query(Image).filter(Image.annotation == label).all()
    print(f"\n=== {label} ({len(rows)} images) ===")
    for f in features:
        values = [getattr(r, f) for r in rows]
        moy = sum(values) / len(values)
        print(f"{f:15} : {moy:.3f}")

session.close()