import os
import subprocess
from datetime import datetime
from urllib.parse import urlparse

from flask import current_app


class BackupService:

    @staticmethod
    def backup_database():

        database_uri = current_app.config["SQLALCHEMY_DATABASE_URI"]

        mysqldump_path = current_app.config.get("MYSQLDUMP_PATH") or "mysqldump"

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

        # Only include -p if a password exists
        if password:
            command.append(f"-p{password}")

        command.append(database)

        with open(filepath, "w", encoding="utf-8") as output:

            result = subprocess.run(
                command,
                stdout=output,
                stderr=subprocess.PIPE,
                text=True,
            )

        if result.returncode != 0:
            print(result.stderr)

        return result.returncode == 0, filename