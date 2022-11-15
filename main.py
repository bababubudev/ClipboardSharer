from flask import Flask, render_template, redirect, url_for, request, session, flash
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "daidonprabeshdada"
app.permanent_session_lifetime = timedelta(days=1)


def user_in(current_session: dict()) -> bool:
    if "user" in current_session:
        return True
    else:
        return False


@app.route('/', methods=["POST", "GET"])
def index():
    if request.method == "POST":
        session.permanent = True
        if user_in(session):
            logout()

        user = request.form["title"]
        session["user"] = user

        return redirect(url_for("inbox"))
    else:
        if user_in(session):
            user = session["user"]
            return render_template('base.html', user_valid=user)
        else:
            return render_template('base.html')


@app.route('/user')
def inbox():
    if user_in(session):
        user = session["user"]
        return render_template('customarea.html', username=user)
    else:
        return redirect(url_for("index"))


@app.route('/logout')
def logout():
    user = session["user"].capitalize()
    session.pop("user", None)
    flash(f"{user} was replaced from the session!", "info")

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
