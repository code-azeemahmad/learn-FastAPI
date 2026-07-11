from fastapi import APIRouter

router = APIRouter(
    prefix="/products",
    tags=["Products"],
)

products = ["laptop", "phone", "chair"]

@router.get("/")
def get_products():
    return {
        "products": products
    }
@router.get("/{product_id}")
def get_products(product_id: int):
    return {
        "product_id": products[product_id]
    }