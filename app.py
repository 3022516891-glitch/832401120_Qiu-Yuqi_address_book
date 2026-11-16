from pathlib import Path
from xml.etree.ElementTree import ParseError
from zipfile import BadZipFile

from flask import Flask, abort, redirect, render_template, request, send_file, url_for

from openpyxl.utils.exceptions import InvalidFileException

from excel import export_contacts, import_contacts
from storage import get_db, init_app, insert_contact


METHOD_LABELS = {
    "电话": "Phone",
    "邮箱": "Email",
    "社交账号": "Social account",
    "地址": "Address",
    "其他": "Other",
}
METHOD_TYPES = tuple(METHOD_LABELS)


def list_contacts(favorites_only=False):
    rows = get_db().execute(
        """
        SELECT c.*, m.kind, m.value
        FROM contact c LEFT JOIN contact_method m ON m.contact_id = c.id
        WHERE ? = 0 OR c.favorite = 1
        ORDER BY c.favorite DESC, c.name COLLATE NOCASE, c.id, m.id
        """,
        (favorites_only,),
    )
    contacts = {}
    for row in rows:
        contact = contacts.setdefault(
            row["id"],
            dict(id=row["id"], name=row["name"], favorite=row["favorite"], methods=[]),
        )
        if row["kind"] is not None:
            contact["methods"].append((METHOD_LABELS[row["kind"]], row["value"]))
    return contacts.values()


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(DATABASE=Path(app.instance_path) / "contacts.sqlite3")
    if test_config is not None:
        app.config.update(test_config)
    init_app(app)

    @app.get("/")
    def index():
        favorites_only = request.args.get("favorites") == "1"
        return render_template(
            "index.html", contacts=list_contacts(favorites_only), favorites_only=favorites_only
        )

    @app.route("/contacts/new", methods=["GET", "POST"])
    def new_contact():
        name = ""
        methods = [(METHOD_TYPES[0], "")]
        error = None
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            kinds = request.form.getlist("kind")
            values = request.form.getlist("value")
            methods = list(zip(kinds, (value.strip() for value in values)))
            if not name or len(name) > 100:
                error = "Enter a name between 1 and 100 characters."
            elif len(kinds) != len(values) or any(
                kind not in METHOD_TYPES or len(value) > 300 for kind, value in methods
            ):
                error = "Choose a valid contact method type and enter at most 300 characters per method."
            else:
                db = get_db()
                with db:
                    insert_contact(db, name, False, methods)
                return redirect(url_for("index"), code=303)
        return render_template(
            "new.html", name=name, methods=methods or [(METHOD_TYPES[0], "")],
            method_labels=METHOD_LABELS, error=error,
        ), (400 if error else 200)

    @app.get("/contacts/export.xlsx")
    def export_excel():
        template = request.args.get("template") == "1"
        contacts = () if template else list_contacts()
        return send_file(
            export_contacts(contacts, METHOD_LABELS.values()),
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name="contacts-template.xlsx" if template else "contacts.xlsx",
        )

    @app.route("/contacts/import", methods=["GET", "POST"])
    def import_excel():
        if request.method == "GET":
            return render_template("import.html")
        request.max_content_length = 5 * 1024 * 1024
        upload = request.files.get("workbook")
        if not upload or not upload.filename.lower().endswith(".xlsx"):
            return render_template("import.html", error="Choose an .xlsx file."), 400
        try:
            contacts = import_contacts(upload.stream, METHOD_LABELS)
        except ValueError as error:
            return render_template("import.html", error=str(error)), 400
        except (BadZipFile, InvalidFileException, ParseError, KeyError, IndexError, OSError):
            return render_template("import.html", error="This workbook could not be opened."), 400
        if not contacts:
            return render_template("import.html", error="The workbook has no contacts."), 400
        db = get_db()
        with db:
            for name, favorite, methods in contacts:
                insert_contact(db, name, favorite, methods)
        return render_template("import.html", imported=len(contacts))

    @app.post("/contacts/<int:contact_id>/favorite")
    def favorite(contact_id):
        db = get_db()
        with db:
            cursor = db.execute(
                "UPDATE contact SET favorite = 1 - favorite WHERE id = ?", (contact_id,)
            )
            if cursor.rowcount == 0:
                abort(404)
        filters = {"favorites": 1} if request.form.get("favorites") == "1" else {}
        return redirect(url_for("index", **filters), code=303)

    return app
