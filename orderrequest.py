from pydantic import BaseModel

class OrderRequest(BaseModel):
    book_id:int
    quantity:int