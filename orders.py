from sqlalchemy import *
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Order(Base):

    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    book_id = Column(Integer)
    quantity = Column(Integer)
    total_amount = Column(Float)
    order_status = Column(String(20))