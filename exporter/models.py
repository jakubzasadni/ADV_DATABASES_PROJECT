from sqlalchemy import Boolean, Column, DateTime, Float, Index, Integer, String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Earthquake(Base):
    __tablename__ = "earthquakes"

    id = Column(String(20), primary_key=True)
    time = Column(DateTime(timezone=True), nullable=False)
    magnitude = Column(Float)
    mag_type = Column(String(10))
    place = Column(String)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    depth = Column(Float)
    status = Column(String(20))
    alert = Column(String(10))
    tsunami = Column(Boolean, default=False)
    significance = Column(Integer)
    updated_at = Column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index("idx_earthquakes_time", "time"),
        Index("idx_earthquakes_magnitude", "magnitude"),
        Index("idx_earthquakes_alert", "alert"),
    )
