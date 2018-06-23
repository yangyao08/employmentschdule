from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, AddPersonForm, AddEngagementForm,RemovePersonForm, RemoveEngagementForm, SearchPersonnelForm, SearchEngagementForm, AssignEngagementForm
from app.models import User
import sqlite3
from flask_login import current_user, login_user, logout_user, login_required
from flask import render_template, flash, redirect, url_for, request, session
from werkzeug.urls import url_parse
from datetime import datetime
from functools import wraps

def requires_access_level(access_level):
  def decorator(f):
      @wraps(f)
      def decorated_function(*args, **kwargs):
          if not current_user.is_authenticated:
            flash("Please login to view the page!")
            return redirect(url_for('login'))
          user = User.query.filter_by(username=current_user.username).first()
          if user is None or not user.allowed(access_level):
            flash("You do not have access to that page. Sorry!")
            return redirect(url_for('index'))
          return f(*args, **kwargs)
      return decorated_function
  return decorator


@app.route('/')
@app.route('/index')
@login_required
def index():
  return render_template('index.html', title='Home')

@app.route('/login', methods=['GET', 'POST'])
def login():
  if current_user.is_authenticated:
    return redirect(url_for('index'))
  form = LoginForm()
  if form.validate_on_submit():
    user = User.query.filter_by(username=form.username.data).first()
    if user is None or not user.check_password(form.password.data):
      flash('Invalid username or password')
      return redirect(url_for('login'))
    login_user(user, remember=form.remember_me.data)
    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '': #prevent external site
      next_page = url_for('index')
    return redirect(next_page)
  return render_template('login.html', title='Query Database', form=form)

@app.route('/logout')
def logout():
  logout_user()
  return redirect(url_for('login')) #not index as currently that's where the data is shown

@app.route('/user/<username>')
@login_required
def user(username):
  user = User.query.filter_by(username=username).first_or_404()
  posts = [
      {'author': user, 'body': 'Test post #1'},
      {'author': user, 'body': 'Test post #2'}
  ]
  return render_template('user.html', user=user, posts=posts)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/register', methods=['GET', 'POST'])
def register():
  if current_user.is_authenticated:
      return redirect(url_for('index'))
  form = RegistrationForm()
  if form.validate_on_submit():
      user = User(username=form.username.data, email=form.email.data)
      user.set_password(form.password.data)
      db.session.add(user)
      db.session.commit()
      flash('Congratulations, you are now a registered user!')
      return redirect(url_for('login'))
  return render_template('register.html', title='Register', form=form)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
  form = EditProfileForm(current_user.username)
  if form.validate_on_submit():
      current_user.username = form.username.data
      db.session.commit()
      flash('Your changes have been saved.')
      return redirect(url_for('edit_profile'))
  elif request.method == 'GET':
      form.username.data = current_user.username
  return render_template('edit_profile.html', title='Edit Profile', form=form)

@app.route('/viewpersonnel')
def viewpersonnel():
 con = sqlite3.connect("testemployees.db")
 con.row_factory = sqlite3.Row

 cur = con.cursor()
 cur.execute("select * from Employees")

 rows = cur.fetchall();
 return render_template("view_personnel.html",rows = rows)

@app.route('/viewengagements')
def viewengagements():
 con = sqlite3.connect("testemployees.db")
 con.row_factory = sqlite3.Row

 cur = con.cursor()
 cur.execute("select * from Engagements")

 rows = cur.fetchall();
 return render_template("view_engagements.html",rows = rows)



@app.route('/searchpersonnel', methods=['GET', 'POST'])
def searchpersonnel():
  form = SearchPersonnelForm()
  if form.validate_on_submit():
    con = sqlite3.connect("testemployees.db")
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute("SELECT * FROM Employees WHERE `Name` = ?",(form.Personnel.data,))

    rows = cur.fetchall();


    return render_template("view_personnel.html",rows = rows)
  return render_template('searchpersonnel.html', title='Search for Personnel', form=form)

@app.route('/searchengagement', methods=['GET', 'POST'])
def searchengagement():
  form = SearchEngagementForm()
  if form.validate_on_submit():
    con = sqlite3.connect("testemployees.db")
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute("SELECT * FROM Engagements WHERE `Name` = ?",(form.Engagement.data,))

    rows = cur.fetchall();


    return render_template("view_engagements.html",rows = rows)
  return render_template('searchengagement.html', title='Search for Engagement', form=form)
 


@app.route('/addnewpersonnel', methods=['GET', 'POST'])
def addnewpersonnel():
  form = AddPersonForm()
  if form.validate_on_submit():
    Name = form.Name.data
    Position = form.Position.data
    #Tier = form.Tier.data
    Engagements = None
    Easy_Jobs = 0
    Medium_Jobs = 0
    Difficult_Jobs = 0


    con = sqlite3.connect("testemployees.db")
    cur = con.cursor()
    cur.execute(
      """INSERT INTO 
        `Employees` (
          `Name`, 
          `Position`, 
          `Tier` ,
          `Engagements` ,
          `Easy Jobs` ,
          `Medium Jobs` ,
          `Difficult Jobs`,
          `Employed` ) 
      VALUES (?,?,?,?,?,?,?,?)""", 
      (Name,Position,None,Engagements,Easy_Jobs,Medium_Jobs,Difficult_Jobs,1))
    con.commit()
    con.close()
    return render_template('addedpersonnel.html')
  return render_template('addnewpersonnel.html', form=form)


@app.route('/addnewengagement', methods=['GET', 'POST'])
def addnewengagement():
  form = AddEngagementForm()
  if form.validate_on_submit():
    Name = form.Name.data
    Job = form.Job.data
    Difficulty = form.Difficulty.data
    Expected_Hours = form.Expected_Hours.data
    Start_Date = form.Start_Date.data
    End_Date = form.End_Date.data
    Days_Given = form.Days_Given.data
    Req_person = form.Req_person.data
    Priority_Person = form.Priority_Person.data

    con = sqlite3.connect("testemployees.db")
    cur = con.cursor()
    cur.execute(
      """INSERT INTO 
        `Engagements` (
          `Name`, 
          `Job`, 
          `Difficulty` ,
          `Expected Hours` ,
          `Start Date` ,
          `End Date` ,
          `Days Given`,
          `Required Num of Person`,
          `Personnel Involved` ,
          `Priority Person`,
          `Completed`) 
      VALUES (?,?,?,?,?,?,?,?,?,?,?)""", 
      (Name,Job,Difficulty,Expected_Hours,Start_Date,End_Date,Days_Given,Req_person,0,Priority_Person,0))
    con.commit()
    con.close()
    return render_template('addedengagement.html')
  return render_template('addnewengagement.html', form=form)

@app.route('/deletepersonnel', methods=['GET', 'POST'])
def deletepersonnel():
  form = RemovePersonForm()
  if form.validate_on_submit():
    con = sqlite3.connect("testemployees.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute('DELETE FROM Employees where `Name`  = ?', (form.person.data,))
    con.commit()
    con.close()
    return render_template('deletedpers.html')
  return render_template('deletepersonnel.html',form=form)

@app.route('/deleteengagement', methods=['GET', 'POST'])
def deleteengagement():
  form = RemoveEngagementForm()
  if form.validate_on_submit():
    con = sqlite3.connect("testemployees.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute('DELETE FROM Engagements where `Name`  = ?', (form.engagement.data,))
    con.commit()
    con.close()
    return render_template('deletedeng.html')
  return render_template('deleteengagement.html',form=form)

@app.route('/assign_engagement', methods=['GET', 'POST'])
def assign_engagement():
  form = AssignEngagementForm()
  if form.validate_on_submit():
    con = sqlite3.connect("testemployees.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute('SELECT `Required Num of Person` FROM Engagements Where Name = ?', (form.Engagement.data,))
    #get required number of personnel
    req = cur.fetchone()[0]

    #loop while required number not 0



    #run assignment algorithm
    con.commit()
    con.close()
    return render_template('assigned.html')
  return render_template('assign.html',form=form)