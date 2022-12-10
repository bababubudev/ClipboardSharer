from flask import Flask, render_template, redirect, url_for, request, session, flash
from datetime import timedelta, datetime
from flask_sqlalchemy import SQLAlchemy
from dotenv import dotenv_values


app = Flask(__name__)

sutukka = dotenv_values(".env")
app.secret_key = sutukka["secret_key"]
user, password = sutukka["user"], sutukka["password"]
host = sutukka["host"]
db = sutukka["db"]

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username=user, password=password, hostname=host, databasename=db)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///redirects.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.permanent_session_lifetime = timedelta(days=1)

db = SQLAlchemy(app)


class redirects(db.Model):
    _id = db.Column("id", db.INTEGER, primary_key=True)
    linker = db.Column(db.String(30))
    text = db.Column(db.String(320))
    time_created = db.Column(db.DateTime)

    def __init__(self, linker, text, time_created):
        self.linker = linker
        self.text = text
        self.time_created = time_created


def redirect_of(current_session: dict(), key: str) -> bool:
    if key in current_session:
        return True
    else:
        return False


@app.route('/', methods=["POST", "GET"])
def index():
    data_timeout()
    if request.method == "POST":
        session.permanent = True
        link = request.form["title"]
        link = " ".join(link.split())

        if redirect_of(session, "link") and link != session["link"]:
            logout()

        session["link"] = link
        found_user = redirects.query.filter_by(linker=link).first()

        if found_user:
            session["textinput"] = found_user.text
        else:
            lnk = redirects(link, "", datetime.now())
            db.session.add(lnk)
            db.session.commit()

        return redirect(url_for("inbox"))
    else:
        if redirect_of(session, "link"):
            link = session["link"]
            return render_template('base.html', link_valid=link)
        else:
            return render_template('base.html')


@app.route('/link', methods=["POST", "GET"])
def inbox():
    text = None
    if redirect_of(session, "link"):
        link = session["link"]

        if request.method == "POST":
            text = request.form["textinput"]
            session["textinput"] = text
            found_user = redirects.query.filter_by(linker=link).first()
            found_user.text = text
            db.session.commit()
            flash("Your text has been saved for later!", "info")
        else:
            if "textinput" in session:
                text = session["textinput"]
        return render_template('customarea.html', linkname=link, textinput=text)
    else:
        return redirect(url_for("index"))


@app.route('/logout')
def logout():
    link = session["link"]
    session.pop("link", None)
    session.pop("textinput", None)
    flash(f"{link.capitalize()} was replaced from the session!", "info")

    return redirect(url_for("index"))


def data_timeout():
    users = redirects.query.all()
    # rows = session.query(redirects).all()

    for user in users:
        stoppage = datetime.now()
        elapsed = stoppage - user.time_created

        if elapsed > app.permanent_session_lifetime:
            db.session.delete(user)
            db.session.commit()
            print(
                f"Deleting user {user.linker} after {elapsed.total_seconds()}")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(debug=True)
