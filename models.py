from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, doctor, pharmacy, diagnostic

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    avatar = db.Column(db.String(200), nullable=True)  # Store the path to the avatar image
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    contact = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    admission_date = db.Column(db.DateTime, default=datetime.utcnow)
    diagnosis = db.Column(db.String(200))
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
class Bed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bed_number = db.Column(db.String(10), unique=True, nullable=False)
    ward = db.Column(db.String(50), nullable=False)
    is_occupied = db.Column(db.Boolean, default=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=True)
    
# In models.py
class Medication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(200))
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    prescribed_date = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'dispensed'
    dispensed_date = db.Column(db.DateTime, nullable=True)
    dispensed_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    patient = db.relationship('Patient', backref=db.backref('medications', lazy=True))
    pharmacist = db.relationship('User', backref=db.backref('dispensed_medications', lazy=True))

class MedicalNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    patient = db.relationship('Patient', backref=db.backref('medical_notes', lazy=True, order_by='MedicalNote.created_at.desc()'))
    doctor = db.relationship('User', backref=db.backref('medical_notes', lazy=True))

class DiagnosticTest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    test_name = db.Column(db.String(100), nullable=False)
    test_description = db.Column(db.Text, nullable=True)
    test_date = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.String(20), default='pending')  # pending, completed
    result = db.Column(db.Text, nullable=True)
    result_date = db.Column(db.DateTime, nullable=True)
    
    patient = db.relationship('Patient', backref=db.backref('diagnostic_tests', lazy=True))
    doctor = db.relationship('User', backref=db.backref('ordered_tests', lazy=True))


    
