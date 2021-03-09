from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm
app = Flask(__name__)

app.config['SECRET_KEY'] = '8642a640a492530125e4412552ee0db9'

posts = [
    {
        'author': 'Neil Choromokos',
        'title': 'First Blog Post',
        'content': 'first post content',
        'date': '11/12'
    },
    {
        'author': 'Jay Kashyap',
        'title': 'Second Blog Post',
        'content': 'poggers',
        'date': '11/12'
    }
]

@app.route('/')
def home():
    return render_template('homepage.html', posts=posts)

@app.route("/about")
def about():
    return render_template('aboutpage.html', title='About')

@app.route('/register', methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for { form.username.data }!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)

@app.route('/register')
def login():
    form = LoginForm()
    return render_template('login.html', title='Login', form=form)


if __name__ == '__main__':
    app.run(debug=True)