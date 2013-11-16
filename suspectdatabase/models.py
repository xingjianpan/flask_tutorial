
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