from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import time

app = FastAPI(
    title="Mon API",
    description="API personnelle gratuite déployée sur Vercel",
    version="1.0.0",
)

# Autoriser les appels depuis n'importe où (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Modèles =====
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    in_stock: bool = True

# ===== Stockage en mémoire (pour démo) =====
items_db: dict[int, Item] = {}
next_id = 1

# ===== Endpoints =====

@app.get("/")
def root():
    """Page d'accueil de l'API."""
    return {
        "message": "Bienvenue sur mon API !",
        "docs": "/docs",
        "version": "1.0.0",
    }

@app.get("/health")
def health():
    """Vérifier que l'API fonctionne."""
    return {"status": "ok", "timestamp": time.time()}

@app.get("/items")
def list_items():
    """Lister tous les items."""
    return {"items": list(items_db.values()), "count": len(items_db)}

@app.get("/items/{item_id}")
def get_item(item_id: int):
    """Récupérer un item par son ID."""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item introuvable")
    return items_db[item_id]

@app.post("/items", status_code=201)
def create_item(item: Item):
    """Créer un nouvel item."""
    global next_id
    items_db[next_id] = item
    created = {"id": next_id, **item.model_dump()}
    next_id += 1
    return created

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    """Supprimer un item."""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item introuvable")
    del items_db[item_id]
    return {"deleted": item_id}

@app.get("/search")
def search(q: str = Query(..., min_length=1)):
    """Rechercher dans les items."""
    results = [
        {"id": i, **item.model_dump()}
        for i, item in items_db.items()
        if q.lower() in item.name.lower()
    ]
    return {"query": q, "results": results}￼Enter
