from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from datetime import datetime

app = Flask(__name__)

CSV_FILE = 'expenses.csv'

# --- Predefined categories ---
INCOME_CATEGORIES = ['Salary', 'Freelance', 'Investment']
EXPENSE_CATEGORIES = ['Housing', 'Groceries', 'Travel', 'Entertainment', 'Utilities', 'Health']

# --- Load CSV safely ---
try:
    df = pd.read_csv(CSV_FILE)
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)

    # Ensure 'id' exists and is integer
    if 'id' not in df.columns or df['id'].isnull().any():
        df['id'] = range(1, len(df) + 1)
    df['id'] = df['id'].astype(int)
except FileNotFoundError:
    df = pd.DataFrame(columns=['id', 'Date', 'Amount', 'Type', 'Category', 'Note'])

df.set_index('id', inplace=True)


def save_data():
    df.reset_index().to_csv(CSV_FILE, index=False)


def get_next_id():
    """Return the smallest available ID, reusing deleted ones."""
    existing_ids = set(df.index)
    new_id = 1
    while new_id in existing_ids:
        new_id += 1
    return new_id


@app.route('/', methods=['GET', 'POST'])
def index():
    global df

    if request.method == 'POST':
        new_id = get_next_id()
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        amount = float(request.form['amount'])
        type_ = request.form['type']
        category = request.form['category']
        note = request.form['note']

        new_row = pd.DataFrame([{
            'id': new_id, 'Date': date, 'Amount': amount,
            'Type': type_, 'Category': category, 'Note': note
        }]).set_index('id')

        df = pd.concat([df, new_row])
        save_data()
        return redirect(url_for('index'))

    income = df[df['Type'] == 'Income']['Amount'].sum()
    expenses = df[df['Type'] == 'Expense']['Amount'].sum()
    total = income - expenses
    latest = df.sort_values(by='Date', ascending=False).head(10)

    return render_template(
        'index.html',
        data=latest,
        income=income,
        expenses=expenses,
        total=total,
        income_categories=INCOME_CATEGORIES,
        expense_categories=EXPENSE_CATEGORIES
    )


@app.route('/delete/<int:id>')
def delete_expense(id):
    global df
    if id in df.index:
        df.drop(id, inplace=True)
        save_data()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
