import os
import subprocess
from datetime import datetime
from urllib.parse import urlparse

from flask import current_app


class BackupService:

    @staticmethod
    def backup_database():

        database_uri = current_app.config["SQLALCHEMY_DATABASE_URI"]

        mysqldump_path = (
            current_app.config.get("MYSQLDUMP_PATH")
            or "mysqldump"
        )

        parsed = urlparse(database_uri)

        host = parsed.hostname
        user = parsed.username
        password = parsed.password or ""
        database = parsed.path.lstrip("/")

        backup_dir = os.path.join(
            current_app.root_path,
            "backups"
        )

        os.makedirs(
            backup_dir,
            exist_ok=True
        )

        filename = datetime.now().strftime(
            "backup_%Y%m%d_%H%M%S.sql"
        )

        filepath = os.path.join(
            backup_dir,
            filename
        )

        command = [
            mysqldump_path,
            "-h",
            host,
            "-u",
            user,
        ]

        if password:
            command.append(f"-p{password}")

        command.append(database)

        with open(
            filepath,
            "w",
            encoding="utf-8"
        ) as output:

            result = subprocess.run(
                command,
                stdout=output,
                stderr=subprocess.PIPE,
                text=True,
            )

        if result.returncode != 0:

            print(result.stderr)

            return False, filename

        return True, filename


    @staticmethod
    def restore_database(backup_filename):

        database_uri = current_app.config[
            "SQLALCHEMY_DATABASE_URI"
        ]

        mysql_path = (
            current_app.config.get("MYSQL_PATH")
            or "mysql"
        )

        parsed = urlparse(database_uri)

        host = parsed.hostname
        user = parsed.username
        password = parsed.password or ""
        database = parsed.path.lstrip("/")

        backup_dir = os.path.join(
            current_app.root_path,
            "backups"
        )

        backup_filename = os.path.basename(
            backup_filename
        )

        filepath = os.path.join(
            backup_dir,
            backup_filename
        )

        # Validate backup file

        if not os.path.isfile(filepath):

            return (
                False,
                "Backup file not found."
            )

        if not backup_filename.lower().endswith(".sql"):

            return (
                False,
                "Invalid backup file."
            )

        # Create safety backup

        safety_success, safety_filename = (
            BackupService.backup_database()
        )

        if not safety_success:

            return (
                False,
                "Restore cancelled because "
                "the safety backup failed."
            )

        # Build MySQL restore command

        command = [
            mysql_path,
            "-h",
            host,
            "-u",
            user,
        ]

        if password:

            command.append(
                f"-p{password}"
            )

        command.append(database)

        # Restore database

        try:

            with open(
                filepath,
                "r",
                encoding="utf-8"
            ) as sql_file:

                result = subprocess.run(
                    command,
                    stdin=sql_file,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )

            if result.returncode != 0:

                error_message = (
                    result.stderr.strip()
                    or "Database restore failed."
                )

                print(error_message)

                return (
                    False,
                    "Restore failed. "
                    f"Safety backup preserved: "
                    f"{safety_filename}. "
                    f"{error_message}"
                )

            return (
                True,
                "Database restored successfully. "
                f"Safety backup: "
                f"{safety_filename}"
            )

        except Exception as e:

            print(str(e))

            return (
                False,
                "Restore failed. "
                f"Safety backup preserved: "
                f"{safety_filename}. "
                f"{str(e)}"
            )