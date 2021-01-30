# routes.py
# All URL endpoints that a user may access, including GET and POST endpoints.

import csv
import datetime
from io import StringIO
from flask import (
    flash,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    Response,
    url_for,
)
from flask_login import current_user, login_user, logout_user, login_required
from reserveda import app, api
from reserveda.forms import (
    AddItemForm,
    LogInForm,
    SignUpForm,
    ResetPasswordForm,
    ResetPasswordRequestForm,
)


@app.after_request
def add_header(response):
    """
    Adds an additional header to all served files that tells the browser not to cache
    the page. This is needed in order because some templates will manipulate the DOM,
    but going forward and back through the browser would otherwise ignore those changes.
    """
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


@app.route("/", methods=["GET", "POST"])
def index():
    """
    Serves the main index page.
    """
    code = request.args.get("c")
    data = None
    if code:
        data = {"code": code}
    signup_form = SignUpForm(prefix="signup", data=data)
    login_form = LogInForm(prefix="login")
    if signup_form.submit.data and signup_form.validate_on_submit():
        user = api.register(
            email=signup_form.email.data,
            password=signup_form.password.data,
            code=signup_form.code.data,
        )
        login_user(user, remember=True)
        return redirect(url_for("main"))
    if login_form.submit.data and login_form.validate_on_submit():
        user = api.login(email=login_form.email.data, password=login_form.password.data)
        if user:
            login_user(user, remember=True)
            return redirect(url_for("main"))
    return render_template("index.html", signup_form=signup_form, login_form=login_form)


@app.route("/signout", methods=["GET"])
def signout():
    """Signs the user out and redirects them back to the main page."""
    logout_user()
    return redirect(url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LogInForm()
    if form.validate_on_submit():
        user = api.login(email=form.email.data, password=form.password.data)
        if user:
            login_user(user, remember=True)
            return redirect(url_for("main"))
    return render_template("login.html", form=form)


@app.route("/main", methods=["GET", "POST"])
@login_required
def main():
    """Serves the main logged in page, which lists current items."""
    form = AddItemForm()
    if form.validate_on_submit():
        api.add_item(user_id=current_user.id, name=form.name.data)
        return redirect(url_for("main"))
    items = api.list_items(current_user.group_id)
    return render_template("main.html", items=items, form=form)


@app.route("/history/<item_id>", methods=["GET"])
@login_required
def history(item_id):
    """Shows the event history of a provided item."""
    events = api.list_events(current_user.id, item_id=item_id)
    item = api.get_item(item_id)
    event_pairs = []
    for event in events:
        if event.action == "reserved":
            event_pairs.append([event])
        if event.action == "returned":
            event_pairs[-1].append(event)

    return render_template("item_history.html", events=event_pairs, item=item)


@app.route("/reset_password_request", methods=["GET", "POST"])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for("main"))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        api.send_password_reset_email(form.email.data)
        flash(
            """
            Check your email for instructions to reset your password.
            Be sure to check the spam folder as well.
            """
        )
        return redirect(url_for("login"))
    return render_template("reset_password_request.html", form=form)


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("main"))
    user_email = api.verify_reset_password_token(token)
    if not user_email:
        return redirect(url_for("index"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        api.set_password(user_email, form.password.data)
        flash("Your password has been reset.")
        return redirect(url_for("login"))
    return render_template("reset_password.html", form=form)


####################
# Non-UI Endpoints #
####################


@app.route("/list_items", methods=["GET"])
@login_required
def list_items():
    """Provides a list of all items for the user's group."""
    items = api.list_items(current_user.group_id)
    response = {i.id: i.status for i in items}
    return make_response(jsonify(response), 200)


@app.route("/toggle_item", methods=["POST"])
@login_required
def toggle_item():
    """Turns the provided item id on or off."""
    user_id = current_user.id
    item_id = request.json["id"]
    comment = request.json["comment"] if "comment" in request.json else None
    force = bool(request.json["force"]) if "force" in request.json else False
    success = api.toggle_item(user_id, item_id, comment, force)
    return make_response(jsonify({"success": success}), 200)


@app.route("/delete_item", methods=["POST"])
@login_required
def delete_item():
    """Deletes the provided item id."""
    user_id = current_user.id
    item_id = request.json["id"]
    success = api.delete_item(user_id=user_id, item_id=item_id)
    return make_response(jsonify({"success": success}), 200)


@app.route("/download_history", methods=["GET"])
@login_required
def download_history():
    """Downloads a csv of the event history for a specified item."""
    item_id = request.args.get("id")
    offset = request.args.get("offset")
    events = api.list_events(current_user.id, item_id=item_id)
    csv_list = []
    for event in events:
        new_timestamp = event.timestamp - datetime.timedelta(minutes=int(offset))
        new_timestamp = new_timestamp.replace(microsecond=0)
        if event.action == "reserved":
            csv_list.append([event.user.email, new_timestamp, None, event.comment])
        elif event.action == "returned":
            csv_list[-1][2] = new_timestamp
    csv_list.append(["user", "reserved", "returned", "comment"])
    csv_list.reverse()

    def generate():
        data = StringIO()
        w = csv.writer(data)
        for row in csv_list:
            w.writerow(row)
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)

    response = Response(generate(), mimetype="text/csv")
    response.headers.set("Content-Disposition", "attachment")
    return response
