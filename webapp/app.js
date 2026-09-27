// Configuration de l'API
const API_URL = 'http://127.0.0.1:5000/api';

// Variables globales
let doctors = [];
let selectedDoctorId = null;
let slots = [];
let currentPatientId = null;

// ===== GESTION DES PAGES =====
function showPage(pageName) {
    // Masquer toutes les pages
    const pages = document.querySelectorAll('.page');
    pages.forEach(page => page.classList.remove('active'));

    // Afficher la page sélectionnée
    const selectedPage = document.getElementById(pageName);
    if (selectedPage) {
        selectedPage.classList.add('active');
    }

    // Charger les données selon la page
    if (pageName === 'doctors') {
        loadDoctors();
    } else if (pageName === 'book') {
        loadDoctorsForBooking();
    }
}

// ===== PAGE: LISTE DES MÉDECINS =====
async function loadDoctors() {
    const doctorsList = document.getElementById('doctorsList');
    doctorsList.innerHTML = '<p class="loading">Chargement des médecins...</p>';

    try {
        const response = await fetch(`${API_URL}/doctors`);
        doctors = await response.json();

        if (doctors.length === 0) {
            doctorsList.innerHTML = '<p class="info">Aucun médecin disponible</p>';
            return;
        }

        doctorsList.innerHTML = '';
        doctors.forEach(doctor => {
            const doctorCard = document.createElement('div');
            doctorCard.className = 'doctor-card';
            doctorCard.innerHTML = `
                <h3>👨‍⚕️ ${doctor.name}</h3>
                <p class="doctor-specialty">${doctor.specialty}</p>
                <p><strong>Email:</strong> ${doctor.email}</p>
                <button class="btn" onclick="selectDoctorAndShowSlots(${doctor.id})">
                    Voir les créneaux
                </button>
            `;
            doctorsList.appendChild(doctorCard);
        });
    } catch (error) {
        console.error('Erreur:', error);
        doctorsList.innerHTML = '<p class="message error">Erreur lors du chargement des médecins</p>';
    }
}

// ===== PAGE: RÉSERVER UN RDV =====
async function loadDoctorsForBooking() {
    const doctorSelect = document.getElementById('doctorSelect');

    try {
        const response = await fetch(`${API_URL}/doctors`);
        doctors = await response.json();

        doctorSelect.innerHTML = '<option value="">-- Choisir un médecin --</option>';
        doctors.forEach(doctor => {
            const option = document.createElement('option');
            option.value = doctor.id;
            option.textContent = `${doctor.name} (${doctor.specialty})`;
            doctorSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Erreur:', error);
    }
}

async function loadSlots() {
    const doctorSelect = document.getElementById('doctorSelect');
    const slotSelect = document.getElementById('slotSelect');
    selectedDoctorId = doctorSelect.value;

    if (!selectedDoctorId) {
        slotSelect.innerHTML = '<option value="">-- Choisir un créneau --</option>';
        return;
    }

    try {
        const response = await fetch(`${API_URL}/slots`);
        const allSlots = await response.json();

        // Filtrer les créneaux du médecin sélectionné
        slots = allSlots.filter(slot => 
            slot.doctor_id === parseInt(selectedDoctorId) && slot.is_available
        );

        slotSelect.innerHTML = '<option value="">-- Choisir un créneau --</option>';

        if (slots.length === 0) {
            slotSelect.innerHTML += '<option disabled>Aucun créneau disponible</option>';
            return;
        }

        slots.forEach(slot => {
            const option = document.createElement('option');
            option.value = slot.id;
            const startTime = new Date(slot.start_time).toLocaleString('fr-FR');
            const endTime = new Date(slot.end_time).toLocaleTimeString('fr-FR');
            option.textContent = `${startTime} - ${endTime}`;
            slotSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Erreur:', error);
        slotSelect.innerHTML = '<option value="">Erreur lors du chargement</option>';
    }
}

async function bookAppointment() {
    const patientName = document.getElementById('patientName').value;
    const patientEmail = document.getElementById('patientEmail').value;
    const patientDob = document.getElementById('patientDob').value;
    const slotId = document.getElementById('slotSelect').value;
    const reason = document.getElementById('reason').value;
    const messageDiv = document.getElementById('bookMessage');

    // Validation
    if (!patientName || !patientEmail || !patientDob || !slotId || !reason) {
        messageDiv.className = 'message error';
        messageDiv.textContent = '❌ Veuillez remplir tous les champs';
        return;
    }

    try {
        // Créer le patient
        let patientResponse = await fetch(`${API_URL}/patients`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: patientName,
                email: patientEmail,
                date_of_birth: patientDob
            })
        });

        let patientData = await patientResponse.json();
        let patientId = patientData.id;

        // Si le patient existe déjà, récupérer son ID
        if (!patientId) {
            const patientsResponse = await fetch(`${API_URL}/patients`);
            const patients = await patientsResponse.json();
            const existingPatient = patients.find(p => p.email === patientEmail);
            if (existingPatient) {
                patientId = existingPatient.id;
            }
        }

        // Créer le rendez-vous
        const appointmentResponse = await fetch(`${API_URL}/appointments`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                patient_id: patientId,
                slot_id: parseInt(slotId),
                doctor_id: selectedDoctorId,
                reason: reason
            })
        });

        if (appointmentResponse.status === 409) {
            messageDiv.className = 'message error';
            messageDiv.textContent = '❌ Ce créneau est déjà réservé';
            return;
        }

        if (!appointmentResponse.ok) {
            throw new Error('Erreur lors de la création du RDV');
        }

        // Succès
        messageDiv.className = 'message success';
        messageDiv.textContent = '✅ Rendez-vous réservé avec succès! Vérifiez vos emails.';

        // Réinitialiser le formulaire
        document.getElementById('patientName').value = '';
        document.getElementById('patientEmail').value = '';
        document.getElementById('patientDob').value = '';
        document.getElementById('slotSelect').value = '';
        document.getElementById('reason').value = '';

    } catch (error) {
        console.error('Erreur:', error);
        messageDiv.className = 'message error';
        messageDiv.textContent = '❌ Erreur lors de la réservation';
    }
}

// ===== PAGE: MES RENDEZ-VOUS =====
async function loadMyAppointments() {
    const patientEmail = document.getElementById('myPatientEmail').value;
    const appointmentsList = document.getElementById('appointmentsList');

    if (!patientEmail) {
        appointmentsList.innerHTML = '<p class="message error">Veuillez entrer votre email</p>';
        return;
    }

    appointmentsList.innerHTML = '<p class="loading">Chargement de vos rendez-vous...</p>';

    try {
        // Récupérer tous les patients
        const patientsResponse = await fetch(`${API_URL}/patients`);
        const patients = await patientsResponse.json();
        const patient = patients.find(p => p.email === patientEmail);

        if (!patient) {
            appointmentsList.innerHTML = '<p class="message error">Aucun patient trouvé avec cet email</p>';
            return;
        }

        // Récupérer les rendez-vous du patient
        const appointmentsResponse = await fetch(`${API_URL}/patients/${patient.id}/appointments`);
        const appointments = await appointmentsResponse.json();

        if (appointments.length === 0) {
            appointmentsList.innerHTML = '<p class="info">Vous n\'avez aucun rendez-vous réservé</p>';
            return;
        }

        appointmentsList.innerHTML = '';

        appointments.forEach(appointment => {
            const appointmentCard = document.createElement('div');
            appointmentCard.className = 'appointment-card';

            const startTime = new Date(appointment.start_time).toLocaleString('fr-FR');
            const status = appointment.status === 'confirmed' ? '✅ Confirmé' : '❌ ' + appointment.status;

            appointmentCard.innerHTML = `
                <h3>Rendez-vous avec ${appointment.doctor_name}</h3>
                <div class="appointment-details">
                    <div class="detail">
                        <div class="detail-label">Médecin</div>
                        <div class="detail-value">${appointment.doctor_name}</div>
                    </div>
                    <div class="detail">
                        <div class="detail-label">Spécialité</div>
                        <div class="detail-value">${appointment.specialty}</div>
                    </div>
                    <div class="detail">
                        <div class="detail-label">Date & Heure</div>
                        <div class="detail-value">${startTime}</div>
                    </div>
                    <div class="detail">
                        <div class="detail-label">Raison</div>
                        <div class="detail-value">${appointment.reason}</div>
                    </div>
                    <div class="detail">
                        <div class="detail-label">Statut</div>
                        <div class="detail-value">${status}</div>
                    </div>
                </div>
                <div class="appointment-actions">
                    <button class="btn btn-danger" onclick="cancelAppointment(${appointment.id})">
                        Annuler le RDV
                    </button>
                </div>
            `;

            appointmentsList.appendChild(appointmentCard);
        });

    } catch (error) {
        console.error('Erreur:', error);
        appointmentsList.innerHTML = '<p class="message error">Erreur lors du chargement des rendez-vous</p>';
    }
}

async function cancelAppointment(appointmentId) {
    if (!confirm('Êtes-vous sûr de vouloir annuler ce rendez-vous?')) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/appointments/${appointmentId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            alert('✅ Rendez-vous annulé avec succès');
            const patientEmail = document.getElementById('myPatientEmail').value;
            if (patientEmail) {
                loadMyAppointments();
            }
        } else {
            const error = await response.json();
            alert('❌ ' + (error.message || 'Erreur lors de l\'annulation'));
        }
    } catch (error) {
        console.error('Erreur:', error);
        alert('❌ Erreur lors de l\'annulation');
    }
}

// ===== HELPER FUNCTION =====
async function selectDoctorAndShowSlots(doctorId) {
    selectedDoctorId = doctorId;
    // Rediriger vers la page de réservation
    showPage('book');
    
    // Sélectionner le médecin dans le dropdown
    document.getElementById('doctorSelect').value = doctorId;
    loadSlots();
}

// Charger la page d'accueil au démarrage
window.addEventListener('load', () => {
    showPage('home');
});
