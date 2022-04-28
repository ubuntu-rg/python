from flask import Flask, redirect, url_for, render_template, request, session, flash, abort
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import logging

app = Flask("__name__")
# Initiate the session secret key and lifetime of the session
app.secret_key = "ea4a6213-0ddf-4b17-9996-09e731b2b162"
app.permanent_session_lifetime = timedelta(minutes=45)

# Initiate the logger and create a file to save all the logs within it
logging.basicConfig(filename='Logfile.log', level=logging.DEBUG)

# Define the DataBase
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Users(db.Model):
    # Create the DB TABLE
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(50))
    email = db.Column("email", db.String(50))
    password = db.Column("password", db.String(256))

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password


def check_if_admin(user_session):
    if "user" in user_session:
        if not user_session['user'] == "admin":
            abort(401)
    if len(user_session) == 0:
        abort(401)


@app.route("/home")
@app.route("/")
def homepage():
    # Returns the homepage according to the status of the user
    if "user" in session:
        return render_template("base.html", username=session["user"])
    else:
        return render_template("base.html")


# View the DB data - Should be removed later!
@app.route("/admin/view")
def view():
    app.logger.critical("Someone just viewed the /view URI with the DB data!")
    check_if_admin(session)
    return render_template("view.html", values=Users.query.all())


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["name"]
        password = request.form["password"]
        password = generate_password_hash(password)
        app.logger.info(f"New user was registered to the system: {username}")
        # Add a new user to the DB
        # Creating new Users object with the username, email, password attributes
        usr = Users(username, "", password)
        db.session.add(usr)

        found_user = Users.query.filter_by(name=username).first()
        found_user.password = password
        db.session.commit()


        session["user"] = username
        session["password"] = password
        flash(f"Hello {username}! you have registered successfully!", "info")
        return render_template("register.html")
    else:
        if "user" in session:
            flash("You are already logged in", "info")
            return redirect(url_for("userprofile"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # Check if the user is trying to login
    if request.method == "POST":
        # Create the session for the user
        session.permanent = True
        username = request.form["username"]
        password = request.form["password"]
        session["user"] = username
        session["password"] = password

        # Check if the user is in the DB and if the password is correct
        found_user = Users.query.filter_by(name=username).first()
        if Users.query.filter_by(name=username).first() and check_password_hash(found_user.password, password):
            session["email"] = found_user.email
            app.logger.info(f"The user '{username}' was logged in to the system.")
        else:
            app.logger.warning(f"Someone tried to log in to the system with the username: {username}")
            flash("User name or password is incorrect", "info")
            return render_template("login.html")

        flash(f"Welcome, {username}!")
        return redirect(url_for("userprofile"))
    else:
        # If the user is already logged in and trying to reach the login page, redirect the user to the profile page
        if "user" in session:
            flash(f"You are already logged in!")
            return redirect(url_for("userprofile"))
        return render_template("login.html")


@app.route("/userprofile", methods=["GET", "POST"])
@app.route("/user", methods=["GET", "POST"])
def userprofile():
    email = None
    # Check if the user is logged in
    if "user" in session:
        username = session["user"]
        # Check if the user is updating his data
        if request.method == "POST":
            email = request.form["email"]
            # Check that the email text is greater than 0
            if len(email) > 0:
                session["email"] = email
                # If user changes his email, save it in the DB
                found_user = Users.query.filter_by(name=username).first()
                found_user.email = email
                db.session.commit()
                flash(f"Your data has been updated to: {email}", "info")
                app.logger.info(f"The user {username} has changed his email to: {email}")
            else:
                flash("Please fill your email in the form below.", "warning")
        else:
            # Show the userprofile with the user data
            if "email" in session:
                email = session["email"]
        return render_template("welcome.html", username=username, email=email)
    else:
        # If the user is not logged in and trying to reach this page, redirect the user to the login page
        flash("You are not logged in, please enter your credentials")
        return redirect(url_for("login"))


@app.route("/user/admin", methods=['GET', 'POST'])
def admin_panel():
    # Show unauthorized message for users who not admins
    check_if_admin(session)
    # Delete user from the DB - admin option
    if request.method == "POST":
        selected_users = [request.form.getlist(str(i)) for i in range(len(Users.query.all()))]
        for name in selected_users:
            if name:
                Users.query.filter_by(name=name[0]).delete()
                db.session.commit()
                flash(f"The user {name[0]} was deleted from the DB", "warning")
                app.logger.warning(f"The user {name} was deleted from the server.")
        # if user_to_delete == None:
        #     flash("Choose a user from the list.")
        # else:

    return render_template("admin.html", values=Users.query.all())


@app.route("/admin/logs")
def logs():
    check_if_admin(session)
    logfile = open("Logfile.log", "r").read()
    return render_template("logs.html", logfile=logfile)


@app.route("/logout")
def logout():
    # Check if the user is logged in
    if "user" in session:
        user = session["user"]
        flash(f"{user}, You have been logged out!", "info")
        app.logger.info(f"The user {user} has logged out of the system")
    # Clear the user session data and redirect to the login page after a successful logout
    session.pop("user", None)
    session.pop("email", None)
    session.pop("password", None)
    session.clear()
    return redirect(url_for("login"))


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


if __name__ == "__main__":
    # Initiate the DB class
    db.create_all()
    # Initiate the webserver
    app.run(host="0.0.0.0", port=8080, debug=True)

