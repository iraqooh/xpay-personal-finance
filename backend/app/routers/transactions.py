from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Literal
from uuid import UUID
from datetime import date
from math import ceil

from app.schemas import TransactionCreate, TransactionRead, PaginatedResponse, PaginationMeta
from app.models import Transaction, User
from app.dependencies import get_db, get_current_user, get_transaction_or_404

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.post("/", response_model=TransactionRead, status_code=201)
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_transaction = Transaction(
        **transaction.model_dump(),
        user_id=current_user.id
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@router.get("/", response_model=PaginatedResponse[TransactionRead])
def get_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category_id: Optional[UUID] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Transaction).filter(Transaction.user_id == current_user.id)
    
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    if date_from:
        query = query.filter(Transaction.date >= date_from)
    if date_to:
        query = query.filter(Transaction.date <= date_to)
    
    total = query.count()
    
    items = (
        query
        .order_by(Transaction.date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    current_page = (skip // limit) + 1 if limit > 0 else 1
    total_pages = ceil(total / limit) if limit > 0 else 1

    meta = PaginationMeta(
        total=total,
        skip=skip,
        limit=limit,
        page=current_page,
        pages=total_pages,
        has_next=current_page < total_pages,
        has_prev=current_page > 1
    )
    
    return PaginatedResponse(items=items, meta=meta)

@router.get("/{transaction_id}", response_model=TransactionRead)
def get_transaction(tx: Transaction = Depends(get_transaction_or_404)):
    return tx


@router.put("/{transaction_id}", response_model=TransactionRead)
def update_transaction(
    update_data: TransactionCreate,
    tx: Transaction = Depends(get_transaction_or_404),
    db: Session = Depends(get_db)
):
    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(tx, key, value)
    
    db.commit()
    db.refresh(tx)
    return tx


@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(
    tx: Transaction = Depends(get_transaction_or_404),
    db: Session = Depends(get_db)
):
    db.delete(tx)
    db.commit()
    return Response(status_code=204)