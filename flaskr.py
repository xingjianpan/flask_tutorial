# -*- coding: utf-8 -*


import os
AbsPath = os.path.abspath(__file__)
SITEDIRNAME = os.path.dirname(AbsPath)
MEDIADIR = os.path.join(SITEDIRNAME, 'media')
STATICDIR = os.path.join(SITEDIRNAME, 'static')
TEMPLATEDIR = os.path.join(SITEDIRNAME, 'templates')

"""
General
"""
from flask import Flask, url_for, redirect, render_template, request
from flask import flash
import datetime
from flask import g
"""
Database
"""
from flask.ext.sqlalchemy import SQLAlchemy

"""
Debug Tool
"""
from flask_debugtoolbar import DebugToolbarExtension

"""
For Markdown and yaml
"""
import yaml
from flaskext.markdown import Markdown

"""
For Admin
"""
from flask.ext import admin
from flask.ext.admin.contrib import sqla
from flask.ext.admin import helpers

"""
For Forms 
"""
from wtforms import form, fields, validators

"""
login
"""
from flask.ext import login
from flask.ext.login import LoginManager,login_required

"""
Email
"""
from flask.ext.mail import Mail


app = Flask(__name__)
app.debug = True
app.config.from_object('config')
db = SQLAlchemy(app)
md = Markdown(app, extensions = ['codehilite'] )
#toolbar = DebugToolbarExtension(app)
login_manager = login.LoginManager()
login_manager.init_app(app)

mail = Mail(app)

# Create user loader function
# this function loads a user from the atabase
@login_manager.user_loader
def load_user(user_id):
    return db.session.query(UserInfo).get(user_id)



def _get_date():
    return datetime.datetime.now()

"""
Login
"""


class UserInfo(db.Model):
    __tablename__ = 'user_info'
    
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120))
    password = db.Column(db.String(64))
    admin_role = db.Column(db.String(64), default='User')
     
    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id
        
    def is_admin(self):
        return self.admin_role == 'SiteAdmin'
    
    def is_forum_admin(self):
        return self.admin_role == 'ForumAdmin'
        
    def is_forum_member(self):
        return self.admin_role == 'ForumUser'

    # Required for administrative interface
    def __unicode__(self):
        return self.email
    


issue_vertical = db.Table('issue_vertical',
        db.Column('vertical_id', db.Integer, db.ForeignKey('vertical.id')),
        db.Column('issue_id', db.Integer, db.ForeignKey('issue.id'))
        )


issue_client = db.Table('client_issue',
        db.Column('client_id', db.Integer, db.ForeignKey('client.id')),
        db.Column('issue_id', db.Integer, db.ForeignKey('issue.id'))
        )
        
issue_invitee = db.Table('issue_invitee',
        db.Column('invitee_id', db.Integer, db.ForeignKey('user_info.id')),
        db.Column('issue_id', db.Integer, db.ForeignKey('issue.id'))
)

issue_product = db.Table('issue_product',
        db.Column('prouct_id', db.Integer, db.ForeignKey('product.id')),
        db.Column('issue_id', db.Integer, db.ForeignKey('issue.id'))
)


issue_contentset = db.Table('issue_contentset',
        db.Column('contentset_id', db.Integer, db.ForeignKey('contentset.id')),
        db.Column('issue_id', db.Integer, db.ForeignKey('issue.id'))
)

    
class IssueStatus(db.Model):
    __tablename__ ='issue_status'
    id = db.Column(db.Integer, primary_key=True)
    short_name = db.Column(db.String(100), unique=True)
    long_name = db.Column(db.Text)
    
    def __unicode__(self):
         return  '%s' % self.long_name

class QualityForum(db.Model):
    __tablename__ ='quality_forum'
    id = db.Column(db.Integer, primary_key=True)
    short_name = db.Column(db.String(10), unique=True)
    long_name = db.Column(db.String(100), unique=True)
    description = db.Column(db.Text)
    
    def __unicode__(self):
         return  '%s' % self.long_name    

#Editable by Forum Member     
class Issue(db.Model):
    __tablename__ = 'issue'
    
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), unique=True)
    severity_id = db.Column(db.Integer,db.ForeignKey('issue_severity.id'))
    severity = db.relationship('IssueSeverity', 
                    backref=db.backref('Issue'))
    description = db.Column(db.Text)
    resolution = db.Column(db.Text)
    IFFM_number = db.Column(db.String(25))
    createdate = db.Column(db.DateTime, default=_get_date)
    modified_date = db.Column(db.DateTime, default=_get_date)
    quality_forum_id = db.Column(db.Integer, db.ForeignKey('quality_forum.id'))
    quality_forum = db.relationship('QualityForum', backref=db.backref('Issue'))
    issue_status_id = db.Column(db.Integer, db.ForeignKey('issue_status.id'))
    issue_status = db.relationship('IssueStatus', 
                backref=db.backref('Issue'))
    clients = db.relationship('Client', secondary=issue_client,
                backref=db.backref('Issue'), lazy='dynamic')
    invitees = db.relationship('UserInfo', secondary=issue_invitee,
                backref=db.backref('Issue'), lazy='dynamic')
    products = db.relationship('Product', secondary=issue_product,
                backref=db.backref('Issue'), lazy='dynamic')
    contensets = db.relationship('ContentSet', secondary=issue_contentset,
                backref=db.backref('Issue'), lazy='dynamic')
    verticals = db.relationship('Vertical', secondary=issue_vertical,
                backref=db.backref('Issue'), lazy='dynamic')


    def __unicode__(self):
        return '[ %d ]: %s' % (self.id, self.title)

class Vertical(db.Model):
    __tablename__ = 'vertical'

    id = db.Column(db.Integer, primary_key = True)
    short_name = db.Column(db.String(10), unique=True)
    long_name = db.Column(db.String(100), unique = True)

    def __unicode__(self):
        return '%s' % self.long_name




class Client(db.Model):
    __tablename__ = 'client'
    
    id = db.Column(db.Integer, primary_key = True)
    short_name = db.Column(db.String(10), unique=True)
    long_name = db.Column(db.String(100), unique = True)
   
    def __unicode__(self):
        return '[Client] %s' % self.long_name

class Product(db.Model):
    __tablename__ = 'product'   
    id = db.Column(db.Integer, primary_key = True)
    short_name = db.Column(db.String(10), unique=True)
    long_name = db.Column(db.String(100), unique = True)
    
    def __unicode__(self):
        return '[Product] %s' % self.long_name


class ContentSet(db.Model):
    __tablename__ = 'contentset'

    id = db.Column(db.Integer, primary_key = True)
    short_name = db.Column(db.String(10), unique=True)
    long_name = db.Column(db.String(100), unique = True)    

    def __unicode__(self):
        return '[ContentSet] %s' % self.long_name




class IssueSeverity(db.Model):
    __tablename__ = 'issue_severity'

    id = db.Column(db.Integer, primary_key = True)
    short_name = db.Column(db.String(10), unique=True)
    long_name = db.Column(db.String(100), unique = True)

    def __unicode__(self):
        return '%s' % self.long_name

#Editable by Forum Adimin    
class IssueStatusHistory(db.Model):
    __tablename__ = 'issue_status_history'
    id = db.Column(db.Integer,primary_key = True)
    issue_id = db.Column(db.Integer, db.ForeignKey('issue.id'))
    issue = db.relationship('Issue', backref=db.backref('IssueStatusHistory'))
    status_date = db.Column(db.DateTime)
    issuestatus_id = db.Column(db.Integer, db.ForeignKey('issue_status.id'))
    issuestatus = db.relationship('IssueStatus', backref=db.backref('IssueStatusHistory'))    

class IssueContributorType(db.Model):
    __tablename__ = 'issue_contributor_type'
    id = db.Column(db.Integer, primary_key = True)
    short_name = db.Column(db.String(25), unique=True)
    long_name = db.Column(db.String(100))

    def __unicode__(self):
        return '%s' % self.long_name
            
#Editable by Forum Member 
class IssueContributor(db.Model):
    __tablename__ = 'issue_contributor'
    
    id = db.Column(db.Integer, primary_key = True)
    issue_id = db.Column(db.Integer, db.ForeignKey('issue.id'))
    issue = db.relationship('Issue', backref=db.backref('IssueContributor'))
    #Raiser, accountable_owner, responsible_owner, forum_owner, commenter, VOC_supplier
    contributor_type_id = db.Column(db.Integer, db.ForeignKey('issue_contributor_type.id'))      
    contributor_type = db.relationship('IssueContributorType', 
            backref=db.backref('IssueContributor'))
    contributor_id = db.Column(db.Integer, db.ForeignKey('user_info.id'))
    contributor = db.relationship('UserInfo', 
            backref=db.backref('IssueContributor'))


class IssueAnalysisType(db.Model):
    __tablename__ = 'issue_analysis_type'
    id = db.Column(db.Integer, primary_key = True)
    short_name = db.Column(db.String(25), unique=True)
    long_name = db.Column(db.String(100))

    def __unicode__(self):
        return '%s' % self.long_name    



#Editable by Forum Member     
class IssueAnalysis(db.Model):
    __tablename__ = 'issue_analysis'
    
    id = db.Column(db.Integer, primary_key = True)
    issue_id = db.Column(db.Integer, db.ForeignKey('issue.id'))
    issue = db.relationship('Issue', backref=db.backref('IssueAnalysis'))
    issue_analysis_type_id = db.Column(db.Integer, db.ForeignKey('issue_analysis_type.id'))
    issue_analysis_type = db.relationship('IssueAnalysisType',
                    backref=db.backref('IssueAnalysis'))
    comments = db.Column(db.Text)

#Editable by Forum Adimin    
class IssueAction(db.Model):
    __tablename__ = 'issue_action'
    id = db.Column(db.Integer, primary_key = True)
    issue_id = db.Column(db.Integer, db.ForeignKey('issue.id'))
    issue = db.relationship('Issue', backref=db.backref('IssueActions'))
    action_date = db.Column(db.DateTime)
    action = db.Column(db.Text)
    action_by = db.Column(db.String(25))

#Editable by Forum Member
class IssueComment(db.Model):
    __tablename__ = 'issue_comment'
    
    id = db.Column(db.Integer, primary_key = True)
    issue_id = db.Column(db.Integer, db.ForeignKey('issue.id'))
    issue = db.relationship('Issue', backref=db.backref('IssueComments'))
    comment_date = db.Column(db.DateTime)
    comment = db.Column(db.Text)
    comment_by_id = db.Column(db.Integer,db.ForeignKey('user_info.id'))
    comment_by = db.relationship('UserInfo', backref=db.backref('IssueComment'))
    

#Need to rethink about this model
#Editable by Forum Adimin

class IssueScheduleType(db.Model):
    __tablename__ ='issue_schedule_type'
    id = db.Column(db.Integer, primary_key = True)
    short_name = db.Column(db.String(25), unique=True)
    long_name = db.Column(db.String(100), unique=True)
    
    def __unicode__(self):
        return '%s' % self.long_name

class IssueSchedule(db.Model):
    __tablename__ = 'issue_schedule'
    id = db.Column(db.Integer, primary_key = True)
    issue_id = db.Column(db.Integer, db.ForeignKey('issue.id'))
    issue = db.relationship('Issue', backref=db.backref('IssueReviewSchedule'))
    schedule_type_id = db.Column(db.Integer, db.ForeignKey('issue_schedule_type.id'))
    schedule_type = db.relationship('IssueScheduleType', 
                        backref=db.backref('IssueSchedule'))
    schedule_date = db.Column(db.DateTime)
    

# Create customized model view class
class AdminView(sqla.ModelView):
    def is_accessible(self):
        return login.current_user.is_authenticated() and login.current_user.is_admin()

class UserView(sqla.ModelView):
    def is_accessible(self):
        return login.current_user.is_authenticated()
    

# Create customized index view class
class AdminIndexView(admin.AdminIndexView):
    def is_accessible(self):
        return login.current_user.is_authenticated()

        
class LoginForm(form.Form):
    login = fields.TextField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Invalid user')

        if user.password != self.password.data:
            raise validators.ValidationError('Invalid password')

    def get_user(self):
        return db.session.query(UserInfo).filter_by(login=self.login.data).first()


class RegistrationForm(form.Form):
    login = fields.TextField(validators=[validators.required()])
    email = fields.TextField(validators=[validators.Email()])
    password = fields.PasswordField('Password', validators=[validators.required(),
                                    validators.EqualTo('confirm', message = 'Passwords must match')])
    confirm = fields.PasswordField('Repeat Password')

    def validate_login(self, field):
        if db.session.query(UserInfo).filter_by(login=self.login.data).count() > 0:
            raise validators.ValidationError('Duplicate username')



@app.route('/issue/<int:issue_id>/')
def issue_detail_view(issue_id):
    issue = Issue.query.get(issue_id)
    #issue_analysis = IssueAnalysis.query.filter_by(issue_id=issue.id).all()
    issue_contributors = IssueContributor.query.filter_by(issue_id=issue.id).join(IssueContributorType).all()
    issue_analysis = IssueAnalysis.query.filter_by(issue_id=issue.id).join(IssueAnalysisType).all()
    issue_actions = IssueAction.query.filter_by(issue_id=issue.id).all()
    issue_comments = IssueComment.query.filter_by(issue_id=issue.id).all()
    issue_timeline = IssueStatusHistory.query.filter_by(issue_id=issue.id).join(IssueStatus).all()
    return render_template('issue_detail.html', issue=issue,
                                                issue_analysis=issue_analysis,
                                                issue_actions=issue_actions,
                                                issue_comments=issue_comments,
                                                issue_contributors=issue_contributors,
                                                issue_timeline=issue_timeline,
                                                user=login.current_user)
    
@app.route('/')
def issue_view():
    issues = Issue.query.all()
    return render_template('issue.html', issues=issues,
                            user=login.current_user)

@app.route('/severity/<int:severityid>')
def severity_view(severityid):
    issues = Issue.query.filter_by(severity_id=severityid).all()
    return render_template('issue.html', issues=issues,
                                user=login.current_user)
 
@app.route('/vertical/<int:verticalid>')
def vertical_view(verticalid):
    issues = Issue.query.join(Issue.verticals).filter(Vertical.id==verticalid).all()
    return render_template('issue.html', issues=issues,
                                user=login.current_user)


@app.route('/client/<int:clientid>')
def client_view(clientid):
    issues = Issue.query.join(Issue.clients).filter(Client.id==clientid).all()
    return render_template('issue.html', issues=issues,
                                user=login.current_user)
 
 
@app.route('/status/<int:statusid>')
def status_view(statusid):
    issues = Issue.query.filter_by(issue_status_id=statusid).all()
    return render_template('issue.html', issues=issues,
                                user=login.current_user)



@app.route('/forum/<int:forumid>')
def forum_view(forumid):
    issues = Issue.query.filter_by(quality_forum_id=forumid).all()
    return render_template('issue.html', issues=issues,
                                user=login.current_user) 
                                
@app.route('/dashboard/<int:userid>')
@login_required
def my_viwe(userid):
    user_id = UserInfo.query.filter_by(id = userid).first().id
    issues_invited =Issue.query.join(Issue.invitees).filter(UserInfo.id==user_id).all()
    rm_id=IssueContributorType.query.filter_by(short_name='RM').first().id
    ao_id=IssueContributorType.query.filter_by(short_name='AO').first().id
    #issue_id_as_rm=IssueContributor.query.filter_by(contributor_type_id=rm_id).filter_by(contributor_id=ser_id).all()
    issues_as_rm=Issue.query.join(IssueContributor).filter_by(contributor_id=user_id).filter_by(contributor_type_id=rm_id).all()
    issues_as_ao=Issue.query.join(IssueContributor).filter_by(contributor_id=user_id).filter_by(contributor_type_id=ao_id).all()   
    return render_template('dashboard.html', issues_invited=issues_invited,
                                            issues_as_rm=issues_as_rm,
                                            issues_as_ao=issues_as_ao,
                                    user=login.current_user)                   

@app.route('/login/',methods = ('GET', 'POST'))
def login_view():
    form = LoginForm(request.form)
    if helpers.validate_form_on_submit(form):
        user = form.get_user()
        login.login_user(user)
        return redirect(url_for('issue_view'))
        
    return render_template('form.html', form=form)
    
            

@app.route('/register/',methods=['GET','POST'])
def register_view():
    form = RegistrationForm(request.form)
    if helpers.validate_form_on_submit(form):
        user = UserInfo()
        form.populate_obj(user)
        
        db.session.add(user)
        db.session.commit()
        flash('Logging you in')
        login.login_user(user)
        return redirect(url_for('issue_view'))
    
    return render_template('form.html', form=form)


@app.route('/logout/')
def logout_view():
    login.logout_user()
    return redirect(url_for('issue_view'))

    

@app.route('/suspects')
@login_required
def display_suspects():
    s=Country.query.all()
    users=UserInfo.query.all()
    return render_template('suspects.html',
                s=s,
                users=users)

#error handler
@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


                                                   
admin = admin.Admin(app, name='My Application',index_view=AdminIndexView())
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
admin.add_view(AdminView(UserInfo, db.session))
admin.add_view(UserView(Issue, db.session))
admin.add_view(AdminView(QualityForum, db.session))
admin.add_view(UserView(IssueContributor, db.session))
admin.add_view(AdminView(IssueContributorType, db.session))
admin.add_view(UserView(IssueAnalysis, db.session))
admin.add_view(UserView(IssueAction, db.session))
admin.add_view(UserView(IssueComment, db.session))
admin.add_view(AdminView(IssueStatus, db.session))
admin.add_view(UserView(IssueSchedule, db.session))
admin.add_view(AdminView(IssueScheduleType, db.session))
admin.add_view(AdminView(Client, db.session))
admin.add_view(AdminView(Product, db.session))
admin.add_view(AdminView(ContentSet, db.session))
admin.add_view(UserView(IssueStatusHistory, db.session))
admin.add_view(AdminView(Vertical, db.session))
admin.add_view(AdminView(IssueSeverity, db.session))
admin.add_view(AdminView(IssueAnalysisType, db.session))
"""
User
Issue
IssueContributor
IssueAnalysis
IssueAction
IssueComment
IssueStatus
IssueReviewSchedule
"""
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
    app.run()    



"""
dummy data
"""


"""
from flaskr import UserInfo, Issue, Client, Product, ContentSet
from flaskr import IssueContributor, IssueAnalysis, IssueAction,IssueContributorType
from flaskr import IssueComment, IssueStatus, IssueSchedule

scr=Screener('name of scr1','selct *',80.31,1,'hahah',True,'fundbpro','this is descriptoion')        
sdp=SuspectDataPoint('123','ABC',scr,'2013-3-3','details','2013-3-30','2013-3-2','value','sadf',111,'xnp','ss','2013-3-4')
db.session.add(scr)
db.session.commit()
a=IssueStatus.query.filter_by(issue_id=1).order_by(IssueStatus.status_date.desc()).first()
"""

"""
>>> from flaskr import app
>>> from flask.ext.sqlalchemy import SQLAlchemy
>>> db = SQLAlchemy(app)
>>> db
<SQLAlchemy engine='postgresql+psycopg2://xingjian:xingjian@localhost/flaskr'>
>>>
"""