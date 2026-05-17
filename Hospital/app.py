from flask import Flask, render_template, redirect, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'super_secret_hospital_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Prevent browser cache issues
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


db = SQLAlchemy(app)

# =========================
# ADMIN LOGIN DETAILS
# =========================
ADMIN_EMAIL = "admin@hospital.com"
ADMIN_PASS = "nakul@123"


# =========================
# MODELS
# =========================
class Appointment(db.Model):
    p_id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    phone_no = db.Column(db.String(150), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    dept = db.Column(db.String(150), nullable=False)
    doctor = db.Column(db.String(150), nullable=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    message = db.Column(db.Text, nullable=True)

    # Pending / Accepted / Cancelled
    status = db.Column(db.String(50), default="Pending")


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(250), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# =========================
# DOCTORS DATA
# =========================
DOCTORS_DATASET = [
    {"name": "Dr. Aarav Sharma", "spec": "Cardiology", "exp": "14 Years", "img": "fa-heartbeat"},
    {"name": "Dr. Ananya Iyer", "spec": "Cardiology", "exp": "11 Years", "img": "fa-heartbeat"},
    {"name": "Dr. Vikram Malhotra", "spec": "Cardiology", "exp": "16 Years", "img": "fa-heartbeat"},
    {"name": "Dr. Diya Deshmukh", "spec": "Cardiology", "exp": "9 Years", "img": "fa-heartbeat"},
    {"name": "Dr. Rohan Varma", "spec": "Cardiology", "exp": "12 Years", "img": "fa-heartbeat"},

    {"name": "Dr. Kabir Kapoor", "spec": "Neurology", "exp": "15 Years", "img": "fa-brain"},
    {"name": "Dr. Meera Nair", "spec": "Neurology", "exp": "10 Years", "img": "fa-brain"},
    {"name": "Dr. Arjun Banerjee", "spec": "Neurology", "exp": "18 Years", "img": "fa-brain"},
    {"name": "Dr. Sneha Reddy", "spec": "Neurology", "exp": "8 Years", "img": "fa-brain"},
    {"name": "Dr. Aditya Joshi", "spec": "Neurology", "exp": "13 Years", "img": "fa-brain"},

    {"name": "Dr. Ishaan Mehta", "spec": "Orthopedic", "exp": "17 Years", "img": "fa-bone"},
    {"name": "Dr. Pooja Singhal", "spec": "Orthopedic", "exp": "12 Years", "img": "fa-bone"},
    {"name": "Dr. Alok Mishra", "spec": "Orthopedic", "exp": "20 Years", "img": "fa-bone"},
    {"name": "Dr. Riya Chawla", "spec": "Orthopedic", "exp": "7 Years", "img": "fa-bone"},
    {"name": "Dr. Devendra Rao", "spec": "Orthopedic", "exp": "14 Years", "img": "fa-bone"},

    {"name": "Dr. Siddharth Gill", "spec": "Pediatrics", "exp": "11 Years", "img": "fa-baby"},
    {"name": "Dr. Tanvi Patel", "spec": "Pediatrics", "exp": "9 Years", "img": "fa-baby"},
    {"name": "Dr. Rajesh Gupta", "spec": "Pediatrics", "exp": "19 Years", "img": "fa-baby"},
    {"name": "Dr. Kavita Rao", "spec": "Pediatrics", "exp": "13 Years", "img": "fa-baby"},
    {"name": "Dr. Sanjay Dutt", "spec": "Pediatrics", "exp": "15 Years", "img": "fa-baby"},

    {"name": "Dr. Amit Saxena", "spec": "General Medicine", "exp": "22 Years", "img": "fa-stethoscope"},
    {"name": "Dr. Neha Verma", "spec": "Dermatology", "exp": "8 Years", "img": "fa-allergies"},
    {"name": "Dr. Suresh Prabhu", "spec": "Oncology", "exp": "21 Years", "img": "fa-ribbon"},
    {"name": "Dr. Kiran Mazumdar", "spec": "Endocrinology", "exp": "16 Years", "img": "fa-capsules"},
    {"name": "Dr. Vivek Oberoi", "spec": "Gastroenterology", "exp": "14 Years", "img": "fa-bacteria"}
]


# =========================
# ROUTES
# =========================
@app.route('/')
def index():
    return render_template('index.html')


# =========================
# SIGNUP
# =========================
@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'POST':

        username = request.form['username'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']

        # Prevent admin email registration
        if email == ADMIN_EMAIL:
            flash('This email is reserved for admin.', 'error')
            return redirect('/signup')

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash('Email already registered.', 'error')
            return redirect('/signup')

        hashed_password = generate_password_hash(password)

        new_user = User(
            username=username,
            email=email,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Signup successful. Please login.', 'success')
        return redirect('/login')

    return render_template('signup.html')


# =========================
# LOGIN
# =========================
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email'].strip().lower()
        password = request.form['password']

        # ADMIN LOGIN
        if email == ADMIN_EMAIL:

            if password == ADMIN_PASS:
                session.clear()
                session['admin'] = True
                session['user_email'] = ADMIN_EMAIL

                flash('Admin Login Successful!', 'success')
                return redirect('/admin_dashboard')

            else:
                flash('Invalid admin password.', 'error')
                return redirect('/login')

        # NORMAL USER LOGIN
        user = User.query.filter_by(email=email).first()

        if not user:
            flash('User not found.', 'error')
            return redirect('/login')

        if not check_password_hash(user.password, password):
            flash('Incorrect password.', 'error')
            return redirect('/login')

        session.clear()
        session['user_id'] = user.id
        session['user_email'] = user.email
        session['admin'] = False

        flash('Login Successful!', 'success')
        return redirect('/')

    return render_template('login.html')


# =========================
# APPOINTMENT
# =========================
@app.route('/appointment', methods=['GET', 'POST'])
def appointment():

    if 'user_id' not in session:
        flash('Please login first.', 'error')
        return redirect('/login')

    if request.method == 'POST':

        try:
            new_appointment = Appointment(
                user_id=session['user_id'],
                name=request.form['patient_name'].title(),
                email=request.form['email'].strip().lower(),
                phone_no=request.form['phone_no'],
                age=int(request.form['age']),
                gender=request.form['gender'],
                dept=request.form['department'],
                doctor=request.form['doctor'],
                date=datetime.strptime(request.form['date'], "%Y-%m-%d").date(),
                time=datetime.strptime(request.form['time'], "%H:%M").time(),
                message=request.form['message'],
                status="Pending"
            )

            db.session.add(new_appointment)
            db.session.commit()

            flash('Appointment booked successfully!', 'success')
            return redirect('/your_appointments')

        except Exception as e:
            print("Appointment Error:", e)
            flash('Something went wrong while booking appointment.', 'error')
            return redirect('/appointment')

    return render_template('appointment.html', doctors=DOCTORS_DATASET)


# =========================
# DOCTORS PAGE
# =========================
@app.route('/doctors')
def doctors():
    return render_template('doctors.html', doctors=DOCTORS_DATASET)


# =========================
# USER APPOINTMENTS
# =========================
@app.route('/your_appointments')
def your_appointments():

    if 'user_id' not in session:
        return redirect('/login')

    appointments = Appointment.query.filter_by(
        user_id=session['user_id']
    ).order_by(Appointment.date.desc()).all()

    return render_template(
        'your_appointments.html',
        appointments=appointments
    )


# =========================
# ADMIN STATUS UPDATE
# =========================
@app.route('/update_status/<int:id>/<string:status>')
def update_status(id, status):

    if not session.get('admin'):
        flash('Access Denied!', 'error')
        return redirect('/')

    appt = Appointment.query.get_or_404(id)

    # Prevent multiple clicks issue
    if appt.status != "Pending":
        flash('Appointment already updated.', 'error')
        return redirect('/admin_dashboard')

    # Only valid statuses
    if status not in ['Accept', 'Cancel']:
        flash('Invalid status.', 'error')
        return redirect('/admin_dashboard')

    appt.status = status
    db.session.commit()

    if status == 'Accept':
        flash(
            f'Appointment for {appt.name} accepted successfully.',
            'success'
        )
    else:
        flash(
            f'Appointment for {appt.name} cancelled successfully.',
            'error'
        )

    return redirect('/admin_dashboard')


# =========================
# ADMIN DASHBOARD
# =========================
@app.route('/admin_dashboard')
def admin_dashboard():

    if not session.get('admin'):
        flash('Access Denied!', 'error')
        return redirect('/')

    appointments = Appointment.query.order_by(
        Appointment.date.desc()
    ).all()

    return render_template(
        'admin_dashboard.html',
        appointments=appointments
    )


# =========================
# PROFILE
# =========================
@app.route('/profile')
def profile():

    if 'user_id' not in session:
        return redirect('/login')

    current_user = User.query.get(session['user_id'])

    if not current_user:
        session.clear()
        return redirect('/login')

    user_appointments = Appointment.query.filter_by(
        user_id=current_user.id
    ).all()

    return render_template(
        'profile.html',
        current_user=current_user,
        appointments=user_appointments
    )


# =========================
# NEWSLETTER EMAIL
# =========================
@app.route('/email', methods=['POST'])
def email():
    # Email functionality removed for Render compatibility
    flash('Thank you for subscribing!', 'success')
    return redirect('/')


# =========================
# LOGOUT
# =========================
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect('/')


# =========================
# OTHER PAGES
# =========================
@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/departments')
def departments():
    return render_template('departments.html')


# =========================
# MAIN
# =========================
if __name__ == '__main__':

    with app.app_context():
        db.create_all()

    app.run(host='0.0.0.0', port=5000)