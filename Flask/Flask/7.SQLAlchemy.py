from flask import Flask, redirect, url_for, render_template, request, session, flash, abort
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime
from werkzeug.security import generate_password_hash, check_password_hash
import logging
import datetime

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

# List all the users in the system
users = []


class Emails(db.Model):
    # Create the forum DB TABLE
    _id = db.Column("email_id", db.Integer, primary_key=True)
    sent_date = db.Column("post_date", DateTime, default=datetime.datetime.utcnow)
    sender = db.Column("sender", db.String(50))
    receiver = db.Column("receiver", db.String(50))
    subject = db.Column("subject", db.String(256))
    data = db.Column("data", db.String(2048))
    unread_mail = db.Column("unread_mail", db.Boolean)
    deleted = db.Column("deleted", db.Boolean, default=False)
    starred = db.Column("starred", db.Boolean, default=False)
    # This parameter should set if the mail is incoming or outgoing
    income_mail = db.Column("income_mail", db.Boolean, default=True)

    def __init__(self, sender, receiver, subject, data, unread_mail):
        self.sender = sender
        self.receiver = receiver
        self.subject = subject
        self.data = data
        self.unread_mail = unread_mail


class Forum(db.Model):
    # Create the forum DB TABLE
    _id = db.Column("post_id", db.Integer, primary_key=True)
    post_date = db.Column("post_date", DateTime, default=datetime.datetime.utcnow)
    username = db.Column("username", db.String(50))
    subject = db.Column("subject", db.String(256))
    data = db.Column("data", db.String(2048))
    likes = db.Column("likes", db.Integer)

    def __init__(self, username, subject, data):
        self.username = username
        self.subject = subject
        self.data = data
        self.likes = 0


class Replies(db.Model):
    # Create the forum DB TABLE
    _id = db.Column("post_id", db.Integer, primary_key=True)
    post_related_id = db.Column("post_related_id", db.Integer)
    post_date = db.Column("post_date", DateTime, default=datetime.datetime.utcnow)
    username = db.Column("username", db.String(50))
    data = db.Column("data", db.String(2048))

    def __init__(self, post_related_id, username, data):
        self.post_related_id = post_related_id
        self.username = username
        self.data = data


class Users(db.Model):
    user_likes = {}
    # Create the DB TABLE
    _id = db.Column("id", db.Integer, primary_key=True)
    created_date = db.Column("created_date", DateTime, default=datetime.date.today())
    name = db.Column("name", db.String(50))
    email = db.Column("email", db.String(50))
    password = db.Column("password", db.String(256))
    # User Profile Data
    fullname = db.Column("fullname", db.String(50))
    phonenumber = db.Column("phonenumber", db.Integer)
    address = db.Column("address", db.String(50))
    country = db.Column("country", db.String(50))
    post_counter = db.Column("post_counter", db.Integer)
    replies_counter = db.Column("replies_counter", db.Integer)
    amount_user_likes = db.Column("amount_user_likes", db.Integer)
    unread_mails = db.Column("unread_mails", db.Integer)

    def __init__(self, name, email, password, fullname, phonenumber, address, country, amount_user_likes):
        self.name = name
        self.name = name
        self.email = email
        self.password = password
        self.fullname = fullname
        self.phonenumber = phonenumber
        self.address = address
        self.country = country
        self.post_counter = 0
        self.replies_counter = 0
        self.amount_user_likes = amount_user_likes
        self.unread_mails = 0


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


# View the Users DB data - Should be removed later!
@app.route("/admin/view")
def view():
    app.logger.critical("Someone just viewed the /view URI with the DB data!")
    check_if_admin(session)
    unread = Users.query.filter_by(name="admin").first().unread_mails
    return render_template("view.html", values=Users.query.all(), unread=unread)


# View the Forum DB data - Should be removed later!
@app.route("/admin/view-forum")
def view_forum():
    app.logger.critical("Someone just viewed the /view-forum URI with the DB data!")
    check_if_admin(session)
    unread = Users.query.filter_by(name="admin").first().unread_mails
    return render_template("view-forum.html", values=Forum.query.all(), unread=unread)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["name"]
        password = request.form["password"]
        password = generate_password_hash(password)
        # Add a new user to the DB if the username does not exist
        if username in users:
            flash(f"The name '{username}' is already used by someone", "info")
        else:
            app.logger.info(f"New user was registered to the system: {username}")
            users.append(username)
            usr = Users(username, "", password, "", 0, "", "", 0)
            db.session.add(usr)

            found_user = Users.query.filter_by(name=username).first()
            found_user.password = password
            db.session.commit()

            session["user"] = username
            session["password"] = password
            flash(f"Hello {username}! you have registered successfully!", "info")
            return redirect("userprofile")
        return render_template("register.html")
    else:
        if "user" in session:
            flash("You are already logged in", "info")
            return redirect(url_for("userprofile"))
    return render_template("register.html")


@app.route("/forum", methods=["GET", "POST"])
def forum():
    if request.method == "POST":
        try:
            form_name = request.form['likes']
            username = session["user"]
            if "likes" in form_name:
                post_id = form_name.split("-")[1]
                found_post = Forum.query.filter_by(_id=post_id).first()
                found_user = Users.query.filter_by(name=username).first()
                try:
                    if Users.user_likes[found_post._id]:
                        found_post.likes -= 1
                        found_user.amount_user_likes -= 1
                        Users.user_likes[found_post._id] = False
                    else:
                        found_post.likes += 1
                        found_user.amount_user_likes += 1
                        Users.user_likes[found_post._id] = True
                except KeyError:
                    """ This exception will occur once the user did not liked the post and there is a key error 
                    in the dictionary."""
                    found_post.likes += 1
                    found_user.amount_user_likes += 1
                    Users.user_likes[found_post._id] = True
                db.session.commit()
                return render_template("forum.html", values=Forum.query.all(), replies=Replies.query.all())
        except KeyError:
            pass
    # Create a new reply for the selected post
    if request.method == "POST":
        reply_message = request.form["reply"]
        post_related_id = request.form["postid"]
        if "user" in session:
            username = session['user']
        else:
            username = None
        app.logger.info(f"New reply to post {post_related_id} was published: {reply_message}")

        reply = Replies(post_related_id, username, reply_message)
        # Add one reply to the replies_counter
        found_user = Users.query.filter_by(name=username).first()
        found_user.replies_counter += 1
        db.session.add(reply)
        db.session.commit()
        # Add a like

    return render_template("forum.html", values=Forum.query.all(), replies=Replies.query.all())


@app.route("/forum/new-post", methods=["GET", "POST"])
def new_post():
    # Create a new post
    if request.method == "POST":
        username = session["user"]
        subject = request.form["subject"]
        data = request.form["data"]
        found_user = Users.query.filter_by(name=username).first()
        found_user.post_counter += 1
        app.logger.info(f"New post was published: {subject}")

        # Add new post to the DB
        post = Forum(username, subject, data)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for("forum"))
    if "user" in session:
        return render_template("new-post.html", username=session["user"])
    else:
        return render_template("new-post.html", username="Please Login in order to write a post")


@app.route("/login", methods=["GET", "POST"])
def login():
    # Check if the user is trying to log in
    if request.method == "POST":
        # Create the session for the user
        session.permanent = True
        username = request.form["username"]
        password = request.form["password"]

        # Check if the user is in the DB and if the password is correct
        found_user = Users.query.filter_by(name=username).first()
        if Users.query.filter_by(name=username).first() and check_password_hash(found_user.password, password):
            session["user"] = username
            session["password"] = password
            session["email"] = found_user.email
            session["fullname"] = found_user.fullname
            session["address"] = found_user.address
            session["phonenumber"] = found_user.phonenumber
            session["country"] = found_user.country
            session["post_counter"] = found_user.post_counter
            session["replies_counter"] = found_user.replies_counter
            session["amount_user_likes"] = found_user.amount_user_likes

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
    phone_number = None
    if "user" in session:
        username = session["user"]
        if "email" in session:
            email = session["email"]
        if "phonenumber" in session:
            phone_number = session["phonenumber"]
        unread = Users.query.filter_by(name=username).first().unread_mails
        return render_template("user.html", username=username, email=email, phonenumber=phone_number, unread=unread)
    else:
        # If the user is not logged in and trying to reach this page, redirect the user to the login page
        flash("You are not logged in, please enter your credentials")
        return redirect(url_for("login"))


@app.route("/user/user-security", methods=["GET", "POST"])
def user_security():
    current_email = None
    current_fullname = None
    current_country = None
    current_address = None
    current_phonenumber = None
    to_flash = False
    # Check if the user is logged in
    if "user" in session:
        username = session["user"]
        # Check if the user is updating his data
        if request.method == "POST":
            email = request.form["email"]
            fullname = request.form["full-name"]
            phone_number = request.form["phone-number"]
            address = request.form["address"]
            country = request.form["country"]
            old_password = request.form["old-password"]
            new_password = request.form["new-password"]
            # Get the user session
            found_user = Users.query.filter_by(name=username).first()
            # Check that the email text is greater than 0
            if len(email) > 5:
                session["email"] = email
                # If user changes his email, save it in the DB
                found_user.email = email
                db.session.commit()
                to_flash = True
                app.logger.info(f"The user {username} has changed his email to: {email}")
            if len(fullname) >= 0:
                session["fullname"] = fullname
                found_user.fullname = fullname
                db.session.commit()
            if len(country) >= 0:
                session["country"] = country
                found_user.country = country
                db.session.commit()
            if len(address) >= 0:
                session["address"] = address
                found_user.address = address
                db.session.commit()
            if 7 <= len(phone_number) <= 13 or len(phone_number) == 0:
                session["phonenumber"] = phone_number
                found_user.phonenumber = phone_number
                db.session.commit()
                to_flash = True
            else:
                flash("Please type a correct phone number.")
                phone_number = None
                to_flash = False

            # Change Password
            if len(old_password) > 0:
                found_user = Users.query.filter_by(name=username).first()
                if check_password_hash(found_user.password, old_password):
                    if len(new_password) < 8:
                        flash(f"Please enter password with length of 8 chars", "alert")
                        to_flash = False
                    else:
                        session['password'] = generate_password_hash(new_password)
                        found_user.password = generate_password_hash(new_password)
                        db.session.commit()
                else:
                    flash(f"The password is incorrect", "warning")
                    to_flash = False
            if to_flash:
                flash(f"Your data has been updated!", "info")
            unread = Users.query.filter_by(name=username).first().unread_mails
            return render_template("user-security.html", username=username, email=email, fullname=fullname,
                                   phone_number=phone_number, address=address, country=country, unread=unread)
        else:
            # Show the userprofile with the user data
            if "email" in session:
                current_email = session["email"]
            if "fullname" in session:
                current_fullname = session["fullname"]
            if "country" in session:
                current_country = session["country"]
            if "address" in session:
                current_address = session["address"]
            if "phonenumber" in session:
                current_phonenumber = session["phonenumber"]
    else:
        # If the user is not logged in and trying to reach this page, redirect the user to the login page
        flash("You are not logged in, please enter your credentials")
        return redirect(url_for("login"))
    unread = Users.query.filter_by(name=username).first().unread_mails
    return render_template("user-security.html", username=username, email=current_email, fullname=current_fullname,
                           address=current_address, country=current_country, phone_number=current_phonenumber,
                           unread=unread)


@app.route("/user/user-statistics")
def statistics():
    if "user" in session:
        username = session["user"]
        unread = Users.query.filter_by(name=username).first().unread_mails
    else:
        flash("You are not logged in, please enter your credentials")
        return redirect(url_for("login"))
    return render_template("user-statistics.html", username=username, accounts=Users.query.all(),
                           posts=Forum.query.all(), unread=unread)


@app.route("/user/user-inbox", methods=["GET", "POST"])
def inbox():
    email = None
    if "email" in session:
        email = session["email"]
    if "user" in session:
        username = session["user"]
        unread = Users.query.filter_by(name=username).first().unread_mails
        return render_template("user-inbox.html", username=username, email=email, emails=Emails.query.all(),
                               unread=unread)
    else:
        flash("Please login to your account", "warning")
        return redirect("../login")


@app.route("/user/user-inbox/<int:path>", methods=["GET", "POST"])
def read_mail(path):
    email = None
    if "email" in session:
        email = session["email"]
    if "user" in session:
        username = session["user"]
        email_id = request.url.split("/")[5]
        find_email = Emails.query.filter_by(_id=email_id).first()
        find_user = Users.query.filter_by(name=find_email.receiver).first()
        if find_email.unread_mail:
            find_user.unread_mails -= 1
        find_email.unread_mail = False

        db.session.commit()
        unread = Users.query.filter_by(name=username).first().unread_mails
        return render_template("email-data.html", username=username, email=email, emails=Emails.query.all(),
                               found_email=find_email, user=find_user, unread=unread)
    else:
        flash("Please login to your account", "warning")
        return redirect("../../../login")


@app.route("/user/user-inbox/compose", methods=["GET", "POST"])
def compose():
    if "email" in session:
        email = session["email"]
    if "user" in session:
        username = session["user"]
        if request.method == "POST":
            to = request.form.get("to")
            subject = request.form["subject"]
            body = request.form["body"]

            found_user = Users.query.filter_by(name=to).first()
            found_user.unread_mails += 1

            new_mail = Emails(username, to, subject, body, True)
            db.session.add(new_mail)
            db.session.commit()

            return redirect("../user-inbox")
        unread = Users.query.filter_by(name=username).first().unread_mails
        return render_template("compose-mail.html", username=username, email=email, users=Users.query.all(),
                               emails=Emails.query.all(), unread=unread)
    else:
        flash("Please login to your account", "warning")
        return redirect("../../login")


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
    unread = Users.query.filter_by(name="admin").first().unread_mails
    return render_template("admin.html", values=Users.query.all(), unread=unread)


@app.route("/admin/logs")
def logs():
    check_if_admin(session)
    logfile = open("Logfile.log", "r").read()
    unread = Users.query.filter_by(name="admin").first().unread_mails
    return render_template("logs.html", logfile=logfile, unread=unread)


@app.route("/admin/manage-forum", methods=["GET", "POST"])
def manage_forum():
    # Check if the admin account is logged in
    check_if_admin(session)
    # Delete a post from the DB including its replies
    if request.method == "POST":
        # Get all posts
        selected_posts = [request.form.getlist(str(i)) for i in range(len(Forum.query.all()))]
        for post in selected_posts:
            # Check if any post was selected by the checkbox
            if post:
                # Delete the post and its replies
                Forum.query.filter_by(_id=post[0]).delete()
                Replies.query.filter_by(post_related_id=post[0]).delete()
                db.session.commit()
                flash(f"The post id: {post[0]} was deleted from the DB", "warning")
                app.logger.warning(f"The post {post} was deleted from the server.")
    unread = Users.query.filter_by(name="admin").first().unread_mails
    return render_template("manage-forum.html", posts=Forum.query.all(), unread=unread)


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
    session.pop("address", None)
    session.pop("fullname", None)
    session.pop("country", None)
    session.pop("phonenumber", None)
    session.pop("amount_user_likes", None)
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
