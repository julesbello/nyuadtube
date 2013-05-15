from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid
from forms import LoginForm, UploadForm, ProfileForm
from models import User, ROLE_USER, ROLE_ADMIN, Video
import datetime


@app.route('/')
@app.route('/index')
@login_required
def index():
    user = g.user
    videos = Video.query.all()
    return render_template('index.html',
        title = 'Home',
        user = user,
        videos = videos)
        
 
@app.route('/login', methods = ['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for = ['nickname', 'email'])
    return render_template('login.html', 
        title = 'Sign In',
        form = form,
        providers = app.config['OPENID_PROVIDERS'])
        

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))
    
@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        redirect(url_for('login'))
    user = User.query.filter_by(email = resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        user = User(nickname = nickname, email = resp.email, role = ROLE_USER)
        db.session.add(user)
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember = remember_me)
    return redirect(request.args.get('next') or url_for('index'))
    
@app.before_request
def before_request():
    g.user = current_user
    if not g.user.is_anonymous() and not g.user.facebook and request.endpoint != 'profile':
    		return redirect(url_for('profile'))
    
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
    
@app.route('/upload', methods = ['GET', 'POST'])
def upload():
		user = g.user
		form = UploadForm()
		if form.validate_on_submit():
				video = Video(link = form.link.data, 
				comment = form.comment.data, 
				timestamp = datetime.datetime.utcnow(),
				author = user)
				db.session.add(video)
				db.session.commit()
				flash("Upload successful!")
				return redirect(url_for('index'))
		return render_template('upload.html',
		title = 'Upload',
		form = form,
		user = user)
		
@app.route('/profile', methods = ['GET', 'POST'])
def profile():
		form = ProfileForm()
		user = g.user	
		if form.validate_on_submit():
				user.facebook = form.facebook.data if len(form.facebook.data) > 2 else "null"
				user.nickname = form.username.data if len(form.username.data) > 2 else user.nickname
				db.session.commit()
				flash("Profile updated successfully.")
				return redirect(url_for('index'))
		return render_template('profile.html',
		title= 'Profile',
		form = form,
		user = user)



	
	
    