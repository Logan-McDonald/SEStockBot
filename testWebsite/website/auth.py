from flask.globals import session
from website.models import User
from flask import Blueprint, render_template, url_for, flash, redirect, request
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':

        #pulls data from post request
        fname = request.form.get('first_name')
        lname = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        password1 = request.form.get('password_repeat')

        #authenticates account
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Account with Email already Exists', category='error')
        elif len(fname) < 1:
            flash('Enter valid First Name', category='error')   
        elif len(lname) < 1:
            flash('Enter valid Last Name', category='error')
        elif len(email) < 1:
            flash('Enter valid email', category='error')
        elif len(password) < 8:
            flash('Password must be 8 characters', category='error')
        elif password != password1:
            flash('Passwords do not match', category='error')
       
        else:
            
            new_user = User(email=email, first_name=fname, password=generate_password_hash(password, method='sha256'))
            db.session.add(new_user)
            db.session.commit()

            login_user(new_user, remember=True)
            flash('Account Created',category='success')


            return redirect(url_for('pages.homepage'))
    return render_template('register.html', title='register', user=current_user)


@auth.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Successfully Logged in', category='success')
                login_user(user, remember=True)
                return redirect(url_for('pages.homepage'))
            else:
                flash('Incorrect Password', category='error')
        else:
            flash('Email does not exist', category='error')
            
    return render_template('login.html', title='Login', user=current_user)



@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))