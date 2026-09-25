from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import time

# ============================================================
# INSTANCE FASTAPI (doit être au niveau supérieur du fichier)
# ============================================================
app = FastAPI(
    title="Kaze API",
    description="API REST publique en Python — endpoints CRUD, recherche et documentation interactive.",
    version="1.0.0",
)

# ============================================================
# CORS — autorise les appels depuis n'importe quel site
# ============================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# MODÈLES
# ============================================================
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    in_stock: bool = True

# ============================================================
# STOCKAGE EN MÉMOIRE (démo)
# ============================================================
items_db: dict[int, Item] = {}
next_id: int = 1

# ============================================================
# ENDPOINTS
# ============================================================

@app.get("/")
def root():
    """Page d'accueil de l'API."""
    return {
        "message": "Bienvenue sur Kaze API",
        "version": "1.0.0",
        "docs": "/docs",
    }

@app.get("/health")
def health():
    """Vérifie que l'API fonctionne."""
    return {"status": "ok", "timestamp": time.time()}

@app.get("/items")
def list_items():
    """Liste tous les items."""
    return {"items": list(items_db.values()), "count": len(items_db)}

@app.get("/items/{item_id}")
def get_item(item_id: int):
    """Récupère un item par son ID."""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item introuvable")
    return items_db[item_id]

@app.post("/items", status_code=201)
def create_item(item: Item):
    """Crée un nouvel item."""
    global next_id
    items_db[next_id] = item
    created = {"id": next_id, **item.model_dump()}
    next_id += 1
    return created

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    """Supprime un item."""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item introuvable")
    del items_db[item_id]
    return {"deleted": item_id}

@app.get("/search")
def search(q: str = Query(..., min_length=1)):
    """Recherche un item par son nom."""
    results = [
        {"id": i, **item.model_dump()}
        for i, item in items_db.items()
        if q.lower() in item.name.lower()
    ]
    return {"query": q, "count": len(results), "results": results}
