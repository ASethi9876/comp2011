from flask import render_template, flash, redirect, make_response, request
from flask_login import login_user, logout_user, login_required, current_user, LoginManager
from app import app, db, admin, bcrypt
from flask_admin.contrib.sqla import ModelView
from .models import User, Module, Enrolment, Message, Vote
from datetime import datetime
import json

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Module, db.session))
admin.add_view(ModelView(Enrolment, db.session))
admin.add_view(ModelView(Message, db.session))

login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(id):
    return User.query.filter_by(id = id).first()

@app.route('/', methods=['GET', 'POST'])
# Adapted from a tutorial found at: https://www.geeksforgeeks.org/password-hashing-with-bcrypt-in-flask/
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(id = email).first()
        if user:
            is_valid = bcrypt.check_password_hash(user.password, password) 

            if is_valid:
                login_user(user)
                return redirect('/home')

    return render_template('login.html', title="Login")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if (not email or not username or not password or not confirm_password):
            flash("Must fill all fields.")
            return render_template('register.html', title="New User")

        user = User.query.filter_by(id = email).first()
        if user:
            flash("Email address already used.")
            return render_template('register.html', title="New User")
        
        if password != confirm_password:
            flash("Passwords do not match.")
            return render_template('register.html', title="New User")
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8') 
        new_user = User(id=email, username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect('/home')

    return render_template('register.html', title="New User")

@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    module = "All"
    if request.method == 'POST':
        module = request.form.get('module')

    enrolment = Enrolment.query.filter_by(user_id = current_user.username).all()

    # Check if the user has enrolled onto any modules yet
    if enrolment:
        c_module_ids = e_module_ids = [e.module_id for e in enrolment if e.creator == True]
        e_module_ids = [e.module_id for e in enrolment if e.creator == False]
        created = Module.query.filter(Module.id.in_(c_module_ids)).all()
        enrolled = Module.query.filter(Module.id.in_(e_module_ids)).all()
        moduleCheck = True
    else:
        moduleCheck = False
        created = []
        enrolled = []
        
    if module == "All":
        messages = Message.query.order_by(Message.time.desc()).all()
    else:
        messages = Message.query.filter_by(module=module).order_by(Message.time).all()
    return render_template('home.html', title="Homepage", messages=messages, created=created, enrolled=enrolled, moduleCheck=moduleCheck, user=current_user.username)

@app.route('/new_message', methods=['GET', 'POST'])
@login_required
def new_message():
    modules = Module.query.all()
    return render_template('new_message.html', title="New Message", modules=modules)

@app.route('/send_message', methods=['GET', 'POST'])
def send_message():
    message_text = request.form.get('message_text')
    title = request.form.get('title')
    module = request.form.get('module')
    sender = current_user.username
    time = datetime.now()
    new_message = Message(message=message_text, title=title, module=module, sender=sender, time=time)
    db.session.add(new_message)
    db.session.commit()
    return redirect('/home')

@app.route('/delete_message', methods=['GET', 'POST'])
def delete_message():
    id = request.form.get('id')
    Message.query.filter_by(message_id = id).delete()
    db.session.commit()
    return redirect('/home')

@app.route('/module_list', methods=['GET', 'POST'])
@login_required
def module_list():
    # adapted from a response found at: https://stackoverflow.com/questions/62306873/flask-sqlalchemy-selecting-all-rows-with-ids-from-array
    enrolment = Enrolment.query.filter_by(user_id = current_user.username).all()
    c_module_ids = [e.module_id for e in enrolment if e.creator == True]
    e_module_ids = [e.module_id for e in enrolment if e.creator == False]
    m_module_ids = [e.module_id for e in enrolment]
    created = Module.query.filter(Module.id.in_(c_module_ids)).all()
    enrolled = Module.query.filter(Module.id.in_(e_module_ids)).all()
    modules = Module.query.filter(~Module.id.in_(m_module_ids)).all()
    return render_template('module_list.html', title="Module List", created=created, enrolled=enrolled, modules=modules)

@app.route('/create_module', methods=['GET', 'POST'])
@login_required
def create_module():
    if request.method == 'POST':
        module_code = request.form.get('module_code')
        title = request.form.get('title')
        description = request.form.get('description')
        new_module = Module(module_code=module_code, title=title, description=description, members=1)
        db.session.add(new_module)
        db.session.commit() # commit needed to get module_id

        new_enrolment = Enrolment(user_id=current_user.username, module_id=new_module.id, creator=True)
        db.session.add(new_enrolment)
        db.session.commit()
        return(redirect('/home'))

    return render_template('create_module.html', title="Create New Module")

@app.route('/delete_module', methods=['POST'])
def delete_module():
    url = request.referrer
    id = request.form.get('id')
    Module.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url)

@app.route('/join_module', methods=['POST'])
def join_module():
    id = request.form.get('id')
    new_enrolment = Enrolment(user_id=current_user.username, module_id=id, creator=False)
    db.session.add(new_enrolment)

    module = Module.query.filter_by(id=id).first()
    module.members += 1
    db.session.commit()
    return redirect('/module_list')

@app.route('/leave_module', methods=['POST'])
def leave_module():
    url = request.referrer
    id = request.form.get('id')
    Enrolment.query.filter_by(user_id=current_user.username, module_id=id).delete()

    module = Module.query.filter_by(id=id).first()
    module.members -= 1
    db.session.commit()
    return redirect(url)


@app.route('/vote', methods=['POST'])
def vote():
    data = json.loads(request.data)
    message_id = int(data.get('message_id'))
    vote_type = data.get('vote_type')
    message = Message.query.filter_by(message_id=message_id).first()
    voted = Vote.query.filter_by(user_id=current_user.username, message_id=message_id).first()
    
    if (voted):
        # Will convert a previously upvoted message to a downvoted one and vice versa
        if vote_type == 'up' and voted.vote_type == 'up':
            message.upvotes -= 1
            db.session.delete(voted)

        elif vote_type == 'down' and voted.vote_type == 'down':
            message.downvotes -= 1
            db.session.delete(voted)

    else:
        if vote_type == 'up':
            message.upvotes += 1
        elif vote_type == 'down':
            message.downvotes += 1

        vote = Vote(user_id=current_user.username, message_id=message_id, vote_type=vote_type)
        db.session.add(vote)

    db.session.commit()
    
    return json.dumps({'status':'OK','upvotes': message.upvotes, 'downvotes': message.downvotes})

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    flash("Successfully logged out.")
    return redirect('/')

