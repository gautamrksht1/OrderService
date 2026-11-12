from pathlib import Path
import os
import sys
import time

from fastapi import FastAPI
import requests
from sqlalchemy.exc import OperationalError

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from database import SessionLocal, engine
from orders import Base, Order
from orderrequest import OrderRequest


def ensure_database_ready():
    for _ in range(30):
        try:
            Base.metadata.create_all(bind=engine)
            return
        except OperationalError:
            time.sleep(2)
    raise RuntimeError("Database is not ready")


ensure_database_ready()

app = FastAPI()

CATALOG_SERVICE = os.getenv("CATALOG_SERVICE_URL", "").strip().rstrip("/")
if not CATALOG_SERVICE:
    raise RuntimeError("CATALOG_SERVICE_URL environment variable must be set")

@app.post("/orders")
def place_order(request:OrderRequest):

    book_response = requests.get(
        f"{CATALOG_SERVICE}/books/{request.book_id}"
    )

    book = book_response.json()

    reserve_response = requests.post(
        f"{CATALOG_SERVICE}/inventory/reserve",
        json={
            "book_id":request.book_id,
            "quantity":request.quantity
        }
    )

    reserve_result = reserve_response.json()

    if reserve_result["success"] == False:
        return {
            "success":False,
            "message":"Insufficient Stock"
        }

    db = SessionLocal()

    order = Order(
        book_id=request.book_id,
        quantity=request.quantity,
        total_amount=
            book["price"] * request.quantity,
        order_status="SUCCESS"
    )

    db.add(order)

    db.commit()

    db.refresh(order)

    return {
        "success":True,
        "order_id":order.id
    }

@app.get("/orders")
def get_orders():

    db = SessionLocal()

    return db.query(Order).all()