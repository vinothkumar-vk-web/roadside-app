"""
Database Models & Pydantic Schemas for Malumichampatti Roadside Assistance MVP
"""
import enum
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, Boolean, Float, Integer, DateTime, Enum as SQLEnum, ForeignKey, Text
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field
from database import Base

# Enums
class ServiceType(str, enum.Enum):
    MECHANIC = "mechanic"
    TOWING = "towing"
    FUEL_DELIVERY = "fuel_delivery"

class VerificationStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"

class RequestStatus(str, enum.Enum):
    REQUESTED = "requested"
    PARTNER_NOTIFIED = "partner_notified"
    VOICE_ESCALATED = "voice_escalated"
    SMS_ESCALATED = "sms_escalated"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_PARTNERS_AVAILABLE = "no_partners_available"

# Service Zone Model (Supports multi-city expansion)
class ServiceZone(Base):
    __tablename__ = "service_zones"
    id = Column(Integer, primary_key=True, index=True)
    city_name = Column(String(100), nullable=False) # e.g. "Coimbatore"
    zone_name = Column(String(100), nullable=False, unique=True) # e.g. "Malumichampatti"
    center_latitude = Column(Float, nullable=False)
    center_longitude = Column(Float, nullable=False)
    radius_km = Column(Float, default=10.0)
    is_active = Column(Boolean, default=True)

# Partner Model
class Partner(Base):
    __tablename__ = "partners"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name = Column(String(150), nullable=False)
    phone_number = Column(String(15), unique=True, nullable=False)
    is_phone_verified = Column(Boolean, default=False)
    photo_url = Column(Text, nullable=True)
    id_proof_url = Column(Text, nullable=True)
    years_of_experience = Column(Integer, default=0)
    
    # Location
    shop_latitude = Column(Float, nullable=False)
    shop_longitude = Column(Float, nullable=False)
    live_latitude = Column(Float, nullable=True)
    live_longitude = Column(Float, nullable=True)
    is_live_location = Column(Boolean, default=False)
    zone_id = Column(Integer, ForeignKey("service_zones.id"), nullable=True)

    # Availability & Verification
    verification_status = Column(SQLEnum(VerificationStatus), default=VerificationStatus.PENDING)
    is_online = Column(Boolean, default=False)
    rating = Column(Float, nullable=True)
    total_ratings_count = Column(Integer, default=0)
    fcm_token = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    services = relationship("PartnerService", back_populates="partner", cascade="all, delete-orphan")

class PartnerService(Base):
    __tablename__ = "partner_services"
    id = Column(Integer, primary_key=True, index=True)
    partner_id = Column(String, ForeignKey("partners.id"))
    service_type = Column(SQLEnum(ServiceType), nullable=False)
    
    partner = relationship("Partner", back_populates="services")

# Assistance Request Model
class AssistanceRequest(Base):
    __tablename__ = "assistance_requests"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_phone = Column(String(15), nullable=False)
    service_type = Column(SQLEnum(ServiceType), nullable=False)
    customer_latitude = Column(Float, nullable=False)
    customer_longitude = Column(Float, nullable=False)
    landmark = Column(String(255), nullable=True)
    
    assigned_partner_id = Column(String, ForeignKey("partners.id"), nullable=True)
    status = Column(SQLEnum(RequestStatus), default=RequestStatus.REQUESTED)
    zone_id = Column(Integer, ForeignKey("service_zones.id"))
    
    escalation_step = Column(Integer, default=0) # 1: Push, 2: Voice, 3: SMS, 4: Reassign
    attempted_partner_ids = Column(Text, default="") # Comma-separated list of attempted partners
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ----------------- PYDANTIC SCHEMAS -----------------

class PartnerRegisterRequest(BaseModel):
    full_name: str
    phone_number: str
    photo_url: Optional[str] = None
    id_proof_url: Optional[str] = None
    service_types: List[ServiceType]
    years_of_experience: int = Field(ge=0)
    shop_latitude: float
    shop_longitude: float
    is_live_location: bool = False
    zone_name: str = "Malumichampatti"

class PartnerResponse(BaseModel):
    id: str
    full_name: str
    phone_number: str
    verification_status: VerificationStatus
    is_online: bool
    rating: Optional[float]
    services: List[ServiceType]

    class Config:
        from_attributes = True

class ServiceRequestCreate(BaseModel):
    customer_phone: str
    service_type: ServiceType
    latitude: float
    longitude: float
    landmark: Optional[str] = None
    zone_name: str = "Malumichampatti"

class AdminVerifyPartnerRequest(BaseModel):
    partner_id: str
    status: VerificationStatus

# System Dynamic Pricing & Admin Control Model
class SystemPricingConfig(Base):
    __tablename__ = "system_pricing_config"
    id = Column(Integer, primary_key=True, index=True)
    mechanic_base_fee = Column(Float, default=199.0)
    towing_base_fee = Column(Float, default=799.0)
    towing_per_km_fee = Column(Float, default=45.0)
    fuel_delivery_service_fee = Column(Float, default=99.0)
    platform_commission_percent = Column(Float, default=15.0)
    night_surge_multiplier = Column(Float, default=1.25)
    night_surge_enabled = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PricingConfigUpdate(BaseModel):
    mechanic_base_fee: float = Field(ge=0.0)
    towing_base_fee: float = Field(ge=0.0)
    towing_per_km_fee: float = Field(ge=0.0)
    fuel_delivery_service_fee: float = Field(ge=0.0)
    platform_commission_percent: float = Field(ge=0.0, le=50.0)
    night_surge_multiplier: float = Field(ge=1.0, le=3.0)
    night_surge_enabled: bool = False

class PricingConfigResponse(BaseModel):
    mechanic_base_fee: float
    towing_base_fee: float
    towing_per_km_fee: float
    fuel_delivery_service_fee: float
    platform_commission_percent: float
    night_surge_multiplier: float
    night_surge_enabled: bool

    class Config:
        from_attributes = True

