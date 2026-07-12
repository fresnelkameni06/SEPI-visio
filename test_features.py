from app.core.features import extract_features

result = extract_features("data/sample/00543_02.jpg")
for key, value in result.items():
    print(f"{key:15} : {value}")