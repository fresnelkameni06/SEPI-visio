import sys
from app.core.features import extract_features
from app.core.rules import classify, DEFAULT_THRESHOLDS

path = sys.argv[1] if len(sys.argv) > 1 else input("Chemin de l'image : ").strip('"')

f = extract_features(path)
t = DEFAULT_THRESHOLDS

print(f"\n=== {path} ===\n")

votes = [
    ("dark_ratio",          f["dark_ratio"],          ">", t["dark_ratio"],          f["dark_ratio"] > t["dark_ratio"]),
    ("bottom_edge_density", f["bottom_edge_density"], ">", t["bottom_edge_density"], f["bottom_edge_density"] > t["bottom_edge_density"]),
    ("zone_variance",       f["zone_variance"],       "<", t["zone_variance"],       f["zone_variance"] < t["zone_variance"]),
    ("entropy",             f["entropy"],             ">", t["entropy"],             f["entropy"] > t["entropy"]),
    ("green_ratio",         f["green_ratio"],         "<", t["green_ratio"],         f["green_ratio"] < t["green_ratio"]),
]

print(f"{'feature':22}{'valeur':>10}  {'regle':^14} {'vote dirty'}")
print("-" * 60)
score = 0
for name, val, sens, seuil, ok in votes:
    if ok:
        score += 1
    regle = f"{sens} {seuil}"
    print(f"{name:22}{val:>10.4f}  {regle:^14} {'OUI' if ok else 'non'}")

print("-" * 60)
print(f"Score total : {score} / 5   (dirty si score >= 2)")
print(f"\n>>> PREDICTION : {classify(f).upper()}")

print(f"\n--- toutes les features ---")
for k, v in f.items():
    print(f"  {k:22}: {v}")