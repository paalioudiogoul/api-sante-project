import os

# Contenu config.py
config_content = '''import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///sante.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'dev-secret-key-change-in-prod'
'''

# Contenu app/__init__.py
init_content = '''from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
    
    from app.routes import bp
    app.register_blueprint(bp)
    
    return app
'''

# Contenu app/models.py
models_content = '''from app import db
from datetime import datetime

class Doctor(db.Model):
    __tablename__ = 'doctors'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialty = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    
    slots = db.relationship('Slot', backref='doctor', lazy=True, cascade='all, delete-orphan')
    appointments = db.relationship('Appointment', backref='doctor', lazy=True)
    
    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'specialty': self.specialty, 'email': self.email}

class Patient(db.Model):
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    
    appointments = db.relationship('Appointment', backref='patient', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'email': self.email, 'date_of_birth': self.date_of_birth.isoformat()}

class Slot(db.Model):
    __tablename__ = 'slots'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    
    appointments = db.relationship('Appointment', backref='slot', lazy=True)
    
    def to_dict(self):
        return {'id': self.id, 'doctor_id': self.doctor_id, 'start_time': self.start_time.isoformat(), 'end_time': self.end_time.isoformat(), 'is_available': self.is_available}

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    slot_id = db.Column(db.Integer, db.ForeignKey('slots.id'), nullable=False)
    reason = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='confirmed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {'id': self.id, 'patient_id': self.patient_id, 'slot_id': self.slot_id, 'reason': self.reason, 'status': self.status, 'created_at': self.created_at.isoformat()}
'''

# Contenu app/routes.py
routes_content = '''from flask import Blueprint, request, jsonify
from app import db
from app.models import Doctor, Patient, Slot, Appointment
from datetime import datetime, timedelta

bp = Blueprint('api', __name__, url_prefix='/api')

# Routes Doctor
@bp.route('/doctors', methods=['POST'])
def create_doctor():
    data = request.json
    doctor = Doctor(name=data['name'], specialty=data['specialty'], email=data['email'])
    db.session.add(doctor)
    db.session.commit()
    return jsonify(doctor.to_dict()), 201

@bp.route('/doctors', methods=['GET'])
def get_doctors():
    doctors = Doctor.query.all()
    return jsonify([d.to_dict() for d in doctors])

@bp.route('/doctors/<int:id>', methods=['GET'])
def get_doctor(id):
    doctor = Doctor.query.get_or_404(id)
    return jsonify(doctor.to_dict())

# Routes Patient
@bp.route('/patients', methods=['POST'])
def create_patient():
    data = request.json
    patient = Patient(name=data['name'], email=data['email'], date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date())
    db.session.add(patient)
    db.session.commit()
    return jsonify(patient.to_dict()), 201

@bp.route('/patients', methods=['GET'])
def get_patients():
    patients = Patient.query.all()
    return jsonify([p.to_dict() for p in patients])

@bp.route('/patients/<int:id>', methods=['GET'])
def get_patient(id):
    patient = Patient.query.get_or_404(id)
    return jsonify(patient.to_dict())

# Routes Slot
@bp.route('/slots', methods=['POST'])
def create_slot():
    data = request.json
    doctor = Doctor.query.get_or_404(data['doctor_id'])
    start = datetime.fromisoformat(data['start_time'])
    end = datetime.fromisoformat(data['end_time'])
    
    duration = (end - start).total_seconds() / 60
    if duration < 15 or duration > 120:
        return jsonify({'error': 'Duration must be between 15 and 120 minutes'}), 400
    
    slot = Slot(doctor_id=data['doctor_id'], start_time=start, end_time=end)
    db.session.add(slot)
    db.session.commit()
    return jsonify(slot.to_dict()), 201

@bp.route('/slots', methods=['GET'])
def get_slots():
    slots = Slot.query.all()
    return jsonify([s.to_dict() for s in slots])

# Routes Appointment
@bp.route('/appointments', methods=['POST'])
def create_appointment():
    data = request.json
    slot = Slot.query.get_or_404(data['slot_id'])
    
    if not slot.is_available:
        return jsonify({'error': 'Slot already booked'}), 409
    
    appointment = Appointment(patient_id=data['patient_id'], slot_id=data['slot_id'], reason=data['reason'])
    slot.is_available = False
    
    db.session.add(appointment)
    db.session.commit()
    return jsonify(appointment.to_dict()), 201

@bp.route('/appointments/<int:id>', methods=['DELETE'])
def cancel_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    
    time_until = appointment.slot.start_time - datetime.utcnow()
    if time_until.total_seconds() < 86400:
        return jsonify({'error': 'Cannot cancel within 24 hours'}), 400
    
    appointment.status = 'cancelled'
    appointment.slot.is_available = True
    
    db.session.commit()
    return jsonify(appointment.to_dict())
'''

# Contenu app.py
app_content = '''from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
'''

# Crée les fichiers
with open('config.py', 'w') as f:
    f.write(config_content)

with open('app/__init__.py', 'w') as f:
    f.write(init_content)

with open('app/models.py', 'w') as f:
    f.write(models_content)

with open('app/routes.py', 'w') as f:
    f.write(routes_content)

with open('app.py', 'w') as f:
    f.write(app_content)

print("✅ Tous les fichiers créés avec succès!")