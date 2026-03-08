from fastapi import FastAPI
from routers import restaurants, users, reviews, orders, files, orders_historic

app = FastAPI(title="Restaurant System API")

app.include_router(restaurants.router)
app.include_router(users.router)
app.include_router(reviews.router)
app.include_router(orders.router)
app.include_router(files.router)
app.include_router(orders_historic.router)

@app.get("/ping")
def root():
    return {"message": "pong"}