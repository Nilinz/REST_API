from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.database import models, db
from app.schemas import ContactResponse, ContactBase, ContactCreate, ContactUpdate, Contact, ContactSearch, ContactBirthdaySearch
from app.database.db import get_db
from app.routes import auth

router = APIRouter(prefix="/contacts", tags=["contacts"])

@router.post("/contacts/", response_model=Contact, description='No more than 10 requests per minute', dependencies=[Depends(RateLimiter(times=10, seconds=60))], status_code=status.HTTP_201_CREATED)
def create_contact(contact: ContactCreate, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_contact = models.Contact(**contact.dict())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

@router.get("/contacts/", response_model=ContactResponse)
def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    contacts = db.query(models.Contact).offset(skip).limit(limit).all()
    return {"contacts": contacts}

@router.get("/contacts/{contact_id}", response_model=Contact)
def read_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@router.put("/contacts/{contact_id}", response_model=Contact)
def update_contact(contact_id: int, contact: ContactUpdate, db: Session = Depends(get_db)):
    db_contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")

    for var, value in vars(contact).items():
        setattr(db_contact, var, value) if value else None

    db.commit()
    db.refresh(db_contact)
    return db_contact

@router.delete("/contacts/{contact_id}", response_model=Contact)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    db.delete(contact)
    db.commit()
    return contact

@router.get("/contacts/search/", response_model=List[Contact])
def search_contacts(query: str, db: Session = Depends(get_db)):
    contacts = db.query(models.Contact).filter(
        (models.Contact.first_name.ilike(f"%{query}%")) |
        (models.Contact.last_name.ilike(f"%{query}%")) |
        (models.Contact.email.ilike(f"%{query}%"))
    ).all()
    return contacts

@router.get("/contacts/birthday/", response_model=List[Contact])
def upcoming_birthdays(days: int = 7, db: Session = Depends(get_db)):
    today = db.query(db.func.current_date()).scalar()
    end_date = today + timedelta(days=days)
    contacts = db.query(models.Contact).filter(
        (db.func.extract('month', models.Contact.birthday) == db.func.extract('month', today)) &
        (db.func.extract('day', models.Contact.birthday) <= db.func.extract('day', end_date))
    ).all()
    return contacts
