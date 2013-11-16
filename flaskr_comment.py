# -*- coding: utf-8 -*

#make life much easeier to have set these variables.
import os
AbsPath = os.path.abspath(__file__)
SITEDIRNAME = os.path.dirname(AbsPath)
MEDIADIR = os.path.join(SITEDIRNAME, 'media')
STATICDIR = os.path.join(SITEDIRNAME, 'static')
TEMPLATEDIR = os.path.join(SITEDIRNAME, 'templates')

"""
General
"""
#Flaks - main module for flask
#url_for - generate URL given the function name and parameters
#redirect() - redirect a user to another endpoint
#return redirect(url_for('login'))
#abort() -  abort a request early
#abort(401)
#render_template - render a template based on Ninja2 syntax
#request - request object
#see http://flask.pocoo.org/docs/reqcontext/
#flask - flash a message for user to notify what's done
from flask import Flask, url_for, abort, redirect, render_template, request
from flask import flash
from datetime import datetime

"""
Database
"""
#load the flask-sqlalchemy extension
from flask.ext.sqlalchemy import SQLAlchemy

"""
Debug Tool
"""
#load the flask-debugtoolbar extension
from flask_debugtoolbar import DebugToolbarExtension

"""
For Markdown and yaml
"""
import yaml
from flaskext.markdown import Markdown

"""
For Admin
"""
#from flask.ext import something will translate into from flask import flask_something
#load flask_admin extension
from flask.ext import admin
#load flask_login extention
from flask.ext import login
#from flask_admin.contrib load sqla
from flask.ext.admin.contrib import sqla
#from flask_admin import helpers
from flask.ext.admin import helpers

"""
For Forms 
"""
#load wtfrom
from wtforms import form, fields, validators

"""
login
"""
#from flask_login import loginManager
from flask.ext.login import LoginManager

#initial a instance of Flask application.
app = Flask(__name__)
#set debug on
app.debug = True
#load configs from config.py
app.config.from_object('config')
#initial a sqlalchemy session for the app
db = SQLAlchemy(app)
#initla a markdown instance
md = Markdown(app, extensions = ['codehilite'] )
#toolbar = DebugToolbarExtension(app)





"""
Login
"""
##note db.Model suggest using flask_sqlalchemy extension
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120))
    password = db.Column(db.String(64))

    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    # Required for administrative interface
    def __unicode__(self):
        return self.username
        
#LoginForm is a sub-object of form.Form from wtforms.   
class LoginForm(form.Form):
    #login is a fields.TextField instance
    #[validators.required()] means this field is mandatory
    login = fields.TextField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])
    
    #self in a object context, just refer to itself
    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Invalid user')

        if user.password != self.password.data:
            raise validators.ValidationError('Invalid password')

    def get_user(self):
        return db.session.query(User).filter_by(login=self.login.data).first()



class RegistrationForm(form.Form):
    login = fields.TextField(validators=[validators.required()])
    email = fields.TextField()
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        if db.session.query(User).filter_by(login=self.login.data).count() > 0:
            raise validators.ValidationError('Duplicate username')

def init_login():
    login_manager = login.LoginManager()
    login_manager.setup_app(app)
    
    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.query(User).get(user_id)



# Create customized model view class
class MyModelView(sqla.ModelView):
    def is_accessible(self):
        return login.current_user.is_authenticated()


# Create customized index view class
class MyAdminIndexView(admin.AdminIndexView):
    def is_accessible(self):
        return login.current_user.is_authenticated()



@app.route('/')
def index():
    return render_template('index.html', user=login.current_user)

@app.route('/login/',methods = ('GET', 'POST'))
def login_view():
    form = LoginForm(request.form)
    if helpers.validate_form_on_submit(form):
        user = form.get_user()
        flash("Logged in successfully.")
        login.login_user(user)
        return redirect(url_for('index'))
        
    return render_template('form.html', form=form)
    
            

@app.route('/register/',methods=['GET','POST'])
def register_view():
    form = RegistrationForm(request.form)
    if helpers.validate_form_on_submit(form):
        user = User()
        form.populate_obj(user)
        
        db.session.add(user)
        db.session.commit()
        
        login.login_user(user)
        return redirect(url_for('index'))
    
    return render_template('form.html', form=form)


@app.route('/logout/')
def logout_view():
    login.logout_user()
    return redirect(url_for('index'))
    


@login_required
@app.route('/suspects')
def display_suspects():
    s=Country.query.all()
    users=User.query.all()
    return render_template('suspects.html',
                s=s,
                users=users)


"""
Model
"""

class DatabaseInfo(db.Model):
    __tablename__ = 'DatabaseInfo'
    
    DatabaseName = db.Column(db.String(20), primary_key = True)
    RecordIDType = db.Column(db.String(20), nullable = False)
    ContentSetName = db.Column(db.String(20), nullable = False)
    
    def __str__(self):
        return '<Database %s>' % self.DatabaseName


class Person(db.Model):
    __tablename__ = 'Person'

    EmployeeID = db.Column(db.String(10), primary_key = True)
    FirstName = db.Column(db.String(40), nullable = True)
    LastName = db.Column(db.String(40), nullable = True)
    MiddleName = db.Column(db.String(40), nullable = True)
    Email = db.Column(db.String(120), nullable = True)
    LocationID = db.Column(db.Integer, db.ForeignKey('Location.LocationID'))
    location = db.relationship('Location', 
                backref = db.backref('Person', lazy='dynamic'))
    #how to define one-to-many relatinoships on same table???
    ReportTo = db.Column(db.String(10), db.ForeignKey('Person.EmployeeID'))
    JoinDate = db.Column(db.DateTime, nullable = True)
    EndDate = db.Column(db.DateTime, nullable = True)
    RoleID = db.Column(db.Integer, db.ForeignKey('PersonRole.RoleID'))
    personrole = db.relationship('PersonRole', 
                backref = db.backref('Person', lazy='dynamic'))

    def __str__(self):
        return '<Person %s %s>' % (self.LastName, self.FirstName)


class Screener(db.Model):
    __tablename__ = 'Screener'
    
    ScreenerID = db.Column(db.Integer, primary_key=True)
    ScreenerName = db.Column(db.String(255), nullable=False)
    ScreenerDescription = db.Column(db.Text, nullable=True)
    Script = db.Column(db.Text, nullable=False)
    HitRate = db.Column(db.Float(10,2), nullable=False)
    CreateDate = db.Column(db.DateTime, nullable=False)
    #CreatePersonID = db.Column(db.Integer, nullable=False)
    CreatePersonID = db.Column(db.String(10), db.ForeignKey('Person.EmployeeID'))
    person = db.relationship(Person, backref='Screener')
    SuspectReason = db.Column(db.Text, nullable=False)
    IsExtremeOutlier = db.Column(db.Boolean, nullable=False)
    #DatabaseName = db.Column(db.Integer, nullable=False)
    DatabaseName = db.Column(db.String(20), db.ForeignKey('DatabaseInfo.DatabaseName'))
    databaseinfo = db.relationship(DatabaseInfo, backref='Screener') 
    
    def __str__(self):
        return '<Script - %s>' % self.ScreenerName
         
    def __init__(self, ScreenerName="", Script="", HitRate="", CreatePersonID="",
        SuspectReason="",IsExtremeOutlier="",DatabaseName="",ScreenerDescription=None, CreateDate=None):
        self.ScreenerName = ScreenerName
        self.Script = Script
        self.HitRate = HitRate
        self.CreatePersonID = CreatePersonID
        self.SuspectReason = SuspectReason
        self.IsExtremeOutlier = IsExtremeOutlier
        self.DatabaseName = DatabaseName
        self.CreatePersonID = CreatePersonID
        if CreateDate is None:
            CreateDate = datetime.utcnow()
        self.CreateDate = CreateDate
        self.ScreenerDescription = ScreenerDescription
               
    def __repr__(self):
        return '<Script %r>' % self.ScreenerName


    
class SuspectDataPoint(db.Model):
    __tablename__ ='SuspectDataPoint'
    
    SuspectID = db.Column(db.Integer, primary_key=True)
    RecordID  = db.Column(db.String(30), nullable=False)
    Field = db.Column(db.String(30), nullable=False)
    ScreenerID = db.Column(db.Integer, db.ForeignKey('Screener.ScreenerID'))
    screener = db.relationship('Screener',
            backref=db.backref('SuspectDataPoint', lazy='dynamic'))
    ScreenDate = db.Column(db.DateTime, nullable=False)
    SuspectDetails = db.Column(db.Text, nullable=True)
    PeriodEndDate = db.Column(db.DateTime, nullable=False)
    FieldEntryDate = db.Column(db.DateTime, nullable=False)
    OriginalValue = db.Column(db.String(100), nullable=True)
    Source = db.Column(db.String(100), nullable=False)
    UniqueSystemID = db.Column(db.Integer, nullable=False)
    DatabaseAccountCode = db.Column(db.String(50), nullable=False)
    RecordUpdateType = db.Column(db.String(60), nullable=True)
    UploadDate = db.Column(db.DateTime, nullable=False)
    
    def __str__(self):
        return '<SuspectID - %d >' % self.SuspectID
        
    def __init__(self, RecordID="", Field="", screener=screener, ScreenDate="",
                SuspectDetails="", PeriodEndDate="", FieldEntryDate="",
                OriginalValue="", Source="", UniqueSystemID="", DatabaseAccountCode="",
                RecordUpdateType="", UploadDate=""):
        self.RecordID = RecordID
        self.Field = Field
        self.ScreenerID = screener
        self.ScreenDate = ScreenDate   
        self.SuspectDetails = SuspectDetails
        self.PeriodEndDate = PeriodEndDate
        self.FieldEntryDate = FieldEntryDate
        self.OriginalValue = OriginalValue
        self.Source = Source
        self.UniqueSystemID = UniqueSystemID
        self.DatabaseAccountCode = DatabaseAccountCode
        self.RecordUpdateType = RecordUpdateType
        self.UploadDate = UploadDate

    

class PersonRole(db.Model):
    __tablename__ = 'PersonRole'
    RoleID = db.Column(db.Integer, primary_key = True)
    RoleTitle = db.Column(db.String(40), nullable = False)
    GRFID = db.Column(db.Integer, nullable = True)
    
    def __str__(self):
        return '<Role %s>' % self.RoleTitle
  

class Location(db.Model):
    __tablename__ = 'Location'
    LocationID = db.Column(db.Integer, primary_key = True)
    LocationCode = db.Column(db.String(3), nullable = False)
    LocationName = db.Column(db.String(20), nullable = False)
    
    def __str__(self):
        return '<Location %s>' % self.LocationName

class Country(db.Model):
    __tablename__ = 'Country'
    CountryCode = db.Column(db.String(3), primary_key = True)
    CountryName = db.Column(db.String(40), nullable = False)
    ISO2CountryCode = db.Column(db.String(2), nullable = False)
    ISO3CountryCode = db.Column(db.String(3), nullable = False)
    
    def __init__(self, CountryCode="", CountryName="", ISO2CountryCode="", ISO3CountryCode="" ):
        self.CountryCode=CountryCode
        self.CouuntryName = CountryName
        self.ISO2CountryCode =ISO2CountryCode
        self.ISO3CountryCode = ISO3CountryCode
    
    def __str__(self):
        return '<Country %s>' % self.CountryName
        

    


class ProductionLocation(db.Model):
    __tablename__ = 'ProductionLocation'
    ProductionLocationID = db.Column(db.Integer, primary_key=True)
    CountryCode = db.Column(db.String(3), nullable=False)
    DatabaseName = db.Column(db.String(20), nullable=False)
    LocationID = db.Column(db.Integer, db.ForeignKey('Location.LocationID'))
    location = db.relationship('Location',
                backref=db.backref('ProductionLocation', lazy='dynamic'))  

class DatabaseAccount(db.Model):
    __tablename__ = 'DatabaseAccount'
    DatabaseAccountCode = db.Column(db.String(50), primary_key=True)
    DatabaseName = db.Column(db.String(20), db.ForeignKey('DatabaseInfo.DatabaseName'))
    databaseinfo = db.relationship('DatabaseInfo',
                backref=db.backref('DatabaseAccount', lazy='dynamic'))
    EmployeeID = db.Column(db.String(10), db.ForeignKey('Person.EmployeeID'))
    person = db.relationship('Person',
                backref=db.backref('DatabaseAccount', lazy='dynamic'))


    
class FieldAttribute(db.Model):
    __tablename__ = 'FieldAttribute'
    FieldAttributeID = db.Column(db.Integer, primary_key=True)
    Field = db.Column(db.String(30), nullable=False)
    DatabaseName = db.Column(db.String(20), nullable=False)
    AttributeName = db.Column(db.String(40), nullable=False)
    AttributeValue = db.Column(db.String(255), nullable=False)
    

class SuspectComment(db.Model):
    __tablename__ = 'SuspectComment'
    SuspectID = db.Column(db.Integer, db.ForeignKey('SuspectDataPoint.SuspectID'),primary_key=True)
    suspectdatapoint = db.relationship('SuspectDataPoint',
                backref=db.backref('SuspectComment', lazy='dynamic'))
    IsError = db.Column(db.Boolean, nullable = False)
    IsCIPError = db.Column(db.Boolean, nullable = False)
    CorrectedBy = db.Column(db.String(10), db.ForeignKey('DatabaseAccount.DatabaseAccountCode'))
    CorrectedOn = db.Column(db.DateTime, nullable=False)
    OpsComments = db.Column(db.Text, nullable=True)
    QualityComments = db.Column(db.Text, nullable=True)
        


        


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    def __init__(self, name=""):
        self.name = name
    def __repr__(self):
        return '<Category %r>' % self.name        


  
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    body = db.Column(db.Text)
    pub_date = db.Column(db.DateTime)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category',
        backref=db.backref('post', lazy='dynamic'))
        
    def __init__(self, title="", body="", category=None, pub_date=None):
        self.title = title
        self.body = body
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date
        self.category = category    
        
    def __repr__(self):
        return '<Post %r>' % self.title
        

    





class CountryView(sqla.ModelView):
    form_columns = ('CountryCode', 'CountryName','ISO2CountryCode','ISO3CountryCode')
    column_list = ('CountryCode', 'CountryName','ISO2CountryCode','ISO3CountryCode')
    #column_searchable_list = ('title', 'body')
    #column_filters = ('title', 'body')


class DatabaseInfoView(sqla.ModelView):
    form_columns = ('DatabaseName', 'RecordIDType','ContentSetName')
    column_list = ('DatabaseName', 'RecordIDType','ContentSetName')

class ProductionLocationView(sqla.ModelView):
    form_columns = ('CountryCode', 'DatabaseName','location')
    column_list = ('CountryCode', 'DatabaseName','location')


class DatabaseAccountView(sqla.ModelView):
    form_columns = ('DatabaseAccountCode', 'databaseinfo','person')
    column_list = ('DatabaseAccountCode', 'databaseinfo','person')




class PersonView(sqla.ModelView):
    form_columns = ('EmployeeID', 'FirstName','LastName','Email','location','ReportTo',
                    'JoinDate','EndDate','personrole')
    column_list =  ('EmployeeID', 'FirstName','LastName','Email','location','ReportTo',
                    'JoinDate','EndDate','personrole')
                    


class SuspectCommentView(sqla.ModelView):
    form_columns = ('suspectdatapoint', 'IsError','IsCIPError',
            'CorrectedBy','CorrectedOn','OpsComments','QualityComments')
    column_list = ('suspectdatapoint', 'IsError','IsCIPError',
        'CorrectedBy','CorrectedOn','OpsComments','QualityComments')
                 
class FieldAttributeView(sqla.ModelView):
    form_columns = ('Field','DatabaseName','AttributeName','AttributeValue')
    column_list = ('Field','DatabaseName','AttributeName','AttributeValue')
                                                   
#admin.add_view(ModelView(Screener,db.session))
#admin.add_view(ModelView(SuspectDataPoint,db.session))
#admin.add_view(ModelView(PersonRole,db.session))
#admin.add_view(ModelView(Location,db.session))
#admin.add_view(CountryView(Country,db.session))
#admin.add_view(DatabaseInfoView(DatabaseInfo,db.session))
#admin.add_view(ProductionLocationView(ProductionLocation,db.session))
#admin.add_view(DatabaseAccountView(DatabaseAccount,db.session))
#admin.add_view(FieldAttributeView(FieldAttribute,db.session))
#admin.add_view(SuspectCommentView(SuspectComment,db.session))
#admin.add_view(PersonView(Person,db.session))



@app.route('/index/')
def md():
    post_add = os.path.join(SITEDIRNAME, 'mypost.yaml')
    post = yaml.load(file(post_add, 'r'))
    return render_template('mytemplate.html', post=post )



#not accessiable with /hello/    
@app.route('/hello')
@app.route('/hello/<name>')
def hello(name):
    return render_template('hello.html',name=name)


@app.route('/user/<username>')
def show_user_profile(username):
    return 'User %s ' % username

@app.route('/post/<int:post_id>')
def show_post(post_id):
    return 'Post %d ' % post_id

if __name__ == '__main__':
    init_login()
    admin = admin.Admin(app, name='My Application',index_view=MyAdminIndexView())
    admin.add_view(MyModelView(User, db.session))
    app.run()    



"""
dummy data
"""
#scr=Screener('name of scr1','selct *',80.31,1,'hahah',True,'fundbpro','this is descriptoion')        
#sdp=SuspectDataPoint('123','ABC',scr,'2013-3-3','details','2013-3-30','2013-3-2','value','sadf',111,'xnp','ss','2013-3-4')
#db.session.add(scr)
#db.session.commit()