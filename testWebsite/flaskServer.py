from flask import Flask, render_template, url_for, flash, redirect

app = Flask(__name__)

app.config['SECRET_KEY'] = '8642a640a492530125e4412552ee0db9'


@app.route('/', methods=['GET','POST'])
def index():
    return render_template('index.html')

'''
@app.route("/about")
def about():
    return render_template('about.html', title='About', )

@app.route('/register', methods=['GET','POST'])
def register():
    return render_template('register.html', title='Register', )

@app.route('/login')
def login():
    return render_template('login.html', title='Login', )
'''

if __name__ == '__main__':
    app.run(debug=True)