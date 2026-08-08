import os
import uuid
from functools import wraps
from flask import Flask, render_template, request, flash, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from models import db, User, Profile, Subject, Resource, GradeLevel, TierType, Feedback
from sqlalchemy import func

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Basic App Configurations
app.secret_key = os.getenv("SECRET_KEY", "edu_resources_secret_key_2026")

# Database URI (Supabase PostgreSQL via .env)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Enable pre-pinging to handle idle pooler disconnects gracefully
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,  # Recycle connections every 5 minutes
}

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
        if not current_user.is_authenticated:
            flash("Please log in first.")
            return redirect(url_for("login"))
        if not current_user.is_admin:
            flash("Access denied. Admin privileges required.")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/', methods=["GET", "POST"])
def home():
    if request.method == "POST":
        rating = request.form.get("rating", type=int)
        comment = request.form.get("comment", "").strip()

        if not rating or not (1 <= rating <= 5):
            flash("Please select a star rating between 1 and 5.")
            return redirect(url_for("home"))

        if not comment:
            flash("Please enter feedback comments.")
            return redirect(url_for("home"))

        user_id = current_user.id if current_user.is_authenticated else None
        feedback = Feedback(user_id=user_id, rating=rating, comment=comment)
        db.session.add(feedback)
        db.session.commit()

        flash("Thank you for your feedback! ⭐")
        return redirect(url_for("home"))

    feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).all()
    avg_rating = db.session.query(func.avg(Feedback.rating)).scalar() or 0.0
    
    return render_template('index.html', feedbacks=feedbacks, avg_rating=round(avg_rating, 1))


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
            login_user(user)  # Flask-Login handles session state automatically
            flash(f"Welcome back, {user.username}!")
            return redirect(url_for("admin_dashboard" if user.is_admin else "dashboard"))

        flash("Invalid credentials.")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    user = current_user
    profile = user.profile

    if not profile:
        profile = Profile(user_id=user.id)
        db.session.add(profile)
        db.session.commit()

    if request.method == "POST":
        profile.name = request.form.get("name")
        profile.class_val = request.form.get("class")
        profile.board = request.form.get("board")
        profile.state = request.form.get("state")
        profile.avatar_path = request.form.get("avatar_path")

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
                try:
                    subject = Subject(name=name, grade=GradeLevel(grade))
                    db.session.add(subject)
                    db.session.commit()
                    flash("Subject added successfully!")
                except ValueError:
                    flash("Invalid grade level selected.")

        elif action == "upload_resource":
            title = request.form.get("title")
            subject_id = request.form.get("subject_id")
            file = request.files.get("file")

            if file and file.filename.lower().endswith('.pdf') and title and subject_id:
                try:
                    unique_filename = f"{uuid.uuid4().hex}.pdf"
                    upload_result = cloudinary.uploader.upload(
                        file,
                        resource_type="raw",
                        folder="edu_resources_pdfs/free",
                        public_id=unique_filename
                    )

                    cloudinary_url = upload_result.get("secure_url")

                    resource = Resource(
                        title=title,
                        file_path=cloudinary_url,
                        subject_id=int(subject_id),
                        tier=TierType.FREE
                    )
                    db.session.add(resource)
                    db.session.commit()
                    flash("Free PDF uploaded successfully! 🚀")
                except Exception as e:
                    flash(f"Cloudinary upload failed: {str(e)}")
            else:
                flash("Invalid file format. Please upload a valid PDF.")

        elif action == "upload_premium_resource":
            title = request.form.get("title")
            subject_id = request.form.get("subject_id")
            file = request.files.get("file")

            if file and file.filename.lower().endswith('.pdf') and title and subject_id:
                try:
                    unique_filename = f"premium_{uuid.uuid4().hex}.pdf"
                    upload_result = cloudinary.uploader.upload(
                        file,
                        resource_type="raw",
                        folder="edu_resources_pdfs/premium",
                        public_id=unique_filename
                    )

                    cloudinary_url = upload_result.get("secure_url")

                    resource = Resource(
                        title=title,
                        file_path=cloudinary_url,
                        subject_id=int(subject_id),
                        tier=TierType.PREMIUM
                    )
                    db.session.add(resource)
                    db.session.commit()
                    flash("Premium PDF uploaded successfully! 👑")
                except Exception as e:
                    flash(f"Cloudinary upload failed: {str(e)}")
            else:
                flash("Invalid file format. Please upload a valid PDF.")

    subjects = Subject.query.order_by(Subject.grade).all()
    resources = Resource.query.all()
    
    # Fetch feedback data for admin panel
    feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).all()
    avg_rating = db.session.query(func.avg(Feedback.rating)).scalar() or 0.0
    total_reviews = len(feedbacks)

    return render_template(
        "admin.html", 
        subjects=subjects, 
        resources=resources, 
        grades=GradeLevel,
        feedbacks=feedbacks,
        avg_rating=round(avg_rating, 1),
        total_reviews=total_reviews
    )


# --- PREMIUM VAULT DISPLAY ROUTE ---
@app.route("/premium")
def premium():
    premium_resources = Resource.query.filter_by(tier=TierType.PREMIUM).all()
    return render_template("premium.html", resources=premium_resources)


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
    logout_user()
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for("login"))


@app.route('/subject/<int:subject_id>/resources')
def view_resources(subject_id):
    subject = db.get_or_404(Subject, subject_id)
    resources = Resource.query.filter_by(subject_id=subject.id).all()
    
    is_admin = current_user.is_authenticated and current_user.is_admin
            
    return render_template('resources.html', subject=subject, resources=resources, is_admin=is_admin)


@app.route("/admin/delete_resource/<int:resource_id>", methods=["POST"])
@admin_required
def delete_resource(resource_id):
    resource = db.get_or_404(Resource, resource_id)

    try:
        if "cloudinary.com" in resource.file_path:
            url_parts = resource.file_path.split("/")
            folder_and_file = "/".join(url_parts[-2:])
            public_id = folder_and_file.rsplit('.', 1)[0]

            cloudinary.uploader.destroy(public_id, resource_type="raw")
    except Exception as e:
        print(f"Cloudinary deletion log: {e}")

    db.session.delete(resource)
    db.session.commit()

    flash("Resource deleted successfully! 🗑️")
    return redirect(url_for('admin_dashboard'))

@app.route("/support")
def support():
    return render_template("support-helpdesk.html")



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)