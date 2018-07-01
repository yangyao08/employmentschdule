from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, AddPersonForm, AddEngagementForm,RemovePersonForm, RemoveEngagementForm, SearchPersonnelForm, SearchEngagementForm, AssignEngagementForm, ExtendEngagementForm,PulloutPersonnelForm
from app.models import User
import sqlite3
from flask_login import current_user, login_user, logout_user, login_required
from flask import render_template, flash, redirect, url_for, request, session
from werkzeug.urls import url_parse
from datetime import datetime
from functools import wraps
from sqlalchemy import create_engine
from sqlalchemy import Column, Table, Integer, String, Float, DateTime, ForeignKey, Date
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
import random
Base = declarative_base()



#################################################################################################################
#################################################################################################################

############
# BACKEND  #
############

connection = Table('connect',Base.metadata,\
                   Column('person_id', Integer, ForeignKey('people.id')),\
                   Column('engage_id', Integer, ForeignKey('jobs.id')))

class Personnel(Base):
    __tablename__ = 'people'
    
    id = Column(Integer,primary_key = True)
    name = Column(String(50),unique = True)
    position = Column(String(50))
    engagements = relationship('Engagement',secondary=connection, backref='personnels',lazy='dynamic')
    diff_1= Column(Integer, default=0)
    diff_2  = Column(Integer, default=0)
    diff_3 = Column(Integer, default=0)
    engagement_lists = Column(String(255), nullable = True)
    
    
    def __init__(self,name,position):
        self.name = name
        self.position = position
        self.engagements = []
        
    #Constraint 1
    #Return a rating on how occupied a person is starting from a given date
    def capacity(self,date):
        relevant = []
        for job in self.engagements:
            if job.enddate>= date:
                relevant.append(job) 
        return sum(list(map(lambda x:x.hours,relevant)))
    
    #Constraint 2
    #Return a rating of how busy a person is starting from a given date
    def busyness(self,date):
        busy = 0
        for each in self.engagements:
            busyratio = each.hours/each.deadline #assume constant throughout all days
            weight = 1/(abs((each.enddate - date).days)+1) #+1 to prevent error
            busy += busyratio*weight 
        return busy
    
    #Constraint 3A
    #Return a rating of the overall estimated difficulty of the jobs on-hand starting from a given date
    def diff_scale(self,date):
        count=0
        for k,v in self.breakdown(date).items():
            count+=k*v
        return count
    
    #Constraint 3B
    def breakdown(self,date):
        distribution = {1:0,2:0,3:0} 
        relevant = []
        for job in self.engagements:
            if job.enddate>= date:
                relevant.append(job) 
        for each in relevant:
            distribution[each.difficulty] += 1 
        return distribution

engagediff = {'C1':{'PPA':1,'WACC':1,'Biz Val':1,'Impair':1},'C2':{'PPA':2,\
              'Biz Val':2, 'BM Work':3, 'Others':3}}
class Engagement(Base):
    #run once is sufficient
    __tablename__ = 'jobs'


    id = Column(Integer,primary_key = True)
    name = Column(String(100),unique = True)
    jobtype = Column(String(100))
    difficulty = Column(Integer)
    hours = Column(Float)
    startdate = Column(Date)
    enddate = Column(Date)
    deadline = Column(Integer) #not calculated yet
    requirement = Column(Integer)
    personnel_list = Column(String(255), nullable = True)
    
    def __init__(self,name,jobtype,hours,startdate,enddate,requirement):
        jobtier = jobtype.split(':')
        self.name = name
        self.jobtype = jobtype
        self.difficulty = engagediff[jobtier[0]][jobtier[1]]
        self.hours = hours
        self.startdate = startdate
        self.enddate = enddate
        self.deadline = (enddate-startdate).days + 1
        self.requirement = requirement
        self.personnels = []
        
    def priority(self,person): #wnsure that it is peeps
        if person in self.personnels:
          return person.name + " has been assigned to this engagement"
        elif self.requirement == 0:
          print("Requirement has already been fulfilled")
        else:
          self.personnels.append(person)
          self.requirement -= 1
          if self.difficulty == 1:
              person.diff_1 += 1
          elif self.difficulty == 2:
              person.diff_2 += 1
          else:
              person.diff_3 += 1
          prefresh(person)
          erefresh(self)
    
    def assignment(self,ls): #alot of work to be done here. cant do the sort
        while self.requirement != 0:
            #filter bottom 50th percentile 
            
            #constraint 1:Capacity
            ls.sort(key = lambda x: x.capacity(self.startdate))
            ls = ls[:int(0.50*len(ls))+1]
            
            #constraint 2: Busyness
            ls.sort(key=lambda x: x.busyness(self.enddate))
            ls=ls[:int(0.50*len(ls))+1] 
            
            #constraint 3 Difficulty
            ls.sort(key=lambda x: x.diff_scale(self.startdate))
            ls=ls[:int(0.50*len(ls))+1]
            
            selected = random.choice(ls) #Random selection from resultant personnel
            self.requirement -= 1
            self.personnels.append(selected)
            
            if self.difficulty == 1:
                selected.diff_1 += 1
            elif self.difficulty == 2:
                selected.diff_2 += 1
            else:
                selected.diff_3 += 1
            prefresh(selected)
        erefresh(self)
        print("Requirement has already been fulfilled")
            
        
    #remove externally
    def extend_deadline(self,new_end_date):
        if new_end_date> self.enddate:
            self.deadline += (new_end_date - self.enddate).days
            self.enddate = new_end_date
        else:
            print("Please check your new end date.")
               
        
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

def prefresh(peeps):
  job = str([each.name for each in peeps.engagements])
  peeps.engagement_lists = job

def erefresh(job):
  peeps = str([each.name for each in job.personnels])
  job.personnel_list = peeps
################################################################################################################  
################################################################################################################
  
  
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
  engine = create_engine('sqlite:///Schedule.db', echo=False)
  Base = declarative_base()
  Session = sessionmaker(bind=engine)
  s = Session() #Connection to the system
  Base.metadata.create_all(engine)
  rows = s.execute('Select * from people')
  return render_template("view_personnel.html",rows = rows)


@app.route('/viewengagements')
def viewengagements():
  engine = create_engine('sqlite:///Schedule.db', echo=False)
  Base = declarative_base()
  Session = sessionmaker(bind=engine)
  s = Session() #Connection to the system
  Base.metadata.create_all(engine)
  rows = s.execute('Select * from jobs')
  return render_template("view_engagements.html",rows = rows)



@app.route('/searchpersonnel', methods=['GET', 'POST'])
def searchpersonnel():
  form = SearchPersonnelForm()
  if form.validate_on_submit():
    engine = create_engine('sqlite:///Schedule.db', echo=False)
    Base = declarative_base()
    Session = sessionmaker(bind=engine)
    s = Session() #Connection to the system
    Base.metadata.create_all(engine)
    rows = s.query(Personnel).filter(Personnel.name == form.Personnel.data).all()

    return render_template("view_personnel.html",rows = rows)
  return render_template('searchpersonnel.html', title='Search for Personnel', form=form)

@app.route('/searchengagement', methods=['GET', 'POST'])
def searchengagement():
  form = SearchEngagementForm()
  if form.validate_on_submit():
    engine = create_engine('sqlite:///Schedule.db', echo=False)
    Base = declarative_base()
    Session = sessionmaker(bind=engine)
    s = Session() #Connection to the system
    Base.metadata.create_all(engine)
    rows = s.query(Engagement).filter(Engagement.name == form.Engagement.data).all()

    return render_template("view_engagements.html",rows = rows)
  return render_template('searchengagement.html', title='Search for Engagement', form=form)
 

@app.route('/addnewpersonnel', methods=['GET', 'POST'])
def addnewpersonnel():
  engine = create_engine('sqlite:///Schedule.db', echo=False)
  Base = declarative_base()
  Session = sessionmaker(bind=engine)
  s = Session() #Connection to the system
  Base.metadata.create_all(engine)
  form = AddPersonForm()
  if form.validate_on_submit():
    name = form.Name.data
    position = form.Position.data

    person = Personnel(name,position)
    s.add(person)
    s.commit()
    return render_template('addedpersonnel.html')
  return render_template('addnewpersonnel.html', form=form)



@app.route('/addnewengagement', methods=['GET', 'POST'])
def addnewengagement():
  engine = create_engine('sqlite:///Schedule.db', echo=False)
  Base = declarative_base()
  Session = sessionmaker(bind=engine)
  s = Session() #Connection to the system
  Base.metadata.create_all(engine)
  form = AddEngagementForm()
  if form.validate_on_submit():
    name = form.Name.data
    jobtype = form.Job.data
    hours = form.Hours.data
    startdate = form.Start_Date.data
    enddate = form.End_Date.data
    requirement = form.Requirement.data
    engage = Engagement(name,jobtype,hours,startdate,enddate,requirement)
    s.add(engage)
    s.commit()
    return render_template('addedengagement.html')
  return render_template('addnewengagement.html', form=form)

@app.route('/deletepersonnel', methods=['GET', 'POST'])
def deletepersonnel():
  engine = create_engine('sqlite:///Schedule.db', echo=False)
  Base = declarative_base()
  Session = sessionmaker(bind=engine)
  s = Session() #Connection to the system
  Base.metadata.create_all(engine)
  form = RemovePersonForm()
  if form.validate_on_submit():
      pselected = s.query(Personnel).filter(Personnel.name == form.person.data).first()
      for each in pselected.engagements:
          each.requirement += 1
          each.personnels.remove(pselected)
          erefresh(each)
      s.delete(pselected)
      s.commit()
      return render_template('deletedpers.html')
  return render_template('deletepersonnel.html',form=form)

@app.route('/deleteengagement', methods=['GET', 'POST'])
def deleteengagement():
  engine = create_engine('sqlite:///Schedule.db', echo=False)
  Base = declarative_base()
  Session = sessionmaker(bind=engine)
  s = Session() #Connection to the system
  Base.metadata.create_all(engine)
  form = RemoveEngagementForm()
  if form.validate_on_submit():
    eselected = s.query(Engagement).filter(Engagement.name == form.engagement.data).first()
    try:
      for eachpeeps in eselected.personnels:
          if eselected.difficulty == 1:
              eachpeeps.diff_1 -= 1
          elif eselected.difficulty == 2:
              eachpeeps.diff_2 -= 1
          else:
              eachpeeps.diff_3 -= 1
          eselected.personnels.remove(eachpeeps)
          prefresh(eachpeeps)
      s.delete(eselected) 
      s.commit()
    except:
      s.delete(eselected) 
      s.commit()
    return render_template('deletedeng.html')
  return render_template('deleteengagement.html',form=form)

@app.route('/assign_engagement', methods=['GET', 'POST'])
def assign():
    engine = create_engine('sqlite:///Schedule.db', echo=False)
    Base = declarative_base()
    Session = sessionmaker(bind = engine)
    s = Session()
    Base.metadata.create_all(engine)
    
    form = AssignEngagementForm()
    if form.validate_on_submit():
        personname = ()
        eselected =  s.query(Engagement).filter(Engagement.name == form.Engagement.data).first()
        
        #priority assignment
        if form.Person1.data:
            personname += (form.Person1.data,)
        if form.Person2.data:
            personname += (form.Person2.data,)
        if personname:
            for each in personname:
                pselected = s.query(Personnel).filter(Personnel.name == each).first()
                eselected.priority(pselected)
        s.commit()
        
        #random assignment
        all_personnel = s.query(Personnel).all()
        ls = []
        for each in all_personnel:
            if each.name not in [x.name for x in eselected.personnels]:
                ls.append(each)
        eselected.assignment(ls)
        s.commit()
        return render_template('engagementassigned.html')
    return render_template('assign_engagement.html',form = form)

@app.route('/extenddeadline',methods = ['GET','POST'])
def time_extension():
    engine = create_engine('sqlite:///Schedule.db', echo=False)
    Base = declarative_base()
    Session = sessionmaker(bind = engine)
    s = Session()
    Base.metadata.create_all(engine)
    form = ExtendEngagementForm()
    if form.validate_on_submit():
        eselected = s.query(Engagement).filter(Engagement.name == form.Engagement.data).first()
        eselected.extend_deadline(form.NewDate.data)
        s.commit() 
        return render_template('extendedeng.html')
    return render_template('extenddeadline.html',form=form)

@app.route('/pulloutpersonnel',methods = ['GET','POST'])
def pullout_personnel():
    engine = create_engine('sqlite:///Schedule.db', echo=False)
    Base = declarative_base()
    Session = sessionmaker(bind=engine)
    s = Session()
    Base.metadata.create_all(engine)
    
    form = PulloutPersonnelForm()
    
    if form.validate_on_submit():
        eselected =  s.query(Engagement).filter(Engagement.name == form.Engagement.data).first()
        pselected = s.query(Personnel).filter(Personnel.name == form.Personnel.data).first()
        if pselected not in eselected.personnels:
            print("Error: Personnel not found in engagement") #How to raise Error instead?
        else:
            if eselected.difficulty == 1:
                pselected.diff_1 -= 1
            elif eselected.difficulty == 2:
                pselected.diff_2 -= 1
            else:
                pselected.diff_3 -= 1
            eselected.personnels.remove(pselected)
            eselected.requirement += 1
            prefresh(pselected)
            erefresh(eselected)
            s.commit()
            return render_template('personnelpulled.html')
    return render_template('pulloutpersonnel.html',form=form)




                              
