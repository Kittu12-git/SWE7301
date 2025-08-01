# main.py

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from pydantic import BaseModel
from typing import List

# Database setup
DATABASE_URL = "sqlite:///./reporting_system.db"  # Use PostgreSQL for production
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# ------------------- Models -------------------
class Agency(Base):
    __tablename__ = "agencies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text)

class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    check_type = Column(String)
    result = Column(Text)
    reference_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    agency_id = Column(Integer, ForeignKey("agencies.id"))
    agency = relationship("Agency")

# Create tables
Base.metadata.create_all(bind=engine)

# ------------------- Schemas -------------------
class AgencyCreate(BaseModel):
    name: str
    description: str

class AgencyOut(BaseModel):
    id: int
    name: str
    description: str
    class Config:
        orm_mode = True

class ReportCreate(BaseModel):
    name: str
    check_type: str
    result: str
    reference_id: str
    agency_id: int

class ReportOut(BaseModel):
    id: int
    name: str
    check_type: str
    result: str
    reference_id: str
    created_at: datetime
    agency: AgencyOut
    class Config:
        orm_mode = True

# ------------------- App Setup -------------------
app = FastAPI(title="Reporting System API", version="1.0.0")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------- Routes -------------------

@app.post("/agencies/", response_model=AgencyOut, status_code=201)
def create_agency(agency: AgencyCreate, db: Session = Depends(get_db)):
    db_agency = Agency(**agency.dict())
    db.add(db_agency)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Agency with this name already exists")
    db.refresh(db_agency)
    return db_agency

@app.get("/agencies/", response_model=List[AgencyOut])
def list_agencies(db: Session = Depends(get_db)):
    return db.query(Agency).all()

@app.post("/reports/", response_model=ReportOut, status_code=201)
def create_report(report: ReportCreate, db: Session = Depends(get_db)):
    db_report = Report(**report.dict())
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report

@app.get("/reports/", response_model=List[ReportOut])
def get_reports(db: Session = Depends(get_db)):
    return db.query(Report).all()

@app.get("/reports/{report_id}", response_model=ReportOut)
def get_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

@app.put("/reports/{report_id}", response_model=ReportOut)
def update_report(report_id: int, updated: ReportCreate, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    for key, value in updated.dict().items():
        setattr(report, key, value)
    db.commit()
    db.refresh(report)
    return report

@app.delete("/reports/{report_id}", status_code=200)
def delete_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    db.delete(report)
    db.commit()
    return {"detail": "Report deleted successfully"}
