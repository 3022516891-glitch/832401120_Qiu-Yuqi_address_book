# Address Book Coding Standards

These conventions apply to the Flask routes, SQLite storage, Excel handling, and browser interface in this repository.

## Python and project structure

- Use four spaces for indentation and UTF-8 for source files.
- Use `snake_case` for Python modules, functions, and local variables, and `UPPER_CASE` for constants.
- Keep standard library, third-party, and local imports in separate groups.
- Keep request handling in `app.py`, shared database operations in `storage.py`, the database schema in `schema.sql`, and workbook parsing and generation in `excel.py`.
- Place HTML in `templates/` and shared CSS in `static/`. Use Flask's `url_for()` for internal links and static URLs.

## Request handling and data integrity

- Use GET for reading pages and downloading workbooks. Use POST for adding contacts, changing favorites, or importing data.
- Validate form values on the server. Keep validation errors short, actionable, and in English, consistent with the rest of the interface.
- Use placeholders and bound parameters in SQL. Enable foreign-key checks on SQLite connections.
- Store contact methods in the related `contact_method` table. Save a contact and its methods in the same transaction.

## Excel compatibility

- Use `.xlsx` and put one contact on each row. Keep the `Name` header and put repeated methods in numbered columns such as `Phone 2`.
- Export phone numbers as text so leading zeros survive. Validate the complete workbook before saving any imported records.
- Use fictional names, phone numbers, and email addresses when testing or capturing screenshots.

## Checks before committing

1. Start the app with `python -m flask --app app run`.
2. Add a contact with two numbers, toggle its favorite status, and confirm that the Favorites filter works.
3. For Excel changes, export and re-import a workbook, then check that repeated methods and leading zeros survive. Try an invalid row and confirm that no contacts from that upload are saved.
4. Review the diff and use a short commit message describing the change. Keep the local database, virtual environment, preview logs, and credentials out of Git.
