from flask import Flask, redirect, url_for, render_template, request, session
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
        return redirect(url_for("welcome"))
    else:
        if "user" in session:
            return redirect(url_for("welcome"))
        return render_template("login.html")


@app.route("/user")
def welcome():
    if "user" in session:
        user = session["user"]
        return render_template("welcome.html", username=user)
    else:
        return redirect(url_for("login"))


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)

