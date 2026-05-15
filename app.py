from flask import Flask, render_template, request, redirect, session
from db import Base, engine, SessionLocal
from ai import analyze_resume   # Make sure this function exists
import models
import PyPDF2
import docx
import json

app = Flask(__name__)
app.secret_key = "secret123"   # Fixed typo: scret_key -> secret_key

# Create tables
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

        # Fixed: added .first()
        existing_user = db.query(models.User).filter_by(email=email).first()

        if existing_user:
            db.close()
            return "User already exists"

        user = models.User(email=email, password=password)
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

        # Fixed query and added .first()
        user = db.query(models.User).filter_by(
            email=email,
            password=password
        ).first()

        if user:
            # Fixed session syntax
            session["user"] = user.email
            db.close()
            return redirect("/dashboard")
        else:
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

        # ---------- FILE HANDLING ----------
        if file and file.filename != "":
            # PDF
            if file.filename.endswith(".pdf"):
                try:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""

                    for page in pdf_reader.pages:
                        text += page.extract_text() or ""

                    resume_text = text

                except Exception as e:
                    result = {"error": f"PDF error: {str(e)}"}

            # DOCX
            elif file.filename.endswith(".docx"):
                try:
                    doc = docx.Document(file)
                    text = ""

                    for para in doc.paragraphs:
                        text += para.text + "\n"

                    resume_text = text

                except Exception as e:
                    result = {"error": f"DOCX error: {str(e)}"}

        # ---------- ANALYZE RESUME ----------
        if resume_text and user_goal and result is None:
            try:
                result = analyze_resume(resume_text, user_goal)

                # Save to database
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
                result = {"error": f"AI error: {str(e)}"}

    return render_template(
        "dashboard.html",   # Fixed typo
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

    # Convert JSON string to dictionary
    parsed_reports = []

    for r in reports:
        try:
            parsed_result = json.loads(r.results)
        except Exception:
            parsed_result = {}

        parsed_reports.append({
            "resume": r.resume_text,
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