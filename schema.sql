CREATE TABLE IF NOT EXISTS contact (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    favorite INTEGER NOT NULL DEFAULT 0 CHECK (favorite IN (0, 1))
);

CREATE TABLE IF NOT EXISTS contact_method (
    id INTEGER PRIMARY KEY,
    contact_id INTEGER NOT NULL REFERENCES contact(id) ON DELETE CASCADE,
    kind TEXT NOT NULL,
    value TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS contact_method_contact_id ON contact_method(contact_id);
