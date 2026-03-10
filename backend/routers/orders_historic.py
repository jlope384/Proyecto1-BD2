from fastapi import APIRouter, Depends, Response
from database import orders_historic_collection
from utils.utils import serialize_doc, allow_all_cors

router = APIRouter(
    prefix="/orders-historic",
    tags=["Orders Historic"],
    dependencies=[Depends(allow_all_cors)],
)

@router.options("/{full_path:path}")
def orders_historic_cors(full_path: str, response: Response):
    allow_all_cors(response)
    return {"status": "ok"}

@router.get("/")
def get_historic_orders():
    orders = list(orders_historic_collection.find())
    return [serialize_doc(o) for o in orders]