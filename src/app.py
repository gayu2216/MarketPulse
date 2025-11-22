from dataclasses import asdict
from flask import Flask, jsonify, request, render_template, redirect, url_for, session
import os

from src.controllers.account_controller import AccountController
from src.controllers.registration_controller import RegistrationController, RegistrationData
from src.controllers.sales_data_controller import SalesDataController


def create_app(test_config=None):
    app = Flask(__name__)
    ###
    app.secret_key = os.environ.get("FLASK_SECRET", "dev-secret") 
    account_ctrl = AccountController()
    registration_ctrl = RegistrationController(account_ctrl)
    sales_data_ctrl = SalesDataController()
    ###

    @app.route("/", methods=["GET"])
    def index():
        return redirect(url_for('dashboard'))

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "GET":
            return render_template("create_account.html")

        if request.is_json:
            data = request.get_json(force=True) or {}
            reg_data = RegistrationData(
                first_name=(data.get("first_name") or "").strip(),
                last_name=(data.get("last_name") or "").strip(),
                phone=(data.get("phone") or None),
                username=(data.get("username") or "").strip(),
                email=(data.get("email") or "").strip(),
                password=data.get("password") or "",
                confirm_password=data.get("confirm_password") or data.get("password") or "",
            )
            try:
                user = registration_ctrl.register(reg_data)
                return jsonify({"success": True, "username": user.username}), 201
            except Exception as exc:
                return jsonify({"success": False, "error": str(exc)}), 400

        form = request.form
        reg_data = RegistrationData(
            first_name=form.get("first_name", "").strip(),
            last_name=form.get("last_name", "").strip(),
            phone=form.get("phone"),
            username=form.get("username", "").strip(),
            email=form.get("email", "").strip(),
            password=form.get("password") or "",
            confirm_password=form.get("confirm_password") or form.get("password") or "",
        )

        try:
            registration_ctrl.register(reg_data)
            return render_template(
                "action_confirmation.html",
                title="Account Successfully Created",
                message="Your account has been created successfully. You can now log in with your credentials.",
                button_text="Go to Login",
                button_url=url_for("login"),
            )
        except Exception as exc:
            error_msg = str(exc)
            field_map = {
                "first_name": ["first name", "first_name"],
                "last_name": ["last name", "last_name"],
                "phone": ["phone number", "phone"],
                "username": ["username", "username"],
                "email": ["email address", "email"],
                "password": ["password", "password"],
                "confirm_password": ["password confirmation", "confirm_password"],
            }

            field_errors = {}
            for field, names in field_map.items():
                for name in names:
                    if name.lower() in error_msg.lower():
                        field_errors[field] = error_msg
                        break

            return (
                render_template(
                    "create_account.html",
                    error=error_msg,
                    errors=field_errors,
                    first_name=reg_data.first_name,
                    last_name=reg_data.last_name,
                    phone=reg_data.phone or "",
                    username=reg_data.username,
                    email=reg_data.email,
                ),
                400,
            )

    @app.route("/login", methods=["GET"])
    def login_get():
        return render_template("login.html")

    @app.route("/create-account", methods=["GET"])
    def create_account_get():
        return redirect(url_for('register'))

    def require_login():
        username = session.get("username")
        if not username or not account_ctrl.is_authenticated(username):
            return None
        return username

    @app.route("/dashboard", methods=["GET"])
    def dashboard():
        username = require_login()
        if not username:
            return redirect(url_for("login_get"))
        return render_template("dashboard.html", username=username)

    @app.route("/settings", methods=["GET"])
    def settings():
        username = require_login()
        if not username:
            return redirect(url_for("login_get"))
        user = account_ctrl.get_user(username)
        if not user:
            return redirect(url_for("login_get"))
        return render_template("settings.html", username=username, user=user.to_dict() if hasattr(user, 'to_dict') else None)

    @app.route("/delete-account", methods=["GET"])
    def delete_account_get():
        username = require_login()
        if not username:
            return redirect(url_for("login_get"))
        return render_template("delete_verification.html")

    @app.route("/delete-account", methods=["POST"])
    def delete_account_post():
        username = require_login()
        if not username:
            if request.is_json:
                return jsonify({"success": False, "error": "Not authenticated"}), 401
            return redirect(url_for("login_get"))

        account_ctrl.delete_user(username)
        account_ctrl.logout(username)
        session.pop("username", None)

        if request.is_json:
            return jsonify({"success": True}), 200

        return render_template(
            "action_confirmation.html",
            title="Account Deleted Successfully",
            message="Your account has been permanently deleted. We're sorry to see you go!",
            button_text="Return to Home",
            next_url=url_for("index")
        )

    @app.route("/account-information", methods=["GET"])
    def account_information():
        username = require_login()
        if not username:
            return redirect(url_for("login_get"))
        user = account_ctrl.get_user(username)
        return render_template("account_information.html", user=user, username=username)

    @app.route("/account-information", methods=["POST"])
    def account_information_post():
        username = require_login()
        if not username:
            return redirect(url_for("login_get"))

        form = request.form
        new_username = form.get("username", username).strip()
        password = form.get("password") or None

        try:
            user = account_ctrl.update_user(
                username,
                new_username=new_username,
                first_name=(form.get("first_name") or None),
                last_name=(form.get("last_name") or None),
                phone=(form.get("phone") or None),
                email=(form.get("email") or None),
                password=password,
            )
            session["username"] = user.username
            return render_template(
                "account_information.html",
                user=user,
                username=user.username,
                success="Account information updated successfully",
            )
        except Exception as exc:
            return (
                render_template(
                    "account_information.html",
                    user=account_ctrl.get_user(username),
                    username=username,
                    error=str(exc),
                ),
                400,
            )

    @app.route("/logout", methods=["POST"])
    def logout_post():
        username = request.form.get("username") or request.json.get("username") if request.is_json else None
        if not username and "username" in request.cookies:
            username = request.cookies.get("username")

        if username:
            account_ctrl.logout(username)

        if request.is_json:
            return jsonify({"success": True}), 200

        return render_template(
            "action_confirmation.html",
            title="Successfully Logged Out",
            message="You have been successfully logged out of your account.",
            button_text="Return to Login",
            next_url=url_for("login_get")
        )

    @app.route("/login", methods=["POST"])
    def login_post():
        if request.is_json:
            data = request.get_json(force=True)
            username = data.get("username")
            password = data.get("password")
            try:
                ok = account_ctrl.login(username, password)
                if ok:
                    session["username"] = username
                return jsonify({"success": ok}), 200
            except Exception as exc:
                return jsonify({"success": False, "error": str(exc)}), 400

        username = request.form.get("username")
        password = request.form.get("password")
        try:
            account_ctrl.login(username, password)
            session["username"] = username
            return redirect(url_for("dashboard"))
        except Exception as exc:
            return render_template("login.html", error=str(exc)), 400

    @app.route("/upload", methods=["GET", "POST"])
    def upload():
        username = require_login()
        if not username:
            return redirect(url_for("login_get"))

        if request.method == "GET":
            return render_template("upload.html", username=username)

        # POST request
        if 'file' not in request.files:
            return render_template("upload.html", username=username, error="No file provided"), 400

        file = request.files['file']
        if file.filename == '':
            return render_template("upload.html", username=username, error="No file selected"), 400

        try:
            file_path = sales_data_ctrl.save_uploaded_file(file, username)
            # Process the file immediately and store results in session
            sales_data = sales_data_ctrl.process_sales_data(file_path, username)
            if sales_data.get('success'):
                session['sales_data'] = sales_data
                return render_template("upload.html", username=username, success="File uploaded and processed successfully! You can now view the sales data."), 200
            else:
                return render_template("upload.html", username=username, error=f"Error processing file: {sales_data.get('error', 'Unknown error')}"), 400
        except Exception as exc:
            return render_template("upload.html", username=username, error=str(exc)), 400

    @app.route("/view-sales", methods=["GET"])
    def view_sales():
        username = require_login()
        if not username:
            return redirect(url_for("login_get"))

        # Try to get sales data from session first
        sales_data = session.get('sales_data')
        
        # If no data in session, try to process the most recent uploaded file
        if not sales_data:
            user_files = sales_data_ctrl.get_user_uploaded_files(username)
            if user_files:
                # Process the most recent file
                latest_file = max(user_files, key=lambda x: x['path'])
                sales_data = sales_data_ctrl.process_sales_data(latest_file['path'], username)
                if sales_data.get('success'):
                    session['sales_data'] = sales_data
                else:
                    return render_template("view_sales.html", username=username, error=sales_data.get('error', 'Error processing sales data')), 400
            else:
                return render_template("view_sales.html", username=username, error="No sales data found. Please upload a CSV file first."), 200

        return render_template("view_sales.html", username=username, sales_data=sales_data if sales_data.get('success') else None, error=sales_data.get('error') if not sales_data.get('success') else None)

    @app.route("/graphs/<path:filename>")
    def serve_graph(filename):
        """Serve graph images."""
        from flask import send_from_directory
        graphs_path = sales_data_ctrl.graphs_folder
        return send_from_directory(str(graphs_path), filename)

    return app

app = create_app()
