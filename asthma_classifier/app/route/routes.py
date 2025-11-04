from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ..forms import LoginForm, RegisterForm, EditProfileForm
from ..models import User, Prediction, db
import pandas as pd
import joblib
import json
# import pickle, numpy

main = Blueprint('main', __name__)
# Load model when the app starts
MODEL_PATH = "./model/asthma_model.pkl"

model = joblib.load(MODEL_PATH)

# model_info = joblib.load("MODEL_PATH")

# model = model_info["model"]
# model_accuracy_score = model_info.get("accuracy", None)

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

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == "admin":
        total_users = User.query.count()
        total_predictions = Prediction.query.count()
        model_accuracy = 49  # or load from model metrics
        # model_accuracy = model_accuracy_score
        return render_template(
            "dashboard.html",
            total_users=total_users,
            total_predictions=total_predictions,
            model_accuracy=model_accuracy
        )
    else:
        user_predictions = Prediction.query.filter_by(user_id=current_user.id).count()
        last_prediction = Prediction.query.filter_by(user_id=current_user.id).order_by(Prediction.timestamp.desc()).first()
        return render_template(
            "dashboard.html",
            user_predictions=user_predictions,
            last_prediction=last_prediction
        )
    
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

    return render_template('users/register.html', form=form)

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

            # Saving a prediction
            new_pred = Prediction(
                input_data=json.dumps(form_data),
                result=prediction,
                user_id=current_user.id
            )
            db.session.add(new_pred)
            db.session.commit()


        except Exception as e:
            flash(f"Error making prediction: {str(e)}", "danger")

    return render_template('predictions/predict.html', prediction=prediction)

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('users/profile.html')

@main.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        #current_user.email = form.email.data
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        #form.email.data = current_user.email
    return render_template('users/edit_profile.html', form=form)