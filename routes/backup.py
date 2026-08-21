import os


from flask import (
    Blueprint,
    render_template,
    flash,
    redirect,
    url_for,
    send_from_directory,
    current_app,
)

from services.backup_service import BackupService
from utils.auth import login_required
from utils.permissions import permission_required

backup_bp = Blueprint(
    "backup",
    __name__,
    url_prefix="/backup",
)


@backup_bp.route("/")
@permission_required("backup.view")
def index():

    backup_dir = os.path.join(current_app.root_path, "backups")

    os.makedirs(backup_dir, exist_ok=True)

    backups = []

    for file in os.listdir(backup_dir):

        if file.endswith(".sql"):

            filepath = os.path.join(backup_dir, file)

            backups.append(
                {
                    "name": file,
                    "size": round(os.path.getsize(filepath) / 1024, 2),
                    "date": os.path.getmtime(filepath),
                }
            )

    backups.sort(key=lambda x: x["date"], reverse=True)

    return render_template("backup/index.html", backups=backups)


@backup_bp.route("/create", methods=["POST"])
@permission_required("backup.create")
def create_backup():

    success, filename = BackupService.backup_database()

    if success:

        flash(
            f"Database backup created successfully: " f"{filename}",
            "success",
        )

    else:

        flash(
            "Database backup failed.",
            "danger",
        )

    return redirect(url_for("backup.index"))


@backup_bp.route("/download/<filename>")
@permission_required("backup.view")
def download_backup(filename):

    backup_dir = os.path.join(current_app.root_path, "backups")

    filename = os.path.basename(filename)

    return send_from_directory(backup_dir, filename, as_attachment=True)


@backup_bp.route("/restore/<filename>", methods=["POST"])
@permission_required("backup.restore")
def restore_backup(filename):

    filename = os.path.basename(filename)

    success, message = BackupService.restore_database(filename)

    if success:

        flash(message, "success")

    else:

        flash(message, "danger")

    return redirect(url_for("backup.index"))


@backup_bp.route("/delete/<filename>", methods=["POST"])
@permission_required("backup.delete")
def delete_backup(filename):

    backup_dir = os.path.join(current_app.root_path, "backups")

    filename = os.path.basename(filename)

    filepath = os.path.join(backup_dir, filename)

    if os.path.exists(filepath):

        os.remove(filepath)

        flash("Backup deleted successfully.", "success")

    else:

        flash("Backup file not found.", "danger")

    return redirect(url_for("backup.index"))
