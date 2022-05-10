from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta

app = Flask("__name__")
app.secret_key = "ea4a6213-0ddf-4b17-9996-09e731b2b162"
app.permanent_session_lifetime = timedelta(minutes=45)

@app.route("/")
def homepage():
    if "user" in session:
        return render_template("base.html", username=session["user"])
    else:
        return render_template("base.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session.permanent = True
        username = request.form["username"]
        session["user"] = username
        flash(f"Welcome {username}!")
        return redirect(url_for("userprofile"))
    else:
        if "user" in session:
            flash(f"You are already logged in!")
            return redirect(url_for("userprofile"))
        return render_template("login.html")


@app.route("/user")
def userprofile():
    if "user" in session:
        user = session["user"]
        return render_template("user.html", username=user)
    else:
        flash("You are not logged in, please enter your credentials")
        return redirect(url_for("login"))


@app.route("/logout")
def logout():
    if "user" in session:
        user = session["user"]
        flash(f"{user}, You have been logged out!", "info")
    session.pop("user", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)

