from flask import Flask , render_template , redirect , url_for , request , session , flash
from flask_sqlalchemy import SQLAlchemy # type: ignore
from functools import wraps
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


################    Configs    ################

app = Flask(__name__)
app.secret_key = "S7OuN?1g=U^.p^Ng4.Y#b7)+j<Tm6l4{Mzx_a`yK;0r3Ooq'c"
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:shadow123%21%40%23S@localhost/costmanage?charset=utf8mb4"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

DB = SQLAlchemy(app)
Argon = PasswordHasher()

################    Tabels    ################

class User(DB.Model):
    __tablename__ = 'user'
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci'
    }

    id = DB.Column(DB.Integer, primary_key=True)
    fname = DB.Column(DB.String(200))
    lname = DB.Column(DB.String(200))
    username = DB.Column(DB.String(200), unique=True, nullable=False)
    password = DB.Column(DB.String(200), nullable=False)
    description = DB.Column(DB.String(500))

    # یک کاربر چندین CostCenter دارد
    cost_centers = DB.relationship(
        "CostCenter",
        backref="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

class CostCenter(DB.Model):
    __tablename__ = 'costCenter'
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci'
    }

    id = DB.Column(DB.Integer, primary_key=True)

    user_id = DB.Column(
        DB.Integer,
        DB.ForeignKey('user.id', ondelete="CASCADE"),
        nullable=False
    )

    name = DB.Column(DB.String(120), nullable=False)
    description = DB.Column(DB.Text)

    # هر CostCenter چندین CostCategory دارد
    cost_categories = DB.relationship(
        "CostCategory",
        backref="cost_center",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    # هر CostCenter چندین CostExtend دارد
    cost_extends = DB.relationship(
        "CostExtend",
        backref="cost_center",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

class CostCategory(DB.Model):
    __tablename__ = 'costCategory'
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci'
    }

    id = DB.Column(DB.Integer, primary_key=True)

    costCenter_id = DB.Column(
        DB.Integer,
        DB.ForeignKey('costCenter.id', ondelete="CASCADE"),
        nullable=False
    )

    name = DB.Column(DB.String(120), nullable=False)
    description = DB.Column(DB.Text)

    # هر Category چندین CostExtend دارد
    cost_extends = DB.relationship(
        "CostExtend",
        backref="cost_category",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

class CostExtend(DB.Model):
    __tablename__ = 'costExtend'
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci'
    }

    id = DB.Column(DB.Integer, primary_key=True)

    costCenter_id = DB.Column(
        DB.Integer,
        DB.ForeignKey('costCenter.id', ondelete="CASCADE"),
        nullable=False
    )

    costCategory_id = DB.Column(
        DB.Integer,
        DB.ForeignKey('costCategory.id', ondelete="CASCADE"),
        nullable=False
    )

    name = DB.Column(DB.String(120), nullable=False)
    description = DB.Column(DB.Text)

    # هر Extend چندین CostDefine دارد
    cost_defines = DB.relationship(
        "CostDefine",
        backref="cost_extend",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

class CostDefine(DB.Model):
    __tablename__ = 'costDefine'
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci'
    }

    id = DB.Column(DB.Integer, primary_key=True)

    costExtend_id = DB.Column(
        DB.Integer,
        DB.ForeignKey('costExtend.id', ondelete="CASCADE"),
        nullable=False
    )

    debit = DB.Column(DB.Float, nullable=False)
    year = DB.Column(DB.Integer)
    month = DB.Column(DB.Integer)
    day = DB.Column(DB.Integer)


with app.app_context():
    DB.create_all()
  
################    CURD Functions    ################


  
################    Views    ################

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

#### notFound
@app.errorhandler(404)
def notFound(error):
    return render_template('404.html')

#### dashboard
@app.route("/dashboard")
@login_required
def dashboard():
    user = User.query.filter_by(id = session["user_id"]).first()
    return render_template('dashboard.html', userInfo = user)

#### costCenters
@app.route("/dashboard/costCenters" , methods = ["POST" , "GET"])
@login_required
def costCenters():
    user = User.query.filter_by(id = session["user_id"]).first()
    selectCC = CostCenter.query.filter_by(user_id=user.id).all()
    
    if request.method == "POST":
        # Insert Cost Center In DB
        if "submitCostCenter" in request.form:
            try:
                cc = CostCenter(user_id = user.id ,
                                name = request.form["costCenterName"],
                                description = request.form["costCenterDesc"]
                                )
                DB.session.add(cc)
                DB.session.commit()
                flash("success")
                return redirect(url_for("costCenters"))
            except:
                #return render_template('costCenters.html', userInfo = user , ccInsert="InsertError" , selectCC = selectCC)
                flash("error")
                return redirect(url_for("costCenters"))
            
        # Delete Cost Center In DB
        if "submitDeleteCostCenter" in request.form:
            try:
                deleteCostCenter = CostCenter.query.filter_by(id = request.form["cc_id"]).first()
                DB.session.delete(deleteCostCenter)
                DB.session.commit()
                return redirect(url_for("costCenters"))
            except:
                return redirect(url_for("costCenters"))
            
            
    return render_template('costCenters.html', userInfo = user , selectCC = selectCC)

#### costCategory
@app.route("/dashboard/costCategory" , methods = ["POST" , "GET"])
@login_required
def costCategory():
    user = User.query.filter_by(id = session["user_id"]).first()
    costCenterList = CostCenter.query.filter_by(user_id = session.get("user_id")).all()
    categoryList = CostCategory.query.join(CostCenter , CostCenter.id == CostCategory.costCenter_id).filter(CostCenter.user_id==session["user_id"]).all()
    
    if request.method == "POST":
        if "insertCostCategory" in request.form:
            try:
                categoryName = request.form.get("categoryName")
                categoryCostCenterID = request.form.get("costCenterID")
                categoryDescription = request.form.get("categoryDescription")
                
                categoryAdd = CostCategory(
                    costCenter_id = categoryCostCenterID ,
                    name = categoryName ,
                    description = categoryDescription
                )
                DB.session.add(categoryAdd)
                DB.session.commit()
                flash("SuccessAddCategory")
                return redirect(url_for("costCategory"))
            except:
                flash("ErrorAddCategory")
                return redirect(url_for("costCategory"))
            
        elif "deleteCostCategory" in request.form:
            try:
                deleteCategory = CostCategory.query.filter_by(id = request.form.get("cg_id")).first()
                DB.session.delete(deleteCategory)
                DB.session.commit()
                flash("SuccessDeleteCategory")
                return redirect(url_for("costCategory"))
            except:
                flash("ErrorDeleteCategory")
                return redirect(url_for("costCategory"))

    return render_template('costCategory.html',
                           userInfo = user ,
                           costCenterList = costCenterList ,
                           categoryList = categoryList
                           )

#### costExtend
@app.route("/dashboard/costExtend" , methods = ["POST" , "GET"])
@login_required
def costExtend():
    user = User.query.filter_by(id = session["user_id"]).first()
    costCenterList = CostCenter.query.filter_by(user_id = session["user_id"]).all() 
    costCatergoryList = CostCategory.query.join(CostCenter , CostCenter.id == CostCategory.costCenter_id).filter(CostCenter.user_id==session["user_id"]).all()
    costExtendList = CostExtend.query.join(CostCenter , CostCenter.id == CostExtend.costCenter_id).join(CostCategory , CostCategory.id == CostExtend.costCategory_id).filter(CostCenter.user_id==session["user_id"]).all()
    
    if request.method == "POST" :
        if "insertCostExtend" in request.form:
            try :
                costExtendName = request.form.get("costExtendName")
                costExtendCostCenterID = request.form.get("costExtendCostCenterID")
                costExtendCostCategoryID = request.form.get("costExtendCostCategoryID")
                costExtendDescription = request.form.get("costExtendDescription")
                
                insertCostExtend = CostExtend(
                    costCenter_id = costExtendCostCenterID,
                    costCategory_id = costExtendCostCategoryID,
                    name = costExtendName,
                    description = costExtendDescription
                )
                DB.session.add(insertCostExtend)
                DB.session.commit()
                flash("insertCostExtendSuccess")
                return redirect(url_for("costExtend"))
            except:
                flash("insertCostExtendError")
                return redirect(url_for("costExtend"))   
        elif "deleteCostExtend" in request.form:
            try:
                deleteCostExtend = request.form.get("ce_id")
                deleteCostExtendQuery = CostExtend.query.filter_by(id = deleteCostExtend).first()
                DB.session.delete(deleteCostExtendQuery)
                DB.session.commit()
                return redirect(url_for("costExtend"))
            except:
                return redirect(url_for("costExtend"))
            
    return render_template('costExtend.html',
                           userInfo = user,
                           costCenterList= costCenterList,
                           costCatergoryList = costCatergoryList,
                           costExtendList = costExtendList
                           )

#### costDefine
@app.route("/dashboard/costDefine" , methods = ["POST" , "GET"])
@login_required
def costDefine():
    user = User.query.filter_by(id = session["user_id"]).first()
    costExtendList = CostExtend.query.join(CostCenter , CostCenter.id == CostExtend.costCenter_id).join(CostCategory , CostCategory.id == CostExtend.costCategory_id).filter(CostCenter.user_id==session["user_id"]).all()
    
    if request.method == "POST":
        if "insertCostDefine" in request.form:
            costExtendID = request.form.get("costExtendID")
            costDebit = request.form.get("debit")
            
            #Date Splite
            debitDate = request.form.get("debitDate")
            year_str, month_str, day_str = debitDate.split("/")
            year = int(year_str)
            month = int(month_str)
            day = int(day_str)

            
            try:
                insertCostDefine = CostDefine(costExtend_id=costExtendID,
                                              debit=costDebit,
                                              year=year,
                                              month=month,
                                              day=day
                                              )
                DB.session.add(insertCostDefine)
                DB.session.commit()
                flash("insertCostDefineSuccess")
                return redirect(url_for("costDefine"))
            except:
                flash("insertCostDefineError")
                return redirect(url_for("costDefine"))
                
            
    
    return render_template('costDefine.html',
                           userInfo = user,
                           costExtendList = costExtendList
                           )

#### costLists
@app.route("/dashboard/costLists" , methods = ["POST" , "GET"])
@login_required
def costLists():
    user = User.query.filter_by(id = session["user_id"]).first()
    costDefineList = CostDefine.query.join(CostExtend , CostExtend.id == CostDefine.costExtend_id).join(CostCenter , CostCenter.id ==  CostExtend.costCenter_id).filter(CostCenter.user_id==session["user_id"]).all()
    
    if request.method == "POST":
        if "deleteCostDefine" in request.form:
            costDefine_id = request.form.get("costDefine_id")
            deleteCostDefine = CostDefine.query.filter_by(id = costDefine_id).first()
            DB.session.delete(deleteCostDefine)
            DB.session.commit()
            return redirect(url_for("costLists"))
    
    return render_template('costLists.html',
                           userInfo = user,
                           costDefineList = costDefineList
                           )

#### costReports
@app.route("/dashboard/costReports")
@login_required
def costReports():
    user = User.query.filter_by(id = session["user_id"]).first()
    return render_template('costReports.html', userInfo = user)

#### exit
@app.route("/exit")
def exit():
    session.clear()
    return redirect(url_for('index'))

#### register
@app.route("/register" , methods=["GET","POST"])
def register():
    if request.method == "POST":
        fname = request.form["fname"]
        lname = request.form["lname"]
        username = request.form["username"]
        
        password = request.form["password"]
        hashedPass = Argon.hash(password)
        
        description = request.form["description"]
        
        try:
            new_user = User(username=username,
                            password=hashedPass,
                            fname=fname,
                            lname=lname,
                            description=description)
            DB.session.add(new_user)
            DB.session.commit()
            
            return render_template("/register.html" , notif = "success")
        except:
            return render_template("/register.html" , notif = "error")
        
    return render_template('/register.html')

#### index
@app.route("/" , methods=["GET","POST"])
def index():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
    
        user = User.query.filter_by(username = username).first()
        
        if user:
            try:
                Argon.verify(user.password, password)
                session["user_id"] = user.id
                session["username"] = user.username
                return redirect(url_for("dashboard"))
            except VerifyMismatchError:
                return render_template("index.html", notif="error")
        else:
             return render_template("index.html", notif="error")
         
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
    