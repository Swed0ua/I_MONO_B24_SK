from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.services.product_service import ProductService
from app.repositories.base import ProductRepository
from app.database import get_db
from typing import List, Optional

router = APIRouter(prefix="/products", tags=["products"])


def get_product_service(db: AsyncSession = Depends(get_db)) -> ProductService:
    """Dependency для отримання сервісу товарів"""
    product_repository = ProductRepository(db)
    return ProductService(product_repository)


@router.post("/", response_model=ProductResponse)
async def create_product(
    product_data: ProductCreate,
    product_service: ProductService = Depends(get_product_service)
):
    """Створення товару"""
    try:
        result = await product_service.create_product(product_data)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Product creation failed: {str(e)}"
        )


@router.get("/", response_model=List[ProductResponse])
async def get_products(
    active_only: bool = True,
    product_service: ProductService = Depends(get_product_service)
):
    """Отримання всіх товарів"""
    try:
        products = await product_service.get_all_products(active_only=active_only)
        return products
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get products: {str(e)}"
        )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    product_service: ProductService = Depends(get_product_service)
):
    """Отримання товару за ID"""
    product = await product_service.get_product(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    product_service: ProductService = Depends(get_product_service)
):
    """Оновлення товару"""
    try:
        product = await product_service.update_product(product_id, product_data)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        return product
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Product update failed: {str(e)}"
        )


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    product_service: ProductService = Depends(get_product_service)
):
    """Видалення товару (м'яке видалення)"""
    try:
        result = await product_service.delete_product(product_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        return {"message": "Product deleted successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Product deletion failed: {str(e)}"
        )
