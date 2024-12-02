from flask import render_template, flash, redirect, make_response, request
from flask_login import login_user, logout_user, login_required, current_user, LoginManager
from app import app, db, admin, bcrypt
from flask_admin.contrib.sqla import ModelView
from .models import User, Module, Enrolment, Message, Vote
from datetime import datetime
import json
import logging

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Module, db.session))
admin.add_view(ModelView(Enrolment, db.session))
admin.add_view(ModelView(Message, db.session))
admin.add_view(ModelView(Vote, db.session))

# necessary for flask login
login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(id):
    return User.query.filter_by(id = id).first()

# prompt user to login at start
@app.route('/', methods=['GET', 'POST'])
def login():
    app.logger.info('login request')
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(id = email).first()
        if user:
            # adapted from a tutorial found at: https://www.geeksforgeeks.org/password-hashing-with-bcrypt-in-flask/
            is_valid = bcrypt.check_password_hash(user.password, password) 

            if is_valid:
                login_user(user)
                app.logger.info('successful login')
                return redirect('/home')
            
            else:
                app.logger.info('incorrect password')
        
        else:
            app.logger.info('incorrect username')

    return render_template('login.html', title="Login")

# new account creation
@app.route('/register', methods=['GET', 'POST'])
def register():
    app.logger.info('/register request')
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        user = User.query.filter_by(id=email).first()
        if user:
            flash("Email address already used.")
            return redirect('/register')
        
        if username: 
            user = User.query.filter_by(username=username).first()
            if user:
                app.logger.info('invalid username')
                flash("Username already used.")
                return redirect('/register')
            
            # prevents overhang when displaying username
            if len(username) > 50:
                app.logger.info('invalid username')
                flash("Username cannot exceed 50 characters.")
                return redirect('/register')
    
        if password:
            if password != confirm_password:
                app.logger.info('invalid password')
                flash("Passwords do not match.")
                return redirect('/register')
        
            if len(password) < 8 or len(password) > 100:
                app.logger.info('invalid password')
                flash("Password must be at between 8 and 100 characters.")
                return redirect('/register')
        
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8') 
            new_user = User(id=email, username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            app.logger.info('account successfully created')
            return redirect('/home')

    return render_template('register.html', title="New User")

# homepage
@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    app.logger.info('/home request')
    module = "All"
    if request.method == 'POST':
        module = request.form.get('module')

    enrolment = Enrolment.query.filter_by(user_id = current_user.username).all()

    # check if the user has enrolled onto any modules yet
    if enrolment:
        # display owned modules and enrolled modules seperately
        c_module_ids = [e.id for e in enrolment if e.creator == True]
        e_module_ids = [e.id for e in enrolment if e.creator == False]
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

# page to write new message
@app.route('/new_message', methods=['GET', 'POST'])
@login_required
def new_message():
    app.logger.info('/new_message request')
    modules = Module.query.all()
    return render_template('new_message.html', title="New Message", modules=modules)

# send written message
@app.route('/send_message', methods=['GET', 'POST'])
@login_required
def send_message():
    app.logger.info('/send_message request')
    message_text = request.form.get('message_text')
    title = request.form.get('title')
    module = request.form.get('module')

    if message_text:
        if len(message_text) > 5000:
            app.logger.info('invalid message')
            flash("Message cannot exceed 5000 characters.")
            return redirect('/send_message')
        
    if title:
        if len(title) > 50:
            app.logger.info('invalid message title')
            flash("Title cannot exceed 50 characters.")
            return redirect('/send_message')

    sender = current_user.username
    time = datetime.now()
    new_message = Message(message=message_text, title=title, sender=sender, module=module, time=time)
    db.session.add(new_message)
    db.session.commit()
    app.logger.info('message successfully sent')
    return redirect('/home')

# delete messages from homepage
@app.route('/delete_message', methods=['GET', 'POST'])
def delete_message():
    app.logger.info('/delete_message request')
    id = request.form.get('id')
    Message.query.filter_by(id=id).delete()
    db.session.commit()
    app.logger.info('message deleted')
    return redirect('/home')

@app.route('/module_list', methods=['GET', 'POST'])
@login_required
def module_list():
    app.logger.info('/module_message request')

    # adapted from a response found at: https://stackoverflow.com/questions/62306873/flask-sqlalchemy-selecting-all-rows-with-ids-from-array
    enrolment = Enrolment.query.filter_by(user_id = current_user.username).all()
    c_module_ids = [e.id for e in enrolment if e.creator == True]
    e_module_ids = [e.id for e in enrolment if e.creator == False]
    m_module_ids = [e.id for e in enrolment]
    created = Module.query.filter(Module.id.in_(c_module_ids)).all()
    enrolled = Module.query.filter(Module.id.in_(e_module_ids)).all()
    modules = Module.query.filter(~Module.id.in_(m_module_ids)).all()
    return render_template('module_list.html', title="Module List", created=created, enrolled=enrolled, modules=modules)

@app.route('/create_module', methods=['GET', 'POST'])
@login_required
def create_module():
    app.logger.info('/create_module request')
    if request.method == 'POST':
        module_code = request.form.get('module_code')
        title = request.form.get('title')
        description = request.form.get('description')
        course = request.form.get('course')

        if module_code:
            if len(module_code) > 50:
                app.logger.info('invalid module code')
                flash("Module code cannot exceed 50 characters.")
                return redirect('/create_module')
        
        if title:
            if len(title) > 50:
                app.logger.info('invalid title')
                flash("Title cannot exceed 50 characters.")
                return redirect('/create_module')
        
        if course:
            if len(course) > 50:
                app.logger.info('invalid course')
                flash("Course cannot exceed 50 characters")
                return redirect('/create_module')

        new_module = Module(module_code=module_code, title=title, course=course, description=description, members=1)
        db.session.add(new_module)
        db.session.commit() # commit needed to get module_id

        new_enrolment = Enrolment(user_id=current_user.username, module_id=new_module.id, creator=True)
        db.session.add(new_enrolment)
        db.session.commit()
        app.logger.info('module successfully created')
        return(redirect('/home'))

    return render_template('create_module.html', title="Create New Module")

# delete a previously created module
@app.route('/delete_module', methods=['POST'])
def delete_module():
    app.logger.info('/delete_module request')
    url = request.referrer
    id = request.form.get('id')
    Module.query.filter_by(id=id).delete()
    db.session.commit()
    app.logger.info('module deleted')
    return redirect(url)

@app.route('/join_module', methods=['POST'])
def join_module():
    app.logger.info('/join_module request')
    id = request.form.get('id')
    new_enrolment = Enrolment(user_id=current_user.username, module_id=id, creator=False)
    db.session.add(new_enrolment)

    module = Module.query.filter_by(id=id).first()
    module.members += 1
    db.session.commit()
    app.logger.info('module joined')
    return redirect('/module_list')

@app.route('/leave_module', methods=['POST'])
def leave_module():
    app.logger.info('/leave_module request')
    url = request.referrer
    id = request.form.get('id')
    Enrolment.query.filter_by(user_id=current_user.username, module_id=id).delete()

    module = Module.query.filter_by(id=id).first()
    module.members -= 1
    db.session.commit()
    app.logger.info('module left')
    return redirect(url)

# links to ajax functionality for voting
@app.route('/vote', methods=['POST'])
def vote():
    app.logger.info('/vote request')
    data = json.loads(request.data)
    message_id = int(data.get('message_id'))
    vote_type = data.get('vote_type')
    message = Message.query.filter_by(id=message_id).first()
    voted = Vote.query.filter_by(user_id=current_user.username, message_id=message_id).first()
    
    # Remove a vote if it already exists, and do nothing if opposite button pressed
    if (voted):
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
    app.logger.info('vote submitted')
    return json.dumps({'status':'OK','upvotes': message.upvotes, 'downvotes': message.downvotes})

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    app.logger.info('/logout request')
    logout_user()
    app.logger.info('user logged out')
    flash("Successfully logged out.")
    return redirect('/')

