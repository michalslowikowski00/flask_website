
from flask import Flask
from flask_mail import Mail
from flask_mail import Message
from flask_sqlalchemy import SQLAlchemy
from flask import request, redirect, url_for, render_template
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required

app = Flask(__name__)

# mail config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'michal.slowikowski.mailer@gmail.com'
app.config['MAIL_PASSWORD'] = 'Zuzia007?!'

mail = Mail(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://Michal@localhost/flask_tut'
app.config['SECRET_KEY'] = 'super-secret'
app.config['SECURITY_REGISTERABLE'] = True
app.secret_key = 'development key'
app.debug = True
db = SQLAlchemy(app)


# Define models
roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


# index
@app.route('/')
def index():
    return render_template('index.html')


# profile
@app.route('/profile/<email>')
@login_required
def profile(email):
    user = User.query.filter_by(email=email).first()
    return render_template('profile.html', user=user)


# mail configuration
@app.route('/send_message', methods=['POST'])
def send_message():
    sender_name = request.form['name']
    sender_email = request.form['email']
    sender_message = request.form['message']

    subject_of_email = "New message from your site."

    text = "Message from %s %s: %s" % (sender_name, sender_email, sender_message)

    msg = Message(body=text,
                  subject=subject_of_email,
                  sender=sender_email,
                  recipients=['minusjeden@gmail.com'])

    mail.send(msg)
    return render_template('index.html')


@app.route('/post_user', methods=['POST'])
def post_user():
    user = User(request.form['username'], request.form['email'])
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run()
