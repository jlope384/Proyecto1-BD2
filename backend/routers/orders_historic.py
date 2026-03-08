from fastapi import APIRouter
from database import orders_historic_collection
from utils.utils import serialize_doc

router = APIRouter(prefix="/orders-historic", tags=["Orders Historic"])

@router.get("/")
def get_historic_orders():
    orders = list(orders_historic_collection.find())
    return [serialize_doc(o) for o in orders]