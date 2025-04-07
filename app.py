from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Patient, Bed, Medication, DiagnosticTest, MedicalNote
from config import Config
import time
import datetime





app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.template_filter('nl2br')
def nl2br(value):
    return value.replace('\n', '<br>')
# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'doctor':
                return redirect(url_for('doctor_dashboard'))
            elif user.role == 'pharmacy':
                return redirect(url_for('pharmacy_dashboard'))
            elif user.role == 'diagnostic':
                return redirect(url_for('diagnostic_dashboard'))
        else:
            flash('Invalid username or password')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    
    patients = Patient.query.all()
    beds = Bed.query.all()
    users = User.query.all()
    return render_template('admin/dashboard.html', patients=patients, beds=beds, users=users)


@app.route('/doctor/dashboard')
@login_required
def doctor_dashboard():
    if current_user.role != 'doctor':
        return redirect(url_for('index'))
    
    patients = Patient.query.filter_by(doctor_id=current_user.id).all()
    return render_template('doctor/dashboard.html', patients=patients)

@app.route('/pharmacy/dashboard')
@login_required
def pharmacy_dashboard():
    if current_user.role != 'pharmacy':
        return redirect(url_for('index'))
    
    # Get all medications
    medications = Medication.query.all()
    
    # Get pending medications
    pending_medications = Medication.query.filter_by(status='pending').all()
    
    return render_template('pharmacy/dashboard.html', 
                          medications=medications, 
                          pending_medications=pending_medications)



@app.route('/diagnostic/dashboard')
@login_required
def diagnostic_dashboard():
    if current_user.role != 'diagnostic':
        return redirect(url_for('index'))
    
    # Get all tests
    tests = DiagnosticTest.query.all()
    
    # Get pending tests
    pending_tests = DiagnosticTest.query.filter_by(status='pending').all()
    
    return render_template('diagnostic/dashboard.html', 
                          tests=tests, 
                          pending_tests=pending_tests)


import os
from werkzeug.utils import secure_filename

# Add this configuration
app.config['UPLOAD_FOLDER'] = 'static/img'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/patient/register', methods=['GET', 'POST'])
@login_required
def register_patient():
    if request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age')
        gender = request.form.get('gender')
        contact = request.form.get('contact')
        address = request.form.get('address')
        diagnosis = request.form.get('diagnosis')
        
        # Handle avatar upload
        avatar_path = None
        if 'avatar' in request.files:
            avatar = request.files['avatar']
            print(avatar)

            if avatar and avatar.filename and allowed_file(avatar.filename):
                # Get file extension
                file_ext = avatar.filename.rsplit('.', 1)[1].lower()
                # Create a unique filename
                filename = secure_filename(f"avatar_{int(time.time())}.{file_ext}")
                print(filename)
                
                # Create directory if it doesn't exist
                upload_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
                os.makedirs(upload_path, exist_ok=True)
                
                # Save the file - store only the relative path in the database
                avatar_path = os.path.join('img', filename).replace('\\', '/')
                full_path = os.path.join(app.root_path, 'static', avatar_path)
                avatar.save(full_path)
        
        new_patient = Patient(
            name=name,
            age=age,
            gender=gender,
            contact=contact,
            address=address,
            diagnosis=diagnosis,
            avatar=avatar_path,
            doctor_id=current_user.id if current_user.role == 'doctor' else None
        )
        
        db.session.add(new_patient)
        db.session.commit()
        
        flash('Patient registered successfully')
        return redirect(url_for('admin_dashboard'))
        
    return render_template('patient/register.html')

@app.route('/patient/edit/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def edit_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    
    # Check permissions - only admin or assigned doctor can edit
    if current_user.role != 'admin' and (current_user.role != 'doctor' or patient.doctor_id != current_user.id):
        flash('You do not have permission to edit this patient')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        patient.name = request.form.get('name')
        patient.age = request.form.get('age')
        patient.gender = request.form.get('gender')
        patient.contact = request.form.get('contact')
        patient.address = request.form.get('address')
        patient.diagnosis = request.form.get('diagnosis')

        # Handle avatar upload
        if 'avatar' in request.files:
            avatar = request.files['avatar']
            if avatar and avatar.filename and allowed_file(avatar.filename):
                filename = f"avatar_{int(time.time())}.{avatar.filename.rsplit('.', 1)[1].lower()}"
                filename = secure_filename(filename)
                print(filename)
                avatar_path = f"img/{filename}"  
                print(f"Database path: {avatar_path}")
                
                full_path = os.path.join(app.root_path, 'static', 'img', filename)
                print(f"Full save path: {full_path}")
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                # Save the file
                avatar.save(full_path)
                
                # Update patient record with the new avatar path
                patient.avatar = avatar_path

        db.session.commit()
        flash('Patient information updated successfully')
        return redirect(url_for('patient_details', patient_id=patient.id))
        
    return render_template('patient/edit.html', patient=patient)


@app.route('/bed/manage', methods=['GET', 'POST'])
@login_required
def manage_beds():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        bed_number = request.form.get('bed_number')
        ward = request.form.get('ward')
        
        new_bed = Bed(bed_number=bed_number, ward=ward)
        db.session.add(new_bed)
        db.session.commit()
        
        flash('Bed added successfully')
        
    beds = Bed.query.all()
    return render_template('admin/beds.html', beds=beds)

@app.route('/api/beds')
def get_beds():
    beds = Bed.query.all()
    available = sum(1 for bed in beds if not bed.is_occupied)
    total = len(beds)
    
    return {
        'available': available,
        'total': total,
        'beds': [{'id': bed.id, 'number': bed.bed_number, 'ward': bed.ward, 'occupied': bed.is_occupied} for bed in beds]
    }

# Create database tables
@app.before_first_request
def create_tables():
    db.create_all()
    
    # Create default admin user if not exists
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            password=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()

@app.route('/patient/<int:patient_id>')
@login_required
def patient_details(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    doctor = User.query.get(patient.doctor_id) if patient.doctor_id else None
    bed = Bed.query.filter_by(patient_id=patient.id).first()
    medications = Medication.query.filter_by(patient_id=patient.id).all()
    tests = DiagnosticTest.query.filter_by(patient_id=patient.id).all()
    medical_notes = MedicalNote.query.filter_by(patient_id=patient.id).order_by(MedicalNote.created_at.desc()).all()
    
    return render_template('patient/details.html', 
                          patient=patient, 
                          doctor=doctor,
                          bed=bed,
                          medications=medications,
                          tests=tests,
                          medical_notes=medical_notes)

@app.route('/patient/assign_doctor/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def assign_doctor(patient_id):
    if current_user.role != 'admin':
        flash('Only administrators can assign doctors')
        return redirect(url_for('index'))
    
    patient = Patient.query.get_or_404(patient_id)
    doctors = User.query.filter_by(role='doctor').all()
    
    if request.method == 'POST':
        doctor_id = request.form.get('doctor_id')
        
        if doctor_id:
            patient.doctor_id = doctor_id
            db.session.commit()
            flash(f'Doctor assigned to {patient.name} successfully')
            return redirect(url_for('patient_details', patient_id=patient.id))
    
    return render_template('patient/assign_doctor.html', patient=patient, doctors=doctors)



@app.route('/manage/staff')
@login_required
def manage_staff():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    
    users = User.query.all()
    return render_template('admin/staff.html', users=users)

@app.route('/staff/add', methods=['POST'])
@login_required
def add_staff():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role')
    
    # Check if username already exists
    if User.query.filter_by(username=username).first():
        flash('Username already exists')
        return redirect(url_for('manage_staff'))
    
    new_user = User(
        username=username,
        password=generate_password_hash(password),
        role=role
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    flash('Staff member added successfully')
    return redirect(url_for('manage_staff'))

@app.route('/staff/edit', methods=['POST'])
@login_required
def edit_staff():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    
    staff_id = request.form.get('staff_id')
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role')
    
    user = User.query.get_or_404(staff_id)
    
    # Check if username already exists and it's not the current user
    existing_user = User.query.filter_by(username=username).first()
    if existing_user and existing_user.id != int(staff_id):
        flash('Username already exists')
        return redirect(url_for('manage_staff'))
    
    user.username = username
    user.role = role
    
    if password:
        user.password = generate_password_hash(password)
    
    db.session.commit()
    
    flash('Staff member updated successfully')
    return redirect(url_for('manage_staff'))

@app.route('/staff/delete/<int:staff_id>', methods=['POST'])
@login_required
def delete_staff(staff_id):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(staff_id)
    
    # Prevent deleting yourself
    if user.id == current_user.id:
        flash('You cannot delete your own account')
        return redirect(url_for('manage_staff'))
    
    db.session.delete(user)
    db.session.commit()
    
    flash('Staff member deleted successfully')
    return redirect(url_for('manage_staff'))


@app.route('/bed/assign/<int:bed_id>', methods=['GET', 'POST'])
@login_required
def assign_bed(bed_id):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    
    bed = Bed.query.get_or_404(bed_id)
    
    if bed.is_occupied:
        flash('This bed is already occupied')
        return redirect(url_for('manage_beds'))
    
    if request.method == 'POST':
        patient_id = request.form.get('patient_id')
        patient = Patient.query.get_or_404(patient_id)
        
        # Check if patient already has a bed
        existing_bed = Bed.query.filter_by(patient_id=patient_id).first()
        if existing_bed:
            flash('This patient is already assigned to a bed')
            return redirect(url_for('manage_beds'))
        
        bed.patient_id = patient_id
        bed.is_occupied = True
        db.session.commit()
        
        flash(f'Bed {bed.bed_number} assigned to {patient.name} successfully')
        return redirect(url_for('manage_beds'))
    
    # Get patients without beds
    assigned_patient_ids = [b.patient_id for b in Bed.query.filter(Bed.patient_id.isnot(None)).all()]
    available_patients = Patient.query.filter(~Patient.id.in_(assigned_patient_ids)).all()
    
    return render_template('admin/assign_bed.html', bed=bed, patients=available_patients)

@app.route('/bed/release/<int:bed_id>', methods=['POST'])
@login_required
def release_bed(bed_id):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    
    bed = Bed.query.get_or_404(bed_id)
    
    if not bed.is_occupied:
        flash('This bed is not occupied')
        return redirect(url_for('manage_beds'))
    
    bed.patient_id = None
    bed.is_occupied = False
    db.session.commit()
    
    flash(f'Bed {bed.bed_number} released successfully')
    return redirect(url_for('manage_beds'))

@app.route('/bed/delete/<int:bed_id>', methods=['POST'])
@login_required
def delete_bed(bed_id):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    
    bed = Bed.query.get_or_404(bed_id)
    
    if bed.is_occupied:
        flash('Cannot delete an occupied bed')
        return redirect(url_for('manage_beds'))
    
    db.session.delete(bed)
    db.session.commit()
    
    flash(f'Bed {bed.bed_number} deleted successfully')
    return redirect(url_for('manage_beds'))

@app.route('/doctor/update_patient/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def update_patient(patient_id):
    if current_user.role != 'doctor':
        flash('Only doctors can update patient information')
        return redirect(url_for('index'))
    
    patient = Patient.query.get_or_404(patient_id)
    
    # Check if the doctor is assigned to this patient
    if patient.doctor_id != current_user.id:
        flash('You can only update information for your assigned patients')
        return redirect(url_for('doctor_dashboard'))
    
    if request.method == 'POST':
        patient.diagnosis = request.form.get('diagnosis')
        # Update other fields as needed
        
        db.session.commit()
        flash('Patient information updated successfully')
        return redirect(url_for('patient_details', patient_id=patient.id))
    
    return render_template('doctor/update_patient.html', patient=patient)

@app.route('/prescribe/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def prescribe_medication(patient_id):
    if current_user.role != 'doctor':
        flash('Only doctors can prescribe medications')
        return redirect(url_for('index'))
    
    patient = Patient.query.get_or_404(patient_id)
    
    # Check if the doctor is assigned to this patient
    if patient.doctor_id != current_user.id:
        flash('You can only prescribe medications for your assigned patients')
        return redirect(url_for('doctor_dashboard'))
    
    if request.method == 'POST':
        medication_name = request.form.get('name')
        dosage = request.form.get('dosage')
        
        new_medication = Medication(
            name=medication_name,
            dosage=dosage,
            patient_id=patient.id
        )
        
        db.session.add(new_medication)
        db.session.commit()
        
        flash('Medication prescribed successfully')
        return redirect(url_for('patient_details', patient_id=patient.id))
    
    return render_template('doctor/prescribe.html', patient=patient)

@app.route('/pharmacy/dispense/<int:medication_id>', methods=['GET', 'POST'])
@login_required
def dispense_medication(medication_id):
    if current_user.role != 'pharmacy':
        return redirect(url_for('index'))
    
    medication = Medication.query.get_or_404(medication_id)
    
    if request.method == 'POST':
        medication.status = 'dispensed'
        medication.dispensed_date = datetime.datetime.now(datetime.timezone.utc)
        medication.dispensed_by = current_user.id
        
        db.session.commit()
        flash('Medication dispensed successfully')
        return redirect(url_for('pharmacy_dashboard'))
    
    return render_template('pharmacy/dispense.html', medication=medication)

@app.route('/pharmacy/medication/<int:medication_id>')
@login_required
def medication_details(medication_id):
    if current_user.role != 'pharmacy':
        return redirect(url_for('index'))
    
    medication = Medication.query.get_or_404(medication_id)
    return render_template('pharmacy/medication_details.html', medication=medication)

@app.route('/patient/<int:patient_id>/add_note', methods=['POST'])
@login_required
def add_medical_note(patient_id):
    if current_user.role != 'doctor':
        flash('Only doctors can add medical notes')
        return redirect(url_for('index'))
    
    patient = Patient.query.get_or_404(patient_id)
    
    # Check if the doctor is assigned to this patient
    if patient.doctor_id != current_user.id:
        flash('You can only add notes for your assigned patients')
        return redirect(url_for('doctor_dashboard'))
    
    content = request.form.get('medical_note')
    
    if content:
        new_note = MedicalNote(
            content=content,
            patient_id=patient_id,
            doctor_id=current_user.id
        )
        
        db.session.add(new_note)
        db.session.commit()
        
        flash('Medical note added successfully')
    
    return redirect(url_for('patient_details', patient_id=patient_id))

@app.route('/patient/<int:patient_id>/order_test', methods=['GET', 'POST'])
@login_required
def order_test(patient_id):
    if current_user.role != 'doctor':
        flash('Only doctors can order diagnostic tests')
        return redirect(url_for('index'))
    
    patient = Patient.query.get_or_404(patient_id)
    
    # Check if the doctor is assigned to this patient
    if patient.doctor_id != current_user.id:
        flash('You can only order tests for your assigned patients')
        return redirect(url_for('doctor_dashboard'))
    
    if request.method == 'POST':
        test_name = request.form.get('test_name')
        test_description = request.form.get('test_description')
        
        if test_name:
            new_test = DiagnosticTest(
                patient_id=patient_id,
                doctor_id=current_user.id,
                test_name=test_name,
                test_description=test_description,
                status='pending'
            )
            
            db.session.add(new_test)
            db.session.commit()
            
            flash('Diagnostic test ordered successfully')
            return redirect(url_for('patient_details', patient_id=patient_id))
    
    return render_template('doctor/order_test.html', patient=patient)

@app.route('/diagnostic/test/<int:test_id>/add_result', methods=['GET', 'POST'])
@login_required
def add_test_result(test_id):
    if current_user.role != 'diagnostic':
        return redirect(url_for('index'))
    
    test = DiagnosticTest.query.get_or_404(test_id)
    
    if test.status != 'pending':
        flash('This test already has results')
        return redirect(url_for('diagnostic_dashboard'))
    
    if request.method == 'POST':
        result = request.form.get('result')
        
        if result:
            test.result = result
            test.status = 'completed'
            test.result_date = datetime.datetime.now(datetime.timezone.utc)
            
            db.session.commit()
            
            flash('Test results added successfully')
            return redirect(url_for('diagnostic_dashboard'))
    
    return render_template('diagnostic/add_result.html', test=test)

@app.route('/diagnostic/test/<int:test_id>/view_result')
@login_required
def view_test_result(test_id):
    test = DiagnosticTest.query.get_or_404(test_id)
    
    if test.status != 'completed':
        flash('This test does not have results yet')
        return redirect(url_for('diagnostic_dashboard'))
    
    return render_template('diagnostic/view_result.html', test=test)

@app.route('/diagnostic/test/<int:test_id>/update_result', methods=['GET', 'POST'])
@login_required
def update_test_result(test_id):
    if current_user.role != 'diagnostic':
        flash('Only diagnostic staff can update test results')
        return redirect(url_for('index'))
    
    test = DiagnosticTest.query.get_or_404(test_id)
    
    if request.method == 'POST':
        result = request.form.get('result')
        
        if result:
            test.result = result
            test.status = 'completed'
            test.result_date = datetime.datetime.now(datetime.timezone.utc)
            
            db.session.commit()
            
            flash('Test results updated successfully')
            return redirect(url_for('diagnostic_dashboard'))
    
    return render_template('diagnostic/update_result.html', test=test)

