from flask import Flask, render_template, redirect, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib

app = Flask(__name__)
app.secret_key = 'super_secret_hospital_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

ADMIN_EMAIL = "admin@hospital.com"
ADMIN_PASS = "nakul@123"


# --- MODELS ---
class Appointment(db.Model):
    p_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) 
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
    status = db.Column(db.String(50), default="Pending") 


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# --- GLOBAL DATASETS ---
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

DEPARTMENTS_DATASET = [
    {
        "name": "Cardiology",
        "icon": "fa-heartbeat",
        "desc": "Advanced heart care focusing on diagnostics, treatment, and structural surgeries for complex cardiovascular conditions."
    },
    {
        "name": "Neurology",
        "icon": "fa-brain",
        "desc": "Comprehensive treatment for disorders affecting the nervous system, brain, spinal cord, and neuro-muscular structures."
    },
    {
        "name": "Orthopedic",
        "icon": "fa-bone",
        "desc": "Expert bone and joint treatments covering spine care, athletic sports injuries, and advanced joint reconstruction."
    },
    {
        "name": "Pediatrics",
        "icon": "fa-baby",
        "desc": "Dedicated and compassionate medical care customized for infants, toddlers, adolescents, and growing children."
    },
    {
        "name": "General Medicine",
        "icon": "fa-stethoscope",
        "desc": "Comprehensive primary medical care, disease prevention, and expert management of chronic internal illnesses."
    },
    {
        "name": "Dermatology",
        "icon": "fa-allergies",
        "desc": "Specialized clinical diagnosis and therapy for skin, hair, and nail health, along with advanced allergy care."
    },
    {
        "name": "Oncology",
        "icon": "fa-ribbon",
        "desc": "State-of-the-art cancer treatment programs combining systemic chemotherapy, target therapy, and early screenings."
    },
    {
        "name": "Endocrinology",
        "icon": "fa-capsules",
        "desc": "Specialized management of complex hormonal balance disorders, diabetes, metabolism abnormalities, and thyroid care."
    },
    {
        "name": "Gastroenterology",
        "icon": "fa-bacteria",
        "desc": "Advanced diagnostics and therapies for all aspects of digestive track health, liver conditions, and stomach disorders."
    }
]


# --- ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered", "error")
            return "Email already registered"

        new_user = User(
            username=username,
            email=email,
            password=password
        )
        db.session.add(new_user)
        db.session.commit()

        sender_email = 'nakulhemant2211@gmail.com'
        sender_password = 'ndmaeravnthyiaqr'
        user_email = request.form['email']
        subject = "Hospital Updates"

        text = """
    Hello,

    Thank you signing up for our hospital website.
    We will send you updates about our hospital services.

    Stay healthy!
    Thank You!
    MEDHELP Hospital
    """
        message = f"Subject: {subject}\n\n{text}"

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, user_email, message)
            server.quit()
            print("Email sent successfully")
        except Exception as e:
            print("Signup Email Error:", e)

        return redirect('/login')

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if email == ADMIN_EMAIL and password == ADMIN_PASS:
            session.clear()
            session['admin'] = True
            session['user_email'] = ADMIN_EMAIL
            return redirect('/admin_dashboard')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session.clear()
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['admin'] = False
            return redirect('/')

        return "Invalid email or password"

    return render_template('login.html')


@app.route('/appointment', methods=['GET', 'POST'])
def appointment():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        new_appointment = Appointment(
            user_id=session['user_id'],
            name=request.form['patient_name'].title(),
            email=request.form['email'],
            phone_no=request.form['phone_no'],
            age=request.form['age'],
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

        sender_email = 'nakulhemant2211@gmail.com'
        sender_password = 'ndmaeravnthyiaqr'
        user_email = request.form['email']
        subject = "Hospital Updates"

        text = f"""
    Hello,

    Your appointment has been booked successfully, which is scheduled for {request.form['date']} at {request.form['time']}.
    We will send you updates about your appointment status.

    Stay healthy!
    Thank You!
    MEDHELP Hospital
    """
        message = f"Subject: {subject}\n\n{text}"

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, user_email, message)
            server.quit()
            print("Email sent successfully")
        except Exception as e:
            print("Email Booking Error:", e)

        flash("Appointment Booked Successfully!", "success")
        return redirect('/your_appointments')

    return render_template('appointment.html', doctors=DOCTORS_DATASET)


@app.route('/doctors')
def doctors():
    return render_template('doctors.html', doctors=DOCTORS_DATASET)


@app.route('/departments')
def departments():
    return render_template('departments.html', departments=DEPARTMENTS_DATASET)


@app.route('/your_appointments')
def your_appointments():
    if 'user_id' not in session:
        return redirect('/login')

    appointments = Appointment.query.filter_by(user_id=session['user_id']).all()
    return render_template('your_appointments.html', appointments=appointments)


@app.route('/update_status/<int:id>/<string:status>')
def update_status(id, status):
    if not session.get('admin'):
        return redirect('/')

    appt = Appointment.query.get(id)
    if not appt:
        return redirect('/admin_dashboard')

    if appt.status == status or appt.status != "Pending":
        return redirect('/admin_dashboard')

    appt.status = status
    db.session.commit()

    sender_email = 'nakulhemant2211@gmail.com'
    sender_password = 'ndmaeravnthyiaqr'
    user_email = appt.email

    if status == "Accept":
        subject = "Appointment Accepted"
        text = f"""
Hello {appt.name},

Your appointment has been ACCEPTED successfully.

Appointment Details:
Department: {appt.dept}
Doctor: {appt.doctor}
Date: {appt.date}
Time: {appt.time}

Please arrive 10 minutes before your appointment.

Thank you for choosing MEDHELP Hospital.
"""
    elif status == "Cancel":
        subject = "Appointment Cancelled"
        text = f"""
Hello {appt.name},

We are sorry to inform you that your appointment has been CANCELLED.

Appointment Details:
Department: {appt.dept}
Doctor: {appt.doctor}
Date: {appt.date}
Time: {appt.time}

Please book another appointment later.

Thank you,
MEDHELP Hospital
"""

    message = f"Subject: {subject}\n\n{text}"

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, user_email, message)
        server.quit()
        print("Email sent successfully")
        
        if status == "Accept":
            flash(f"Appointment for {appt.name} Accepted & Email Sent!", "success")
        else:
            flash(f"Appointment for {appt.name} Cancelled & Email Sent.", "error")

    except Exception as e:
        print("Email Error:", e)
        flash("Status updated, but notification email failed to send.", "error")

    return redirect('/admin_dashboard')


@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect('/')

    appointments = Appointment.query.all()
    return render_template('admin_dashboard.html', appointments=appointments)


@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect('/login')

    current_user = User.query.get(session['user_id'])
    if not current_user:
        session.clear()
        return redirect('/login')

    user_appointments = Appointment.query.filter_by(user_id=current_user.id).all()
    return render_template('profile.html', current_user=current_user, appointments=user_appointments)


@app.route('/email', methods=['POST'])
def email():
    sender_email = 'nakulhemant2211@gmail.com'
    sender_password = 'ndmaeravnthyiaqr'
    user_email = request.form['email']
    subject = "Hospital Updates"

    text = """
Hello,

Thank you for subscribing to our hospital website.
We will send you updates about our hospital services.

Stay healthy!
Thank You!
MEDHELP Hospital
"""
    message = f"Subject: {subject}\n\n{text}"

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, user_email, message)
        server.quit()
        print("Email sent successfully")
        flash("Thank you for subscribing to our Newsletter!", "success")
    except Exception as e:
        print("Subscription Email Error:", e)
        flash("Subscription failed. Please check your email connection.", "error")

    return redirect('/')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0',port=5000)