routes_code = '''from flask import Blueprint, request, jsonify
from app import db
from app.models import Doctor, Patient, Slot, Appointment
from datetime import datetime

bp = Blueprint('api', __name__, url_prefix='/api')

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

@bp.route('/slots', methods=['POST'])
def create_slot():
    data = request.json
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

@bp.route('/appointments', methods=['POST'])
def create_appointment():
    data = request.json
    slot = Slot.query.get_or_404(data['slot_id'])
    if not slot.is_available:
        return jsonify({'error': 'Slot already booked'}), 409
    appointment = Appointment(patient_id=data['patient_id'], slot_id=data['slot_id'], doctor_id=data['doctor_id'], reason=data['reason'])
    slot.is_available = False
    db.session.add(appointment)
    db.session.commit()
    return jsonify(appointment.to_dict()), 201

@bp.route('/appointments', methods=['GET'])
def get_appointments():
    appointments = Appointment.query.all()
    return jsonify([a.to_dict() for a in appointments])

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

with open('app/routes.py', 'w') as f:
    f.write(routes_code)

print("✅ routes.py recréé avec succès!")