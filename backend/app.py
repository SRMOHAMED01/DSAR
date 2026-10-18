import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from enum import Enum

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import create_engine, Column, String, DateTime, Enum as SQLEnum, JSON, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
from jose import jwt, JWTError
import io

from dsar_engine import DSAREngine

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://Mohamed:12345@localhost:5432/dsar_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

SECRET_KEY = os.getenv("SECRET_KEY", "dsar-demo-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class RequestStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    rejected = "rejected"


class RequestType(str, Enum):
    access = "access"
    deletion = "deletion"
    rectification = "rectification"


class DSARRequest(Base):
    __tablename__ = "dsar_requests"
    id = Column(String(36), primary_key=True)
    requester_email = Column(String(255), nullable=False)
    requester_name = Column(String(255), nullable=False)
    request_type = Column(SQLEnum(RequestType), nullable=False)
    status = Column(SQLEnum(RequestStatus), default=RequestStatus.pending)
    identifier = Column(String(255), nullable=False)
    identifier_type = Column(String(50), default="email")
    details = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    admin_notes = Column(Text, nullable=True)
    export_path = Column(String(500), nullable=True)


Base.metadata.create_all(bind=engine)


class DSARRequestCreate(BaseModel):
    requester_name: str = Field(..., min_length=2, max_length=255)
    requester_email: EmailStr
    request_type: RequestType
    identifier: str = Field(..., min_length=1, max_length=255)
    identifier_type: str = Field(default="email")
    details: Dict[str, Any] = Field(default={})


class DSARRequestResponse(BaseModel):
    id: str
    requester_name: str
    requester_email: str
    request_type: RequestType
    status: RequestStatus
    identifier: str
    identifier_type: str
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime] = None
    admin_notes: Optional[str] = None

    class Config:
        from_attributes = True


app = FastAPI(title="DSAR API", description="Data Subject Access Request Management API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.post("/api/dsar/requests", response_model=DSARRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_dsar_request(request: DSARRequestCreate, db: Session = Depends(get_db)):
    import uuid

    dsar_req = DSARRequest(
        id=str(uuid.uuid4()),
        requester_name=request.requester_name,
        requester_email=request.requester_email,
        request_type=request.request_type,
        identifier=request.identifier,
        identifier_type=request.identifier_type,
        details=request.details,
    )
    db.add(dsar_req)
    db.commit()
    db.refresh(dsar_req)

    engine = DSAREngine()
    engine.log_audit("request_created", request.identifier, {"request_id": dsar_req.id, "type": request.request_type})

    return dsar_req


@app.get("/api/dsar/requests", response_model=List[DSARRequestResponse])
async def list_dsar_requests(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    requests = db.query(DSARRequest).order_by(DSARRequest.created_at.desc()).offset(skip).limit(limit).all()
    return requests


@app.get("/api/dsar/requests/{request_id}", response_model=DSARRequestResponse)
async def get_dsar_request(request_id: str, db: Session = Depends(get_db)):
    req = db.query(DSARRequest).filter(DSARRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="DSAR request not found")
    return req


@app.post("/api/dsar/requests/{request_id}/process")
async def process_dsar_request(request_id: str, db: Session = Depends(get_db)):
    req = db.query(DSARRequest).filter(DSARRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="DSAR request not found")

    req.status = RequestStatus.processing
    req.updated_at = datetime.utcnow()
    db.commit()

    try:
        dsar_engine = DSAREngine()
        discovered = dsar_engine.discover_data(req.identifier, req.identifier_type)
        export_bytes = dsar_engine.export_data(discovered, export_format="json", mask_data=True)

        export_dir = "/tmp/dsar_exports"
        os.makedirs(export_dir, exist_ok=True)
        export_path = os.path.join(export_dir, f"dsar_{request_id}.json")

        with open(export_path, "wb") as f:
            f.write(export_bytes)

        req.status = RequestStatus.completed
        req.export_path = export_path
        req.processed_at = datetime.utcnow()
        req.updated_at = datetime.utcnow()
        db.commit()

        dsar_engine.log_audit("request_processed", req.identifier, {"request_id": request_id, "records_found": sum(len(v) for v in discovered.values())})
        return {"status": "completed", "records_found": sum(len(v) for v in discovered.values()), "export_path": export_path}
    except Exception as e:
        req.status = RequestStatus.rejected
        req.admin_notes = str(e)
        req.updated_at = datetime.utcnow()
        db.commit()
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@app.get("/api/dsar/requests/{request_id}/export")
async def download_export(request_id: str, format: str = "json", db: Session = Depends(get_db)):
    req = db.query(DSARRequest).filter(DSARRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="DSAR request not found")
    if req.status != RequestStatus.completed or not req.export_path or not os.path.exists(req.export_path):
        raise HTTPException(status_code=400, detail="Export not available")

    with open(req.export_path, "rb") as f:
        content = f.read()

    if format == "csv":
        dsar_engine = DSAREngine()
        discovered = dsar_engine.discover_data(req.identifier, req.identifier_type)
        content = dsar_engine.export_data(discovered, export_format="csv", mask_data=True)

    return StreamingResponse(
        io.BytesIO(content),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename=dsar_{request_id}.{format}"},
    )
