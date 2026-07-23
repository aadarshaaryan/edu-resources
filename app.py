import os
from functools import wraps
from flask import Flask, render_template, request, flash, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from models import db, User, Profile, Subject, Resource, GradeLevel, TierType

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Basic App Configurations
app.secret_key = os.getenv("SECRET_KEY", "edu_resources_secret_key_2026")

# Database URI (Supabase PostgreSQL via .env)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure Cloudinary SDK
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

# Initialize Extensions
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.")
            return redirect(url_for("login"))
        user = db.session.get(User, session["user_id"])
        if not user or not user.is_admin:
            flash("Access denied. Admin privileges required.")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def home():
    return render_template('index.html')


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")
        name = request.form.get("name", "")

        if not username or not password or len(password) < 6:
            flash("Invalid input or password under 6 characters.")
            return redirect(url_for("signup"))

        if User.query.filter_by(username=username).first():
            flash("Username already exists.")
            return redirect(url_for("signup"))

        user = User(username=username, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()

        profile = Profile(user_id=user.id, name=name)
        db.session.add(profile)
        db.session.commit()

        flash("Signup successful! Please log in.")
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session["user_id"] = user.id
            session["username"] = user.username
            session["is_admin"] = user.is_admin
            flash(f"Welcome back, {user.username}!")
            return redirect(url_for("admin_dashboard" if user.is_admin else "dashboard"))

        flash("Invalid credentials.")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user_id" not in session:
        flash("Please log in first.")
        return redirect(url_for("login"))

    user = db.session.get(User, session["user_id"])
    profile = user.profile or Profile(user_id=user.id)

    if request.method == "POST":
        profile.name = request.form.get("name")
        profile.class_val = request.form.get("class")
        profile.board = request.form.get("board")
        profile.state = request.form.get("state")
        profile.gmail = request.form.get("gmail")
        profile.avatar_path = request.form.get("avatar_path")

        db.session.add(profile)
        db.session.commit()
        flash("Profile updated successfully ✅")

    return render_template("dashboard.html", user=user, profile=profile)


# --- ADMIN PANEL ROUTES ---
@app.route("/admin", methods=["GET", "POST"])
@admin_required
def admin_dashboard():
    if request.method == "POST":
        action = request.form.get("action")

        if action == "add_subject":
            name = request.form.get("subject_name")
            grade = request.form.get("grade")
            if name and grade:
                subject = Subject(name=name, grade=GradeLevel(grade))
                db.session.add(subject)
                db.session.commit()
                flash("Subject added successfully!")

        elif action == "upload_resource":
            title = request.form.get("title")
            subject_id = request.form.get("subject_id")
            tier = request.form.get("tier", "free")
            file = request.files.get("file")

            if file and file.filename.lower().endswith('.pdf') and title and subject_id:
                try:
                    upload_result = cloudinary.uploader.upload(
                        file,
                        resource_type="image",
                        format="pdf",
                        folder="edu_resources_pdfs"
                    )
                    
                    cloudinary_url = upload_result.get("secure_url")

                    resource = Resource(
                        title=title,
                        file_path=cloudinary_url,
                        tier=TierType(tier),
                        subject_id=int(subject_id)
                    )
                    db.session.add(resource)
                    db.session.commit()
                    flash("PDF uploaded successfully! 🚀")
                except Exception as e:
                    flash(f"Cloudinary upload failed: {str(e)}")
            else:
                flash("Invalid file format. Please upload a valid PDF.")

    subjects = Subject.query.order_by(Subject.grade).all()
    resources = Resource.query.all()
    return render_template(
        "admin.html", 
        subjects=subjects, 
        resources=resources, 
        grades=GradeLevel, 
        tiers=TierType
    )


# --- CLASS RESOURCE DISPLAY ROUTES ---
@app.route("/ninth")
def ninth():
    subjects = Subject.query.filter_by(grade=GradeLevel.NINTH).all()
    return render_template("ninth.html", subjects=subjects)


@app.route("/tenth")
def tenth():
    subjects = Subject.query.filter_by(grade=GradeLevel.TENTH).all()
    return render_template("tenth.html", subjects=subjects)


@app.route("/twelth")
def twelth():
    subjects = Subject.query.filter_by(grade=GradeLevel.TWELFTH).all()
    return render_template("twelth.html", subjects=subjects)


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for("login"))


@app.route('/subject/<int:subject_id>/resources')
def view_resources(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    resources = Resource.query.filter_by(subject_id=subject.id).all()
    
    # Check if the currently logged-in user is an admin
    is_admin = False
    if "user_id" in session:
        user = db.session.get(User, session["user_id"])
        if user and user.is_admin:
            is_admin = True
            
    return render_template('resources.html', subject=subject, resources=resources, is_admin=is_admin)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)