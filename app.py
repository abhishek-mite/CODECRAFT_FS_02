from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key'  # change in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employees.db'
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"

# -------------------
# MODELS
# -------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)  # (use hashing in real apps)

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -------------------
# ROUTES
# -------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and user.password == request.form["password"]:
            login_user(user)
            return redirect(url_for("list_employees"))
        flash("Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/")
@login_required
def list_employees():
    employees = Employee.query.all()
    return render_template("list.html", employees=employees)

@app.route("/add", methods=["GET", "POST"])
@login_required
def add_employee():
    if request.method == "POST":
        emp = Employee(
            name=request.form["name"],
            email=request.form["email"],
            role=request.form["role"]
        )
        db.session.add(emp)
        db.session.commit()
        return redirect(url_for("list_employees"))
    return render_template("add.html")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_employee(id):
    emp = Employee.query.get_or_404(id)
    if request.method == "POST":
        emp.name = request.form["name"]
        emp.email = request.form["email"]
        emp.role = request.form["role"]
        db.session.commit()
        return redirect(url_for("list_employees"))
    return render_template("edit.html", emp=emp)

@app.route("/delete/<int:id>")
@login_required
def delete_employee(id):
    emp = Employee.query.get_or_404(id)
    db.session.delete(emp)
    db.session.commit()
    return redirect(url_for("list_employees"))

# -------------------
# MAIN
# -------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        # Create default admin user if not exists
        if not User.query.filter_by(username="admin").first():
            db.session.add(User(username="admin", password="admin"))
            db.session.commit()
    app.run(debug=True)
