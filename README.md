# API Santé - Téléconsultation

## Endpoints Fonctionnels

### Doctor
- POST /api/doctors - Créer doctor
- GET /api/doctors - Lister doctors
- GET /api/doctors/<id> - Détail doctor

### Patient  
- POST /api/patients - Créer patient
- GET /api/patients - Lister patients
- GET /api/patients/<id> - Détail patient
- GET /api/patients/<id>/appointments - RDV du patient

### Slot
- POST /api/slots - Créer créneau (validation 15-120 min)
- GET /api/slots - Lister créneaux

### Appointment
- POST /api/appointments - Réserver (409 si déjà pris)
- DELETE /api/appointments/<id> - Annuler (24h avant)
- GET /api/appointments - Tous les RDV
- GET /api/doctors/<id>/appointments - RDV du médecin

## Règles Métier Implémentées ✅

✅ Durée créneau : 15-120 minutes
✅ Créneau réservé = 409 Conflict
✅ Annulation jusqu'à 24h avant
✅ Visibilité patient (GET /api/patients/<id>/appointments)
✅ Visibilité médecin (GET /api/doctors/<id>/appointments)

## Tests Validés

curl http://127.0.0.1:5000/api/doctors
curl http://127.0.0.1:5000/api/patients
curl http://127.0.0.1:5000/api/slots
curl http://127.0.0.1:5000/api/appointments