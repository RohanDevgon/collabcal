from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="ROMEO2003",
        database="cal"
    )

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        session["user"] = username
        return redirect(url_for("dashboard"))
    else:
        error_message = "Invalid credentials! Please try again."
        return render_template("home.html", error=error_message)





@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Changed 'username' to 'name' based on the updated form field
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Assuming get_db_connection is a function that returns your DB connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert user data into the 'users' table
        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
        conn.commit()
        conn.close()

        return redirect(url_for('home'))  # Redirect to the home page after successful signup

    return render_template('signup.html')  # Render the signup page if it's a GET request


@app.route('/dashboard')
def dashboard():
    if "user" not in session:
        return redirect(url_for("home"))

    return render_template('dashboard.html')

@app.route("/my-calendar")
def my_calendar():
    if "user" in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = %s", (session["user"],))
        user_id = cursor.fetchone()[0]  # Fetching the correct user_id

        print(f"User ID for {session['user']}: {user_id}")  # Debug print to check user_id
        
        cursor.execute("SELECT * FROM events WHERE user_id = %s", (user_id,))
        events = cursor.fetchall()
        conn.close()

        print(f"Events fetched for user {session['user']}: {events}")  # Debug print to check fetched events
        
        return render_template("my-calendar.html", events=events)
    return redirect(url_for("home"))


@app.route("/shared")
def view_shared_calendar():
    if "user" not in session:
        return redirect(url_for("home"))
    
    # Fetch all users except the logged-in user
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email != %s", (session["user"],))
    users = cursor.fetchall()
    conn.close()

    return render_template("shared.html", users=users)



@app.route("/user-months/<username>")
def user_months(username):
    if "user" not in session:
        return redirect(url_for("home"))
    
    months = [
        "January", "February", "March", "April", "May", "June", 
        "July", "August", "September", "October", "November", "December"
    ]
    
    return render_template("user-months.html", username=username, months=months)


@app.route("/user-month-events/<username>/<month>")
def user_month_events(username, month):
    if "user" not in session:
        return redirect(url_for("home"))

    month_mapping = {
        "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
        "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12
    }

    if month not in month_mapping:
        return "Invalid month", 400

    selected_month = month_mapping[month]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, description, event_date, event_time FROM events 
        WHERE MONTH(event_date) = %s 
        AND YEAR(event_date) = YEAR(CURRENT_DATE()) 
        AND user_id = (SELECT id FROM users WHERE name = %s)
    """, (selected_month, username))
    
    events = cursor.fetchall()
    conn.close()

    return render_template("user-month-events.html", username=username, month=month, events=events)




# @app.route("/book-appointment/<username>", methods=["POST"])
# def book_appointment(username):
#     if "user" not in session:
#         return redirect(url_for("home"))

#     appointment_date = request.form.get("date")
#     appointment_time = request.form.get("time")
#     appointment_title = request.form.get("title")

#     if appointment_date and appointment_time and appointment_title:
#         conn = get_db_connection()
#         cursor = conn.cursor()
#         cursor.execute("SELECT id FROM users WHERE email = %s", (username,))
#         user_id = cursor.fetchone()[0]
        
#         cursor.execute("""
#             INSERT INTO events (user_id, name, event_date, event_time)
#             VALUES (%s, %s, %s, %s)
#         """, (user_id, appointment_title, appointment_date, appointment_time))
#         conn.commit()
#         conn.close()

#         return redirect(url_for("user_calendar", username=username))

#     return "Failed to book appointment!", 400

# from datetime import datetime

# from datetime import datetime



@app.route("/month/<month>", methods=["GET", "POST"])
def month_view(month):
    if "user" not in session:
        return redirect(url_for("home"))

    # Convert the month name to its numeric value (e.g., 'January' -> 1)
    month_mapping = {
        "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
        "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12
    }

    if month not in month_mapping:
        return "Invalid month", 400  # Handling invalid month input

    selected_month = month_mapping[month]

    if request.method == "POST":
        event_date = request.form.get("date")
        event_time = request.form.get("time")
        event_title = request.form.get("title")
        
        if event_date and event_title and event_time:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE email = %s", (session["user"],))
            user_id = cursor.fetchone()[0]
            
            print(f"User ID for {session['user']} (during event creation): {user_id}")  # Debug print
            
            cursor.execute(""" 
                INSERT INTO events (user_id, name, event_date, event_time) 
                VALUES (%s, %s, %s, %s)
            """, (user_id, event_title, event_date, event_time))
            conn.commit()
            conn.close()

            # After adding the event, fetch updated events and reflect them
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM events 
                WHERE MONTH(event_date) = %s AND YEAR(event_date) = YEAR(CURRENT_DATE()) 
                AND user_id = (SELECT id FROM users WHERE email = %s)
            """, (selected_month, session["user"]))
            events = cursor.fetchall()
            conn.close()

            return render_template("month-view.html", month=month, events=events)

    # Fetch events for the selected month
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print(f"Month selected: {month} (Numeric: {selected_month})")  # Debug print
    
    cursor.execute("""
        SELECT * FROM events WHERE MONTH(event_date) = %s 
        AND YEAR(event_date) = YEAR(CURRENT_DATE()) 
        AND user_id = (SELECT id FROM users WHERE email = %s)
    """, (selected_month, session["user"]))
    
    events = cursor.fetchall()
    conn.close()

    print(f"Events for month {month} (Numeric: {selected_month}): {events}")  # Debug print
    
    return render_template("month-view.html", month=month, events=events)


from datetime import datetime




@app.route("/edit-event/<int:event_id>", methods=["GET", "POST"])
def edit_event(event_id):
    if "user" not in session:
        return redirect(url_for("home"))

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        event_title = request.form.get("title")
        event_date = request.form.get("date")
        event_time = request.form.get("time")

        # Ensure the date is valid
        try:
            event_date_obj = datetime.strptime(event_date, '%Y-%m-%d').date()  # Correct format conversion
        except ValueError:
            return "Invalid date format", 400  # Return error for invalid date format

        cursor.execute("""
            UPDATE events
            SET name = %s, event_date = %s, event_time = %s
            WHERE id = %s
        """, (event_title, event_date_obj, event_time, event_id))
        conn.commit()
        conn.close()

        # Get the month from the event_date object
        event_month = event_date_obj.month

        # After editing, fetch updated events and reflect them
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM events WHERE MONTH(event_date) = %s 
            AND YEAR(event_date) = YEAR(CURRENT_DATE()) 
            AND user_id = (SELECT id FROM users WHERE email = %s)
        """, (event_month, session["user"]))
        
        events = cursor.fetchall()
        conn.close()

        return render_template("month-view.html", month=str(event_month).zfill(2), events=events)

    cursor.execute("SELECT * FROM events WHERE id = %s", (event_id,))
    event = cursor.fetchone()
    conn.close()
    return render_template("edit-event.html", event=event)



@app.route("/delete-event/<int:event_id>/<month>", methods=["POST"])
def delete_event(event_id, month):
    if "user" not in session:
        return redirect(url_for("home"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT event_date FROM events WHERE id = %s", (event_id,))
    event = cursor.fetchone()

    if event:
        # Delete the event
        cursor.execute("DELETE FROM events WHERE id = %s", (event_id,))
        conn.commit()
        conn.close()

        # Redirect back to the month view the user was on
        return redirect(url_for("month_view", month=month))

    conn.close()
    return "Event not found", 404



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
