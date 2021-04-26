from flask import Flask, render_template, url_for, flash, redirect, request

app = Flask(__name__)

app.config['SECRET_KEY'] = '8642a640a492530125e4412552ee0db9'


@app.route('/', methods=['GET','POST'])
def index():
    return render_template('index.html')



@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == "POST":
        user = request.form['first_name']
        return redirect(url_for('user', usr=user))
    else:
        return render_template('register.html')

@app.route('/<usr>')
def user(usr):
    return f'<h1>{usr}</h1>'

'''
@app.route('/login', methods=['GET','POST'])
def login():
    return render_template('login.html')'''




if __name__ == '__main__':
    app.run(debug=True)