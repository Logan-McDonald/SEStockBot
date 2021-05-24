from flask import Flask, render_template, url_for, flash, redirect, request

app = Flask(__name__)

app.config['SECRET_KEY'] = '8642a640a492530125e4412552ee0db9'


@app.route('/', methods=['GET','POST'])
def index():
    return render_template('index.html')



@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == "POST":
        fname = request.form['first_name']
        lname = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        password1 = request.form['password_repeat']

        if len(fname) < 1:
            flash('Enter valid First Name', category='error')
            return redirect(url_for('register'))
        elif len(lname) < 1:
            flash('Enter valid Last Name', category='error')
            return redirect(url_for('register'))
        elif len(email) < 1:
            flash('Enter valid email', category='error')
            return redirect(url_for('register'))
        elif len(password) < 8:
            flash('Password must be 8 characters', category='error')
            return redirect(url_for('register'))
        elif password != password1:
            flash('Passwords do not match', category='error')
            return redirect(url_for('register'))
        else:
            flash('Account Created',category='success')
            return redirect(url_for('landing', usr=fname))
    else:
        return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    return render_template('login.html')

@app.route('/landing')
def landing(usr):
    return f'<h1> hello , {usr}</h1>'


if __name__ == '__main__':
    app.run(debug=True)