from app import create_app, db
from app.models import Appointment

app = create_app()

with app.app_context():
    apt = Appointment(patient_id=1, slot_id=1, doctor_id=1, reason="Test")
    db.session.add(apt)
    db.session.commit()
    print(f"✅ Appointment créé : ID={apt.id}")