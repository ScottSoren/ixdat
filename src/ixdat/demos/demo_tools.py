"""Find the demo data and view the tables of an SQLite database in a browser."""

import html
import os
import sqlite3
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs

REPO_DIR = Path(__file__).parent.parent.parent.parent
DEMO_DATA_ENV_VAR = "IXDAT_DEMO_DATA_DIR"


def get_demo_data_dir():
    """Return the folder with the demo data used by the reader demos.

    The folder is given by the environment variable IXDAT_DEMO_DATA_DIR, or is
    ``demo_data/`` in the root of the ixdat repository.

    Raises:
        FileNotFoundError: if the folder does not exist.
    """
    data_dir = Path(os.environ.get(DEMO_DATA_ENV_VAR, REPO_DIR / "demo_data"))
    if not data_dir.is_dir():
        raise FileNotFoundError(
            f"No demo data found at {data_dir}. Put the demo data there, or set "
            f"the environment variable {DEMO_DATA_ENV_VAR} to the demo data folder."
        )
    return data_dir


def get_test_data_dir():
    """Return the ``test_data/`` folder of the ixdat repository."""
    return REPO_DIR / "test_data"


def make_page(selected, sqlite_file):
    db = sqlite3.connect(Path(sqlite_file).resolve().as_uri() + "?mode=ro", uri=True)
    tables = [
        row[0]
        for row in db.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
    ]
    table = selected if selected in tables else tables[0]
    cursor = db.execute('SELECT * FROM "{}"'.format(table))
    columns = [column[0] for column in cursor.description]
    rows = cursor.fetchall()
    db.close()

    links = " ".join(
        '<a href="/?table={0}">{0}</a>'.format(html.escape(name)) for name in tables
    )
    headings = "".join("<th>{}</th>".format(html.escape(name)) for name in columns)
    body = "".join(
        "<tr>{}</tr>".format("".join("<td>{}</td>".format(show(value)) for value in row))
        for row in rows
    )
    return (
        "<!doctype html><title>ixdat SQLite tables</title>"
        "<style>body{{font:14px sans-serif}}a{{margin-right:1em}}"
        "table{{border-collapse:collapse}}th,td{{border:1px solid;padding:4px}}"
        "th{{background:#eee}}</style><h1>ixdat SQLite tables</h1>"
        "<nav>{}</nav><h2>{}</h2><table><tr>{}</tr>{}</table>"
    ).format(links, html.escape(table), headings, body)


def show(value):
    return (
        "{} bytes".format(len(value))
        if isinstance(value, bytes)
        else html.escape(str(value))
    )


class TableHandler(BaseHTTPRequestHandler):
    """Serve one page per table of the SQLite file given by ``sqlite_file``."""

    sqlite_file = None

    def do_GET(self):
        query = parse_qs(self.path.partition("?")[2])
        page = make_page(
            query.get("table", [None])[0], sqlite_file=self.sqlite_file
        ).encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(page)


def view_tables(sqlite_file):
    """Open the tables of `sqlite_file` in a browser. Ctrl+C stops the server."""
    # The server makes a new handler for each request, so the file goes on a
    # handler class made for this call.
    handler = type("TableHandler", (TableHandler,), {"sqlite_file": sqlite_file})
    server = HTTPServer(("127.0.0.1", 0), handler)
    url = "http://127.0.0.1:{}".format(server.server_port)
    print("Open {} (Ctrl+C stops the server)".format(url))
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
