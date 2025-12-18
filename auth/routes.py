from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash

from auth.models import User, AuditLog

auth_bp = Blueprint("auth", __name__)


# =========================
# LOGIN
# =========================
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.home"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are required", "danger")
            return render_template("login.html")

        user = User.authenticate(username, password)
        if user:
            login_user(user)
            return redirect(url_for("dashboard.home"))

        flash("Invalid username or password", "danger")

    return render_template("login.html")


# =========================
# LOGOUT
# =========================
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


# =========================
# SELF – CHANGE PASSWORD
# =========================
@auth_bp.route("/profile/change-password", methods=["GET", "POST"])
@login_required
def change_own_password():
    if request.method == "POST":
        current_pw = request.form.get("current_password", "")
        new_pw = request.form.get("new_password", "")
        confirm_pw = request.form.get("confirm_password", "")

        if not current_pw or not new_pw or not confirm_pw:
            flash("All fields are required", "danger")
            return redirect(url_for("auth.change_own_password"))

        if not User.authenticate(current_user.username, current_pw):
            flash("Current password is incorrect", "danger")
            return redirect(url_for("auth.change_own_password"))

        if new_pw != confirm_pw:
            flash("Passwords do not match", "danger")
            return redirect(url_for("auth.change_own_password"))

        if len(new_pw) < 6:
            flash("New password must be at least 6 characters", "danger")
            return redirect(url_for("auth.change_own_password"))

        data = User.load_users()
        if current_user.id in data:
            data[current_user.id]["password"] = generate_password_hash(new_pw)
            User.save_users(data)

            AuditLog.log(
                actor=current_user.username,
                action="Changed own password",
                target=current_user.username
            )

            flash("Password updated successfully", "success")

        return redirect(url_for("dashboard.home"))

    return render_template("change_password.html")


# =========================
# ADMIN – USER MANAGEMENT
# =========================
@auth_bp.route("/admin/users", methods=["GET", "POST"])
@login_required
def admin_users():
    if not current_user.is_admin:
        abort(403)

    if request.method == "POST" and request.form.get("action") == "create":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "analyst")

        if not username or not password:
            flash("Username and password are required", "danger")
        else:
            new_user = User.create(username, password, role)
            if new_user:
                AuditLog.log(
                    actor=current_user.username,
                    action="Created user",
                    target=username
                )
                flash("User created successfully", "success")
                return redirect(url_for("auth.admin_users"))
            else:
                flash("Username already exists or invalid", "danger")

    users = User.list_users()
    return render_template("admin_users.html", users=users)


# =========================
# ADMIN – UPDATE ROLE
# =========================
@auth_bp.route("/admin/users/role/<user_id>", methods=["POST"])
@login_required
def update_user_role(user_id):
    if not current_user.is_admin:
        abort(403)

    if user_id in ("0", str(current_user.id)):
        flash("Operation not allowed", "danger")
        return redirect(url_for("auth.admin_users"))

    new_role = request.form.get("role")
    data = User.load_users()

    if user_id in data and new_role in ("admin", "analyst"):
        data[user_id]["role"] = new_role
        User.save_users(data)

        AuditLog.log(
            actor=current_user.username,
            action=f"Changed role to {new_role}",
            target=data[user_id]["username"]
        )

        flash("User role updated successfully", "success")

    return redirect(url_for("auth.admin_users"))


# =========================
# ADMIN – RESET PASSWORD
# =========================
@auth_bp.route("/admin/users/reset-password/<user_id>", methods=["POST"])
@login_required
def reset_user_password(user_id):
    if not current_user.is_admin:
        abort(403)

    if user_id in ("0", str(current_user.id)):
        flash("Operation not allowed", "danger")
        return redirect(url_for("auth.admin_users"))

    new_password = request.form.get("new_password", "")
    if len(new_password) < 6:
        flash("Password must be at least 6 characters", "danger")
        return redirect(url_for("auth.admin_users"))

    data = User.load_users()
    if user_id in data:
        data[user_id]["password"] = generate_password_hash(new_password)
        User.save_users(data)

        AuditLog.log(
            actor=current_user.username,
            action="Reset password",
            target=data[user_id]["username"]
        )

        flash("Password reset successfully", "success")

    return redirect(url_for("auth.admin_users"))


# =========================
# ADMIN – DELETE USER
# =========================
@auth_bp.route("/admin/users/delete/<user_id>", methods=["POST"])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        abort(403)

    if user_id in ("0", str(current_user.id)):
        flash("Operation not allowed", "danger")
        return redirect(url_for("auth.admin_users"))

    data = User.load_users()
    if user_id in data:
        username = data[user_id]["username"]
        del data[user_id]
        User.save_users(data)

        AuditLog.log(
            actor=current_user.username,
            action="Deleted user",
            target=username
        )

        flash("User deleted successfully", "success")

    return redirect(url_for("auth.admin_users"))


# =========================
# ADMIN – AUDIT LOGS
# =========================
@auth_bp.route("/admin/audit")
@login_required
def audit_logs():
    if not current_user.is_admin:
        abort(403)

    logs = AuditLog.list_logs()
    return render_template("audit_logs.html", logs=logs)
