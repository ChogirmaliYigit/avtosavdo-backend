from django.http import HttpResponse


def download_db(*args, **kwargs):
    file_path = "database.sql"

    with open(file_path, "rb") as file:
        response = HttpResponse(file.read(), content_type="application/octet-stream")
        response["Content-Disposition"] = f"attachment; filename=database"
        return response
