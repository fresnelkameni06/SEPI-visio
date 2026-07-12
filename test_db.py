from sqlalchemy import create_engine
from app.models import Base

engine = create_engine("sqlite:///visio.db")
Base.metadata.create_all(engine)
print("Base creee avec succes")