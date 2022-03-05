import os
import datetime

from flask import Flask, render_template, redirect
from flask_login import LoginManager, login_required, logout_user

from data import db_session

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
print(f' * SECRET_KEY: {os.environ.get("SECRET_KEY")}')
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/')
def main_page():
    return render_template('main_page.html', title='order anywhere')


if __name__ == '__main__':
    db_session.global_init("db/data.db")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
