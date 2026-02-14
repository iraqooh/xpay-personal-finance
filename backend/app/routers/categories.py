from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List

from app.schemas.category import CategoryCreate, CategoryRead
from app.models import Category, User, Transaction
from app.dependencies import get_db, get_current_user, get_category_or_404

router = APIRouter(prefix="/categories", tags=["categories"])

@router.post("/", response_model=CategoryRead, status_code=201)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_category = Category(
        **category.model_dump(),
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.get("/", response_model=List[CategoryRead])
def get_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Category).all()

@router.get("/{category_id}", response_model=CategoryRead)
def get_category(category: Category = Depends(get_category_or_404)):
    return category


@router.put("/{category_id}", response_model=CategoryRead)
def update_category(
    update_data: CategoryCreate,
    category: Category = Depends(get_category_or_404),
    db: Session = Depends(get_db)
):
    if category.user_id is None:
        raise HTTPException(403, "Cannot modify global categories")
    
    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(category, key, value)
    
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=204)
def delete_category(
    category: Category = Depends(get_category_or_404),
    db: Session = Depends(get_db)
):
    if category.user_id is None:
        raise HTTPException(403, "Cannot delete global categories")
    
    # Optional: check if used in transactions
    if db.query(Transaction).filter(Transaction.category_id == category.id).first():
        raise HTTPException(409, "Category is in use")
    
    db.delete(category)
    db.commit()
    return Response(status_code=204)