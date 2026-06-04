"""
Data models for the Kahatayn Orphan Family Management System.
Using SQLAlchemy ORM for database agnostic design.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Date, Boolean, Float, Text, DateTime
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

# ===========================================
# MASTER DATA TABLES
# ===========================================

class City(Base):
    """City/Location master table."""
    __tablename__ = 'cities'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    
    persons = relationship("Person", back_populates="city")

class School(Base):
    """School master table."""
    __tablename__ = 'schools'
    id = Column(Integer, primary_key=True)
    name = Column(String(150), unique=True, nullable=False)
    location = Column(String(200))
    contact_phone = Column(String(20))
    
    orphans = relationship("Orphan", back_populates="school")

class DocumentType(Base):
    """Document types master table."""
    __tablename__ = 'document_types'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    
    documents = relationship("Document", back_populates="doc_type")

# ===========================================
# CORE ENTITIES
# ===========================================

class Person(Base):
    """Core person entity - parent for all individual records."""
    __tablename__ = 'persons'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    middle_name = Column(String(50))
    last_name = Column(String(50), nullable=False)
    gender = Column(String(10))  # M/F
    birth_date = Column(Date)
    national_id = Column(String(20), unique=True)
    city_id = Column(Integer, ForeignKey('cities.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    city = relationship("City", back_populates="persons")
    contact = relationship("Contact", uselist=False, back_populates="person")
    family_reps = relationship("Representative", back_populates="person")
    orphan_profile = relationship("Orphan", uselist=False, back_populates="person")
    donor_profile = relationship("Donor", uselist=False, back_populates="person")
    volunteer_profile = relationship("Volunteer", uselist=False, back_populates="person")
    system_user = relationship("SystemUser", uselist=False, back_populates="person")

class Contact(Base):
    """Contact information for persons."""
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('persons.id'), nullable=False)
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(String(200))
    
    person = relationship("Person", back_populates="contact")

class Representative(Base):
    """Family representatives (guardians, parents)."""
    __tablename__ = 'representatives'
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('persons.id'), nullable=False)
    family_id = Column(Integer, ForeignKey('families.id'), nullable=False)
    role = Column(String(50))  # Father, Mother, Guardian, Relative, etc.
    
    person = relationship("Person", back_populates="family_reps")
    family = relationship("Family", back_populates="representatives")

class Family(Base):
    """Family cases managed by the organization."""
    __tablename__ = 'families'
    id = Column(Integer, primary_key=True)
    family_code = Column(String(50), unique=True, nullable=False)  # e.g., FAM-000001
    status = Column(String(20), default='active')  # active, inactive, completed
    number_of_children = Column(Integer, default=0)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    representatives = relationship("Representative", back_populates="family")
    orphans = relationship("Orphan", back_populates="family")
    assessments = relationship("Assessment", back_populates="family")

class Orphan(Base):
    """Orphan/vulnerable child records."""
    __tablename__ = 'orphans'
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('persons.id'), unique=True, nullable=False)
    family_id = Column(Integer, ForeignKey('families.id'))
    school_id = Column(Integer, ForeignKey('schools.id'))
    health_status = Column(String(100))  # Good, Fair, Special needs, etc.
    is_adult = Column(Boolean, default=False)
    assigned_volunteer_id = Column(Integer, ForeignKey('volunteers.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    person = relationship("Person", back_populates="orphan_profile")
    family = relationship("Family", back_populates="orphans")
    school = relationship("School", back_populates="orphans")
    assigned_volunteer = relationship("Volunteer", back_populates="assigned_orphans")
    sponsorships = relationship("Sponsorship", back_populates="orphan")

class Sponsorship(Base):
    """Sponsorship relationships between volunteers/donors and orphans."""
    __tablename__ = 'sponsorships'
    id = Column(Integer, primary_key=True)
    orphan_id = Column(Integer, ForeignKey('orphans.id'), nullable=False)
    volunteer_id = Column(Integer, ForeignKey('volunteers.id'))
    sponsor_type = Column(String(50))  # Financial, Educational, Health, etc.
    status = Column(String(20), default='active')  # active, paused, completed
    start_date = Column(Date)
    end_date = Column(Date)
    monthly_amount = Column(Float)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    orphan = relationship("Orphan", back_populates="sponsorships")
    volunteer = relationship("Volunteer", back_populates="sponsorships")

class Volunteer(Base):
    """Volunteer records."""
    __tablename__ = 'volunteers'
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('persons.id'), nullable=False)
    volunteer_code = Column(String(50), unique=True, nullable=False)  # e.g., VOL-000001
    join_date = Column(Date)
    status = Column(String(20), default='active')  # active, inactive, terminated
    specialization = Column(String(100))  # Medical, Education, Financial, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    person = relationship("Person", back_populates="volunteer_profile")
    assigned_orphans = relationship("Orphan", back_populates="assigned_volunteer")
    sponsorships = relationship("Sponsorship", back_populates="volunteer")
    activities = relationship("VolunteerActivity", back_populates="volunteer")

class Donor(Base):
    """Donor/contributor records."""
    __tablename__ = 'donors'
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('persons.id'))
    donor_code = Column(String(50), unique=True, nullable=False)  # e.g., DONOR-000001
    donor_type = Column(String(50))  # Individual, Organization, etc.
    total_donated = Column(Float, default=0)
    join_date = Column(Date)
    status = Column(String(20), default='active')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    person = relationship("Person", back_populates="donor_profile")

class Document(Base):
    """Document storage and tracking."""
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True)
    doc_type_id = Column(Integer, ForeignKey('document_types.id'))
    person_id = Column(Integer, ForeignKey('persons.id'))
    file_path = Column(String(255))
    issue_date = Column(Date)
    expiry_date = Column(Date)
    reference = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    doc_type = relationship("DocumentType", back_populates="documents")

class Assessment(Base):
    """Family financial assessment records."""
    __tablename__ = 'assessments'
    id = Column(Integer, primary_key=True)
    family_id = Column(Integer, ForeignKey('families.id'), nullable=False)
    assessment_date = Column(Date, default=lambda: datetime.utcnow().date())
    
    # Income sources
    salary = Column(Float, default=0)
    side_income = Column(Float, default=0)
    gov_support_daman = Column(Float, default=0)  # Daman social support
    gov_support_tadamun = Column(Float, default=0)  # Tadamun family support
    gov_support_child = Column(Float, default=0)  # Child allowance
    
    # Expenses
    rent = Column(Float, default=0)
    utilities = Column(Float, default=0)
    food = Column(Float, default=0)
    education = Column(Float, default=0)
    health = Column(Float, default=0)
    other_expenses = Column(Float, default=0)
    
    # Calculations
    total_income = Column(Float, default=0)
    total_expenses = Column(Float, default=0)
    net_income = Column(Float, default=0)
    is_accepted = Column(Boolean, default=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    family = relationship("Family", back_populates="assessments")

class VolunteerActivity(Base):
    """Volunteer activity logs."""
    __tablename__ = 'volunteer_activities'
    id = Column(Integer, primary_key=True)
    volunteer_id = Column(Integer, ForeignKey('volunteers.id'), nullable=False)
    activity_type = Column(String(100))  # Visit, Assessment, Report, Call, etc.
    description = Column(Text)
    activity_date = Column(Date, default=lambda: datetime.utcnow().date())
    hours_spent = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    volunteer = relationship("Volunteer", back_populates="activities")

class SystemUser(Base):
    """System users for authentication and authorization."""
    __tablename__ = 'system_users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # manager, volunteer, staff
    person_id = Column(Integer, ForeignKey('persons.id'))
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    person = relationship("Person", back_populates="system_user")
