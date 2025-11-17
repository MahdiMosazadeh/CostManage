from flask import Flask , render_template , redirect , url_for , request , session
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
    
    id = DB.Column(DB.Integer , primary_key = True)
    username = DB.Column(DB.String(200))
    password = DB.Column(DB.String(200))
    fname = DB.Column(DB.String(200))
    lname = DB.Column(DB.String(200))
    description = DB.Column(DB.String(500))
    

with app.app_context():
    DB.create_all()
    
    
    
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
    return render_template('dashboard.html')

#### costCenters
@app.route("/dashboard/costCenters")
def costCenters():
    return render_template('costCenters.html')

#### costCategory
@app.route("/dashboard/costCategory")
def costCategory():
    return render_template('costCategory.html')

#### costExtend
@app.route("/dashboard/costExtend")
def costExtend():
    return render_template('costExtend.html')

#### costDefine
@app.route("/dashboard/costDefine")
def costDefine():
    return render_template('costDefine.html')

#### costLists
@app.route("/dashboard/costLists")
def costLists():
    return render_template('costLists.html')

#### costReports
@app.route("/dashboard/costReports")
def costReports():
    return render_template('costReports.html')

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
    