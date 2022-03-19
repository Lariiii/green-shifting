# coding: utf-8
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint, text, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import null
from sqlalchemy.sql.sqltypes import Time, Text

Base = declarative_base()
metadata = Base.metadata


class TestModel(Base):
    __tablename__ = 'app_anomaly_detectors'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(600), nullable=False)
    link = Column(String(200), nullable=False)
    image_url = Column(String(200), nullable=False)