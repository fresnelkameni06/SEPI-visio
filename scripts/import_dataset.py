import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import Base, Image
from app.core.features import extract_features

DATA_DIR = "data/train/with_label"
LABELS = ["clean", "dirty"]

engine = create_engine("sqlite:///visio.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

total, errors = 0, 0

for label in LABELS:
    folder = os.path.join(DATA_DIR, label)
    if not os.path.isdir(folder):
        print(f"Dossier introuvable : {folder}")
        continue

    for filename in os.listdir(folder):
        filepath = os.path.join(folder, filename)
        try:
            features = extract_features(filepath)
            image = Image(
                filename=filename,
                filepath=filepath,
                source="dataset",
                annotation=label,
                **features,
            )
            session.add(image)
            total += 1
        except Exception as e:
            errors += 1
            print(f"Erreur sur {filename} : {e}")

    session.commit()
    print(f"{label} : termine")

print(f"\nTotal importe : {total} images | Erreurs : {errors}")
session.close()