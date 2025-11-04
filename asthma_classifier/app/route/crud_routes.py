from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, User, Prediction

crud_bp = Blueprint('crud', __name__)

# ---------- USERS ----------

@crud_bp.route('/users')
@login_required
def list_users():
    if current_user.role != 'admin':
        flash("Access denied.")
        return redirect(url_for('main.dashboard'))
    users = User.query.all()
    return render_template('users/list.html', users=users)

@crud_bp.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if current_user.role != 'admin' and current_user.id != user.id:
        flash("Access denied.")
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        db.session.commit()
        flash('User updated successfully.')
        return redirect(url_for('crud.list_users'))
    return render_template('users/edit.html', user=user)

@crud_bp.route('/user/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if current_user.role != 'admin' and current_user.id != user.id:
        flash("Access denied.")
        return redirect(url_for('main.dashboard'))
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully.')
    return redirect(url_for('crud.list_users'))

# ---------- PREDICTIONS ----------

@crud_bp.route('/predictions')
@login_required
def list_predictions():
    if current_user.role == 'admin':
        predictions = Prediction.query.all()
    else:
        predictions = Prediction.query.filter_by(user_id=current_user.id).all()
    return render_template('predictions/list.html', predictions=predictions)

@crud_bp.route('/prediction/<int:prediction_id>/delete', methods=['POST'])
@login_required
def delete_prediction(prediction_id):
    prediction = Prediction.query.get_or_404(prediction_id)
    if current_user.role != 'admin' and current_user.id != prediction.user_id:
        flash("Access denied.")
        return redirect(url_for('crud.list_predictions'))
    db.session.delete(prediction)
    db.session.commit()
    flash('Prediction deleted.')
    return redirect(url_for('crud.list_predictions'))

@crud_bp.route('/prediction/<int:prediction_id>')
@login_required
def view_prediction(prediction_id):
    prediction = Prediction.query.get_or_404(prediction_id)
    if current_user.role != 'admin' and current_user.id != prediction.user_id:
        flash("Access denied.")
        return redirect(url_for('crud.list_predictions'))
    return render_template('predictions/view.html', prediction=prediction)