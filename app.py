from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)
BUDGET_LIMIT = 5000  # Set your desired monthly budget here

def get_db_connection():
    conn = sqlite3.connect("expense.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/", methods=["GET", "POST"])
def index():
    conn = get_db_connection()
    cur = conn.cursor()

    # ADD EXPENSE
    if request.method == "POST":
        date = request.form["date"]
        category = request.form["category"]
        amount = request.form["amount"]
        description = request.form["description"]
        cur.execute("INSERT INTO expenses (date, category, amount, description) VALUES (?, ?, ?, ?)",
                    (date, category, amount, description))
        conn.commit()
        return redirect("/")

    # FILTERS & SORTING
    category_filter = request.args.get("category")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    sort = request.args.get("sort", "new")

    query = "SELECT * FROM expenses WHERE 1=1"
    params = []

    if category_filter:
        query += " AND category=?"; params.append(category_filter)
    if start_date:
        query += " AND date >= ?"; params.append(start_date)
    if end_date:
        query += " AND date <= ?"; params.append(end_date)
    
    query += " ORDER BY date DESC" if sort == "new" else " ORDER BY date ASC"
    
    cur.execute(query, params)
    expenses = cur.fetchall()

    # TOTALS CALCULATION
    cur.execute(f"SELECT SUM(amount) FROM ({query})", params)
    total = cur.fetchone()[0] or 0

    now = datetime.now()
    current_month_str = now.strftime('%Y-%m')
    cur.execute("SELECT SUM(amount) FROM expenses WHERE date LIKE ?", (f"{current_month_str}%",))
    monthly_total = cur.fetchone()[0] or 0

    # PIE CHART DATA
    cur.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    chart_data = cur.fetchall()
    categories = [row[0] for row in chart_data]
    amounts = [row[1] for row in chart_data]

    conn.close()
    return render_template("index.html", 
                           expenses=expenses, 
                           total=total, 
                           monthly_total=monthly_total, 
                           budget=BUDGET_LIMIT,
                           categories=categories, 
                           amounts=amounts,
                           current_month_name=now.strftime('%B'))

@app.route("/edit/<int:id>", methods=["POST"])
def edit(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE expenses SET date=?, category=?, amount=?, description=? WHERE id=?",
                (request.form['date'], request.form['category'], 
                 request.form['amount'], request.form['description'], id))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM expenses WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)