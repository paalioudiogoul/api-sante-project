from app import create_app, db
from app.models import Patient, Appointment

app = create_app()

# Teste juste les données
with app.app_context():
    patient = Patient.query.get(1)
    if patient:
        appointments = Appointment.query.filter_by(patient_id=1).all()
        print(f"Patient {patient.name} a {len(appointments)} rendez-vous:")
        for apt in appointments:
            print(f"  - RDV ID {apt.id}, Slot {apt.slot_id}, Status: {apt.status}")