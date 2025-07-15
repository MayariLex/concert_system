# ==================== IMPORTS ====================
from flask import Flask, render_template, request, redirect, flash,url_for,  session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from db_config import Config
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from flask_wtf import CSRFProtect
from datetime import timedelta
from functools import wraps
import os
from collections import defaultdict

# ==================== APP CONFIG ====================
app = Flask(__name__)
app.config.from_object(Config)

mysql = MySQL(app)
mail = Mail(app)
csrf = CSRFProtect(app)

# ==================== LOGIN REQUIRED DECORATOR ====================
def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash("Please log in first.", "warning")
                return redirect('/login')
            if role and session.get('role') != role:
                flash("Access denied.", "danger")
                return redirect('/')
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ==================== HOME ====================
@app.route('/')
def home():
    return redirect('/login')

# ==================== REGISTER ====================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        hashed_password = generate_password_hash(password)
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, email, password_hash, role) VALUES (%s, %s, %s, 'user')",
                    (username, email, hashed_password))
        mysql.connection.commit()
        cur.close()
        flash("Registered successfully!", "success")
        return redirect('/login')

    return render_template("register.html")

# ==================== LOGIN ====================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT id, username, role, password_hash FROM users WHERE email=%s", (email,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[2]
            return redirect('/admin/dashboard' if user[2] == 'admin' else '/user/dashboard')
        else:
            flash("Invalid credentials", "danger")
            return redirect('/login')

    return render_template("login.html")

# ==================== LOGOUT ====================
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect('/login')

# ==================== ADMIN DASHBOARD ====================
@app.route('/admin/dashboard')
def admin_dashboard():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM concerts ORDER BY date DESC")
    concerts = cur.fetchall()
    cur.close()
    return render_template("admin_dashboard.html", concerts=concerts)

# ==================== USER DASHBOARD ====================
@app.route('/user/dashboard')
@login_required(role='user')
def user_dashboard():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM concerts")
    concerts = cur.fetchall()
    cur.close()
    return render_template('user_dashboard.html', concerts=concerts)

# ==================== ADD CONCERT ====================
@app.route('/admin/add_concert', methods=['GET', 'POST'])
@login_required(role='admin')
def add_concert():
    if request.method == 'POST':
        name = request.form['name']
        artist = request.form['artist']
        date = request.form['date']
        location = request.form['location']
        layout = int(request.form['layout'])
        poster = request.files['poster']

        filename = secure_filename(poster.filename)
        poster.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO concerts (name, artist, date, location, layout, poster)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, artist, date, location, layout, filename))
        concert_id = cur.lastrowid

        layouts = {
            1: ["VVIP", "VIP", "Patron A", "Patron B", "General Admission"],
            2: ["Floor Standing", "VIP Standing", "Lower Box", "Upper Box", "General Admission"],
            3: ["VVIP", "VIP Seated", "Gold", "Silver", "Bronze"],
            4: ["VIP PEAT", "Patron A", "Patron B", "Upper Box A", "Upper Box B"]
        }

        for cat in layouts.get(layout, []):
            price = request.form.get(f"price_{cat}")
            seat_count = request.form.get(f"count_{cat}")

            if price and seat_count:
                cur.execute("INSERT INTO categories (name, price, concert_id) VALUES (%s, %s, %s)",
                            (cat, price, concert_id))
                category_id = cur.lastrowid

                # Generate custom number of seats based on admin input
                for i in range(1, int(seat_count) + 1):
                    label = f"{cat[:1]}{i}"
                    cur.execute(
                        "INSERT INTO seats (label, category_id, concert_id, status) VALUES (%s, %s, %s, 'available')",
                        (label, category_id, concert_id))

        mysql.connection.commit()
        cur.close()
        flash("Concert added successfully!", "success")
        return redirect('/admin/dashboard')

    return render_template('add_concert.html')

# ==================== BOOK SEATS ====================
@app.route('/book/<int:concert_id>')
@login_required(role='user')
def book_seats(concert_id):
    cur = mysql.connection.cursor()

    # Check concert status
    cur.execute("SELECT name, poster, location, date, status FROM concerts WHERE id = %s", (concert_id,))
    concert = cur.fetchone()

    if not concert:
        flash("Concert not found.", "danger")
        return redirect('/user/dashboard')

    if concert[4] == 'done':  # status = 'done'
        flash("This concert is already done. Booking is closed.", "info")
        return redirect('/user/dashboard')

    cur.execute("SELECT id, name, price FROM categories WHERE concert_id = %s", (concert_id,))
    category_data = cur.fetchall()

    categories = {}
    prices = {}
    for cat_id, cat_name, price in category_data:
        prices[cat_id] = price
        cur.execute("""
            SELECT id, label, status
            FROM seats
            WHERE category_id = %s AND concert_id = %s
            ORDER BY label
        """, (cat_id, concert_id))
        seat_list = cur.fetchall()
        categories[(cat_id, cat_name)] = seat_list

    cur.close()

    return render_template('book_seats.html',
                           concert=concert,
                           concert_id=concert_id,
                           categories=categories,
                           prices=prices)

# ==================== PURCHASE SEATS ====================
@app.route('/purchase/<int:concert_id>', methods=['POST'])
@login_required(role='user')
def purchase(concert_id):
    if 'user_id' not in session:
        return redirect('/login')

    seat_ids_raw = request.form.get('seats')
    if not seat_ids_raw:
        flash("No seats selected", "danger")
        return redirect(f'/book/{concert_id}')

    selected_seats = seat_ids_raw.split(',')
    if not selected_seats:
        flash("No valid seats selected", "danger")
        return redirect(f'/book/{concert_id}')

    cur = mysql.connection.cursor()

    # Verify seats and fetch label, price, category
    format_strings = ','.join(['%s'] * len(selected_seats))
    cur.execute(f"""
        SELECT seats.id, seats.label, categories.price, categories.name
        FROM seats
        JOIN categories ON seats.category_id = categories.id
        WHERE seats.id IN ({format_strings}) AND seats.status = 'available'
    """, tuple(selected_seats))
    valid_seats = cur.fetchall()

    if len(valid_seats) != len(selected_seats):
        flash("Some selected seats are already sold or invalid.", "danger")
        return redirect(f'/book/{concert_id}')

    total_price = sum(price for _, _, price, _ in valid_seats)

    # Insert order
    cur.execute("INSERT INTO orders (user_id, concert_id, total_price) VALUES (%s, %s, %s)",
                (session['user_id'], concert_id, total_price))
    order_id = cur.lastrowid

    # Insert order_items and mark seats sold
    seats_data = []
    for seat_id, label, price, category in valid_seats:
        cur.execute("INSERT INTO order_items (order_id, seat_id) VALUES (%s, %s)", (order_id, seat_id))
        cur.execute("UPDATE seats SET status = 'sold' WHERE id = %s", (seat_id,))
        seats_data.append({
            'label': label,
            'price': price,
            'category': category
        })

    # Get user email
    cur.execute("SELECT email FROM users WHERE id = %s", (session['user_id'],))
    email = cur.fetchone()[0]

    # Get concert details (name, location, date)
    cur.execute("SELECT name, location, date FROM concerts WHERE id = %s", (concert_id,))
    concert_info = cur.fetchone()
    concert_name, concert_location, concert_date = concert_info

    # Admin notification
    cur.execute("INSERT INTO notifications (user_id, concert_id, order_id) VALUES (%s, %s, %s)",
                (session['user_id'], concert_id, order_id))

    mysql.connection.commit()
    cur.close()

    # Send email
    send_email_receipt(
        to_email=email,
        username=session['username'],
        concert_name=concert_name,
        concert_location=concert_location,
        concert_date=concert_date,
        seats=seats_data,
        total_price=total_price
    )

    # Render receipt
    return render_template('receipt.html',
                           username=session['username'],
                           concert_id=concert_id,
                           concert_name=concert_name,
                           concert_location=concert_location,
                           concert_date=concert_date,
                           seats=seats_data,
                           total=total_price)


# ==================== SEND EMAIL RECEIPT ====================
def send_email_receipt(to_email, username, concert_name, concert_location, concert_date, seats, total_price):
    # Group seats by category
    from collections import defaultdict
    seat_by_category = defaultdict(list)
    for seat in seats:
        seat_by_category[seat['category']].append(seat['label'])

    # Build the seat list per category
    seat_details = ""
    for category, labels in seat_by_category.items():
        seat_details += f"  • {category}: {', '.join(labels)}\n"

    subject = "🎟️ Your Concert Ticket Receipt"
    body = f"""\
Hello {username},

Thank you for your ticket purchase! 🎉

🎤 Concert: {concert_name}
📍 Location: {concert_location}
📅 Date: {concert_date}

💺 Seats by Category:
{seat_details.strip()}

💰 Total Paid: ₱{total_price}

We look forward to seeing you at the event!
For any questions, just reply to this email.

Cheers,  
🎶 The ConcertTix Team
"""

    msg = Message(subject, recipients=[to_email])
    msg.body = body
    mail.send(msg)





# ==================== VIEW USER TICKETS ====================
@app.route('/user/tickets')
@login_required(role='user')
def user_tickets():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT o.id, o.timestamp, c.name, cat.name, s.label, cat.price
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        JOIN seats s ON oi.seat_id = s.id
        JOIN categories cat ON s.category_id = cat.id
        JOIN concerts c ON o.concert_id = c.id
        WHERE o.user_id = %s
        ORDER BY o.timestamp DESC
    """, (session['user_id'],))
    tickets = cur.fetchall()
    cur.close()
    return render_template("user_tickets.html", tickets=tickets)

# ==================== ADMIN NOTIFICATIONS ====================
@app.route('/admin/notifications')
@login_required(role='admin')
def admin_notifications():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT n.id, u.username, c.name, n.created_at
        FROM notifications n
        JOIN users u ON n.user_id = u.id
        JOIN concerts c ON n.concert_id = c.id
        ORDER BY n.created_at DESC
    """)
    notifications = cur.fetchall()
    cur.close()
    return render_template('admin_notifications.html', notifications=notifications)
# ==================== ADMIN: VIEW ALL CONCERTS ====================
@app.route('/admin/concerts')
@login_required(role='admin')
def admin_concerts():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, artist, date, location, layout, status FROM concerts ORDER BY date DESC")
    concerts = cur.fetchall()
    cur.close()
    return render_template('admin_concerts.html', concerts=concerts)

# ==================== ADMIN: EDIT PRICES ====================
@app.route('/admin/edit_concert/<int:concert_id>', methods=['GET', 'POST'])
@login_required(role='admin')
def edit_concert(concert_id):
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        # Update prices
        for key in request.form:
            if key.startswith("price_"):
                cat_id = key.split("_")[1]
                price = request.form[key]
                cur.execute("UPDATE categories SET price = %s WHERE id = %s", (price, cat_id))
        mysql.connection.commit()
        cur.close()
        flash("Seat prices updated.", "success")
        return redirect('/admin/concerts')

    # Get concert name
    cur.execute("SELECT name FROM concerts WHERE id = %s", (concert_id,))
    concert = cur.fetchone()

    # Get all categories and prices
    cur.execute("SELECT id, name, price FROM categories WHERE concert_id = %s", (concert_id,))
    categories = cur.fetchall()
    cur.close()

    return render_template("edit_concert.html", concert=concert, categories=categories, concert_id=concert_id)

# ==================== ADMIN: MARK CONCERT AS DONE ====================
@app.route('/admin/mark_done/<int:concert_id>', methods=['POST'])
@login_required(role='admin')
def mark_concert_done(concert_id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE concerts SET status = 'done' WHERE id = %s", (concert_id,))
    mysql.connection.commit()
    cur.close()

    flash("✅ Concert marked as done successfully.", "success")
    return redirect('/admin/dashboard')









# ==================== RUN APP ====================
if __name__ == '__main__':
    app.run(debug=True)
