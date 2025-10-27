from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from .models import User, db
from .forms import LoginForm
import pickle, numpy as np, pandas as pd

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return redirect(url_for('main.login'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password')
    return render_template('login.html', form=form)

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

@main.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    if request.method == 'POST':
        # Collect input data from form
        input_data = [
            request.form['age'],
            request.form['gender'],
            request.form['smoking'],
            request.form['family_history'],
            request.form['allergies'],
            request.form['activity']
        ]
        
        # Load preprocessor and model
        preprocessor = pickle.load(open('model/preprocessor.pkl', 'rb'))
        model = pickle.load(open('model/asthma_model.pkl', 'rb'))

        # Preprocess and predict
        X = pd.DataFrame([input_data], columns=[
            'Age', 'Gender', 'Smoking', 'Family_History', 'Allergies', 'Activity'
        ])
        X_processed = preprocessor.transform(X)
        prediction = model.predict(X_processed)

        return render_template('predict.html', result=prediction[0])

    return render_template('predict.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))