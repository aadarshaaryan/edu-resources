from flask import Flask, render_template, request, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "jgfjiosfjksdfjosd"


connection = sqlite3.connect("database.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS files(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT,
    file_name TEXT,
    file_img TEXT
)
""")


# cursor.execute("SELECT COUNT(*) FROM files WHERE file_name = ?", ("reflection and refraction of light",))
# exists = cursor.fetchone()[0]

# if exists == 0:
#     cursor.execute(
#         "INSERT INTO files(file_path, file_name, file_img) VALUES(?, ?, ?)",
#         ("static/PDFs/Light Reflection& Refraction short notes .pdf", "reflection and refraction of light", "https://cdn.slidesharecdn.com/ss_thumbnails/reflectionandrefractionoflight-241203110753-f7d15980-thumbnail.jpg?width=640&height=640&fit=bounds")
#     )
connection.commit()

connection.close()

@app.route('/', methods=["GET", "POST"])
def home():
    if request.method == "POST":
        rows = []   # only used for search results
        query = request.form.get("query")
        connection = sqlite3.connect("database.db")
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute("""
            SELECT * FROM files 
            WHERE file_name LIKE ? OR file_path LIKE ?
        """, ('%' + query + '%', '%' + query + '%'))
        rows = cursor.fetchall()
        connection.close()

        if not rows:
            flash(f"No files found for '{query}' ❌")

        return render_template("index.html", files=rows)

    # Default GET: show all files
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM files")
    rows = cursor.fetchall()
    connection.close()
    return render_template('index.html', files=rows)

def get_db_connection():
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row
    return connection


@app.route("/show_table")
def show_files():
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM files")
    rows = cursor.fetchall()
    connection.close()
    return render_template("show_table.html", files=rows)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
