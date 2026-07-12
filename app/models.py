from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    source = Column(String, default="dataset")
    upload_date = Column(DateTime, default=datetime.now)

    annotation = Column(String)
    predicted_label = Column(String)

    file_size = Column(Integer)
    width = Column(Integer)
    height = Column(Integer)
    aspect_ratio = Column(Float)

    avg_r = Column(Float)
    avg_g = Column(Float)
    avg_b = Column(Float)
    brightness = Column(Float)
    contrast = Column(Float)
    saturation = Column(Float)
    colorfulness = Column(Float)
    dark_ratio = Column(Float)
    edge_density = Column(Float)
    texture = Column(Float)
    entropy = Column(Float)
    green_ratio = Column(Float)
    sharpness = Column(Float)
    max_zone_edges = Column(Float)
    zone_variance = Column(Float)
    bottom_edge_density = Column(Float)
    ground_clutter = Column(Float)
    green_zone_max = Column(Float)
    green_zone_var = Column(Float)

    latitude = Column(Float)
    longitude = Column(Float)

    def __repr__(self):
        return f"<Image {self.filename} | {self.annotation}>"