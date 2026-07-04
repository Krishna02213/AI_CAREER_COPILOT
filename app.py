from flask import Flask, render_template, request, redirect, session
from db import Base, engine, SessionLocal
from ai import analyze_resume
import models
import PyPDF2
import docx
import json
import os

app = Flask(__name__)

# Secret key from environment variable
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")

# Create database tables
Base.metadata.create_all(bind=engine)


# ---------------- HOME ----------------
@app.route("/")
def home():
    if "user" in session:
        return redirect("/dashboard")
    return redirect("/login")


# ---------------- SIGNUP ----------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    db = SessionLocal()

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        existing_user = db.query(models.User).filter_by(email=email).first()

        if existing_user:
            db.close()
            return "User already exists"

        user = models.User(
            email=email,
            password=password
        )

        db.add(user)
        db.commit()
        db.close()

        return redirect("/login")

    db.close()
    return render_template("signup.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    db = SessionLocal()

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = db.query(models.User).filter_by(
            email=email,
            password=password
        ).first()

        if user:
            session["user"] = user.email
            db.close()
            return redirect("/dashboard")

        db.close()
        return "Invalid credentials"

    db.close()
    return render_template("login.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect("/login")

    result = None

    if request.method == "POST":
        user_goal = request.form.get("role")
        resume_text = request.form.get("resume")
        file = request.files.get("file")

        # -------- PDF Upload --------
        if file and file.filename:

            if file.filename.lower().endswith(".pdf"):
                try:
                    reader = PyPDF2.PdfReader(file)
                    text = ""

                    for page in reader.pages:
                        text += page.extract_text() or ""

                    resume_text = text

                except Exception as e:
                    result = {"error": f"PDF Error: {e}"}

            # -------- DOCX Upload --------
            elif file.filename.lower().endswith(".docx"):
                try:
                    document = docx.Document(file)
                    text = ""

                    for para in document.paragraphs:
                        text += para.text + "\n"

                    resume_text = text

                except Exception as e:
                    result = {"error": f"DOCX Error: {e}"}

        # -------- AI Analysis --------
        if resume_text and user_goal and result is None:
            try:
                result = analyze_resume(
                    resume_text,
                    user_goal
                )

                db = SessionLocal()

                user = db.query(models.User).filter_by(
                    email=session["user"]
                ).first()

                report = models.Report(
                    user_id=user.id,
                    resume_text=resume_text,
                    results=json.dumps(result)
                )

                db.add(report)
                db.commit()
                db.close()

            except Exception as e:
                result = {"error": f"AI Error: {e}"}

    return render_template(
        "dashboard.html",
        user=session["user"],
        result=result
    )


# ---------------- HISTORY ----------------
@app.route("/history")
def history():
    if "user" not in session:
        return redirect("/login")

    db = SessionLocal()

    user = db.query(models.User).filter_by(
        email=session["user"]
    ).first()

    reports = db.query(models.Report).filter_by(
        user_id=user.id
    ).all()

    parsed_reports = []

    for report in reports:
        try:
            parsed_result = json.loads(report.results)
        except Exception:
            parsed_result = {}

        parsed_reports.append({
            "resume": report.resume_text,
            "result": parsed_result
        })

    db.close()

    return render_template(
        "history.html",
        reports=parsed_reports
    )


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)