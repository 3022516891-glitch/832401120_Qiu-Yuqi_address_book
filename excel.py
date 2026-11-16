from collections import defaultdict
from io import BytesIO
from zipfile import ZipFile

from openpyxl import Workbook, load_workbook


def export_contacts(contacts, labels):
    grouped_contacts = []
    widths = dict.fromkeys(labels, 1)
    for contact in contacts:
        grouped = defaultdict(list)
        for label, value in contact["methods"]:
            grouped[label].append(value)
            widths[label] = max(widths[label], len(grouped[label]))
        grouped_contacts.append((contact, grouped))

    columns = [(label, index) for label in labels for index in range(widths[label])]
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Contacts"
    sheet.freeze_panes = "C2"
    sheet.append(["Name", "Favorite"] + [
        label if index == 0 else f"{label} {index + 1}" for label, index in columns
    ])
    for row_number, (contact, grouped) in enumerate(grouped_contacts, start=2):
        values = [contact["name"], bool(contact["favorite"])]
        for label, index in columns:
            entries = grouped[label]
            values.append(entries[index] if index < len(entries) else None)
        sheet.append(values)
        for cell in sheet[row_number]:
            if isinstance(cell.value, str):
                cell.data_type = "s"
                cell.number_format = "@"
    output = BytesIO()
    workbook.save(output)
    output.seek(0)
    return output


def import_contacts(stream, labels):
    with ZipFile(stream) as archive:
        if sum(entry.file_size for entry in archive.infolist()) > 32 * 1024 * 1024:
            raise ValueError("The workbook is too large when unpacked.")
    stream.seek(0)
    workbook = load_workbook(stream, read_only=True, keep_links=False)
    try:
        sheet = workbook["Contacts"] if "Contacts" in workbook else workbook.worksheets[0]
        sheet.reset_dimensions()
        rows = sheet.iter_rows()
        headers = [str(cell.value or "").strip().casefold() for cell in next(rows, ())]
        if headers.count("name") != 1 or headers.count("favorite") > 1:
            raise ValueError("Include one Name column and at most one Favorite column.")
        name_index = headers.index("name")
        favorite_index = headers.index("favorite") if "favorite" in headers else None
        methods = {}
        for index, header in enumerate(headers):
            for kind, label in labels.items():
                prefix = label.casefold()
                suffix = header.removeprefix(prefix)
                if header == prefix or (suffix.startswith(" ") and suffix[1:].isdecimal()):
                    methods[index] = kind
                    break
            else:
                if header and header not in {"name", "favorite"}:
                    raise ValueError(f"Unknown column: {header}. Use the downloaded template.")

        contacts = []
        for number, cells in enumerate(rows, start=2):
            if any(cell.data_type == "f" for cell in cells):
                raise ValueError(f"Row {number}: formulas are not supported. Paste values instead.")
            values = [str(cell.value).strip() if cell.value is not None else "" for cell in cells]
            if not any(values):
                continue
            values += [""] * (len(headers) - len(values))
            if any(values[len(headers):]) or any(value and not headers[i] for i, value in enumerate(values[:len(headers)])):
                raise ValueError(f"Row {number}: every value needs a column header.")
            name = values[name_index]
            favorite = values[favorite_index].casefold() if favorite_index is not None else ""
            entries = [(kind, values[i]) for i, kind in methods.items() if values[i]]
            if not name or len(name) > 100:
                raise ValueError(f"Row {number}: enter a name between 1 and 100 characters.")
            if favorite not in {"", "true", "false", "yes", "no", "1", "0"}:
                raise ValueError(f"Row {number}: Favorite must be Yes or No.")
            if any(len(value) > 300 for _, value in entries):
                raise ValueError(f"Row {number}: contact details must be at most 300 characters.")
            contacts.append((name, favorite in {"true", "yes", "1"}, entries))
        return contacts
    finally:
        workbook.close()
