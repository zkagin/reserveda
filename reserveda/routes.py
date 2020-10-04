from flask import jsonify, make_response, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user, login_required
from reserveda import app, api
from reserveda.forms import AddItemForm, LogInForm, SignUpForm


@app.route("/", methods=["GET", "POST"])
def index():
    api.setup_db()

    code = request.args.get("c")
    data = None
    if code:
        data = {"code": code}
    signup_form = SignUpForm(prefix="signup", data=data)
    login_form = LogInForm(prefix="login")
    if signup_form.validate_on_submit():
        user = api.register(
            email=signup_form.email.data,
            password=signup_form.password.data,
            code=signup_form.code.data,
        )
        login_user(user, remember=True)
        return redirect(url_for("main"))
    if login_form.validate_on_submit():
        user = api.login(email=login_form.email.data, password=login_form.password.data)
        if user:
            login_user(user, remember=True)
            return redirect(url_for("main"))
    return render_template("index.html", signup_form=signup_form, login_form=login_form)


@app.route("/signout", methods=["GET"])
def signout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/main", methods=["GET", "POST"])
@login_required
def main():
    form = AddItemForm()
    if form.validate_on_submit():
        api.add_item(email=current_user.email, name=form.name.data)
        return redirect(url_for("main"))
    items = api.list_items(current_user.group_id)
    return render_template("main.html", items=items, form=form)


####################
# Non-UI Endpoints #
####################


@app.route("/toggle_item", methods=["POST"])
def toggle_item():
    if not current_user:
        return False
    result = api.toggle_item(id=request.json["id"])
    return make_response(jsonify({"status": result}), 200)
