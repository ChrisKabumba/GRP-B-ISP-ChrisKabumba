from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .forms import LoginForm, RegisterForm 
from .models import User, PatientRecord, db
import pandas as pd
import joblib
# import pickle, numpy

main = Blueprint('main', __name__)
# Load model when the app starts
MODEL_PATH = "./model/asthma_model.pkl"

model = joblib.load(MODEL_PATH)

@main.route('/')
def home():
    return redirect(url_for('main.login'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password')
    return render_template('login.html', form=form)

# --- Registration Page ---
@main.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    # Only admins can register new users
    if current_user.role != 'admin':
        flash('Access denied: Only administrators can register new users.', 'danger')
        return redirect(url_for('main.dashboard'))

    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Username already exists. Choose another.', 'warning')
            return redirect(url_for('main.register'))

        hashed_password = generate_password_hash(form.password.data)
        new_user = User(
            username=form.username.data, 
            password=hashed_password, 
            role=form.role.data
        )

        db.session.add(new_user)
        db.session.commit()
        flash(f"User '{form.username.data}' registered successfully as {form.role.data}!", 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('register.html', form=form)

@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)


@main.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    prediction = None

    if request.method == 'POST':
        try:
            # Collect form input values
            form_data = {
                'Tiredness': int(request.form.get('Tiredness')),
                'Dry-Cough': int(request.form.get('Dry-Cough')),
                'Difficulty-in-Breathing': int(request.form.get('Difficulty-in-Breathing')),
                'Sore-Throat': int(request.form.get('Sore-Throat')),
                'None_Sympton': int(request.form.get('None_Symptom')), # In the model, None_Symptom is None_Sympton
                'Pains': int(request.form.get('Pains')),
                'Nasal-Congestion': int(request.form.get('Nasal-Congestion')),
                'Runny-Nose': int(request.form.get('Runny-Nose')),
                'None_Experiencing': int(request.form.get('None_Experiencing')),
                'Age': request.form.get('Age'),
                'Gender': request.form.get('Gender')
            }

            # Convert to DataFrame
            input_df = pd.DataFrame([form_data])

            # Predict severity
            prediction = model.predict(input_df)[0]

        except Exception as e:
            flash(f"Error making prediction: {str(e)}", "danger")

    return render_template('predict.html', prediction=prediction)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/add_record', methods=['GET', 'POST'])
@login_required
def add_record():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        symptoms = request.form['symptoms']
        severity = request.form['severity']

        record = PatientRecord(
            name=name, age=age, gender=gender,
            symptoms=symptoms, severity=severity
        )
        db.session.add(record)
        db.session.commit()
        flash('Record added successfully!', 'success')
        return redirect(url_for('main.records'))

    return render_template('add_record.html')

@main.route('/records')
@login_required
def records():
    records = PatientRecord.query.all()
    return render_template('records.html', records=records)

@main.route('/update_record/<int:id>', methods=['GET', 'POST'])
@login_required
def update_record(id):
    record = PatientRecord.query.get_or_404(id)
    if request.method == 'POST':
        record.name = request.form['name']
        record.age = request.form['age']
        record.gender = request.form['gender']
        record.symptoms = request.form['symptoms']
        record.severity = request.form['severity']
        db.session.commit()
        flash('Record updated successfully!', 'info')
        return redirect(url_for('main.records'))
    return render_template('update_record.html', record=record)

@main.route('/delete_record/<int:id>')
@login_required
def delete_record(id):
    record = PatientRecord.query.get_or_404(id)
    db.session.delete(record)
    db.session.commit()
    flash('Record deleted successfully!', 'danger')
    return redirect(url_for('main.records'))