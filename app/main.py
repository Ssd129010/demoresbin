import os
import math
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Cart Service", version="1.0.0")

# In-memory хранилище для демо (в проде — Managed Redis)
CARTS: dict[str, dict[str, int]] = {}

class Item(BaseModel):
    sku: str
    qty: int = 1

@app.get("/healthz")
def healthz():
    return {"status": "ok", "pod": os.getenv("HOSTNAME", "local")}

@app.post("/cart/{user_id}/items")
def add_item(user_id: str, item: Item):
    cart = CARTS.setdefault(user_id, {})
    cart[item.sku] = cart.get(item.sku, 0) + item.qty
    return {"user_id": user_id, "cart": cart}

@app.get("/cart/{user_id}")
def get_cart(user_id: str):
    if user_id not in CARTS:
        raise HTTPException(404, "cart not found")
    return {"user_id": user_id, "cart": CARTS[user_id]}

@app.get("/cart/{user_id}/checkout")
def checkout(user_id: str):
    # Имитация расчёта корзины: скидки, налоги, доставка.
    # Специально грузит CPU, чтобы продемонстрировать автоскейлинг.
    result = 0.0
    for i in range(1, 200_000):
        result += math.sqrt(i) * math.sin(i)
    cart = CARTS.get(user_id, {})
    return {
        "user_id": user_id,
        "items": sum(cart.values()),
        "total_checksum": round(result, 2),
        "served_by": os.getenv("HOSTNAME", "local"),
    }
