from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .forms import LoginForm, RegisterForm 
from .models import User, db
import pandas as pd
import joblib
# import pickle, numpy

file_path = "./model/asthma_severity_model.pkl"
main = Blueprint('main', __name__)
model = joblib.load(file_path)

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

# @main.route('/predict', methods=['GET', 'POST'])
# @login_required
# def predict():
#     if request.method == 'POST':
#         data = [float(x) for x in request.form.values()]
#         model = pickle.load(open('model/asthma_model.pkl', 'rb'))
#         preprocessor = pickle.load(open('model/preprocessor.pkl', 'rb'))
#         input_data = preprocessor.transform(np.array([data]))
#         prediction = model.predict(input_data)
#         return render_template('predict.html', result=prediction[0])
#     return render_template('predict.html')

# @main.route('/predict', methods=['GET', 'POST'])
# @login_required
# def predict():
#     if request.method == 'POST':
#         # Collect input data from form
#         input_data = [
#             request.form['age'],
#             request.form['gender'],
#             request.form['smoking'],
#             request.form['family_history'],
#             request.form['allergies'],
#             request.form['activity']
#         ]
        
#         # Load preprocessor and model
#         preprocessor = pickle.load(open('model/preprocessor.pkl', 'rb'))
#         model = pickle.load(open('model/asthma_model.pkl', 'rb'))

#         # Preprocess and predict
#         X = pd.DataFrame([input_data], columns=[
#             'Age', 'Gender', 'Smoking', 'Family_History', 'Allergies', 'Activity'
#         ])
#         X_processed = preprocessor.transform(X)
#         prediction = model.predict(X_processed)

#         return render_template('predict.html', result=prediction[0])

#     return render_template('predict.html')

@main.route("/predict", methods=["GET", "POST"])
def predict():
    if request.method == "POST":
        try:
            # Match the features used during training
            features = [
                "Tiredness", "Dry-Cough", "Difficulty-in-Breathing", "Sore-Throat",
                "None_Sympton", "Pains", "Nasal-Congestion", "Runny-Nose",
                "None_Experiencing", "Age_0-9", "Age_10-19", "Age_20-24",
                "Age_25-59", "Age_60+", "Gender_Female", "Gender_Male"
            ]

            # Gather user input
            user_input = {f: [int(request.form.get(f, 0))] for f in features}
            X_input = pd.DataFrame(user_input)

            # Predict severity
            prediction = model.predict(X_input)[0]
            proba = model.predict_proba(X_input).max() * 100

            result = f"Predicted Asthma Severity: {prediction} ({proba:.1f}% confidence)"
            flash(result, "success")

        except Exception as e:
            flash(f"Error: {e}", "danger")

    return render_template("predict.html")

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))