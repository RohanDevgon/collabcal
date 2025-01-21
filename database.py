from flask import Flask, request
import mysql.connector

app = Flask(__name__)

# Establish a connection to the database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="ROMEO2003",
    database="cal"
)

@app.route("/add-user", methods=["POST"])
def add_user():
    username = request.form.get("username")
    password = request.form.get("password")
    
    cursor = db.cursor()
    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
    db.commit()
    cursor.close()
    return "User added successfully!"

if __name__ == "__main__":
    app.run(debug=True)
