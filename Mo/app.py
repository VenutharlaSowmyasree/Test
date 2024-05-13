from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import requests
from uuid import UUID
app = Flask(__name__)

# MySQL Configuration
mysql_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'Sony@123',
    'database': 'student_database'
}
brewery_by_city_url = 'https://api.openbrewerydb.org/v1/breweries?by_city={}'
brewery_by_name_url = 'https://api.openbrewerydb.org/v1/breweries?by_name={}'
brewery_by_type_url = 'https://api.openbrewerydb.org/v1/breweries?by_type={}'
def fetch_review(brewery_name):
    try:
        # Connect to the database
        con = mysql.connector.connect(**mysql_config)
        cur = con.cursor()

        # Execute SQL query to fetch rating and description for the given brewery name
        cur.execute("SELECT rating, description FROM reviews WHERE brewery_name = %s", (brewery_name,))
        review = cur.fetchone()

        if review:
            rating, description = review
            return rating, description  # Return the rating and description if found
        else:
            return "N/A", "N/A"  # Return "N/A" for both rating and description if no review found for the brewery
    except mysql.connector.Error as err:
        print("Error fetching review:", err)
        return "N/A", "N/A"  # Return "N/A" for both rating and description in case of error
    finally:
        cur.close()
        con.close()
@app.route('/')
def index():
     return redirect(url_for('signup'))
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        con = mysql.connector.connect(**mysql_config)
        cur = con.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        con.commit()
        cur.close()
        con.close()
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        con = mysql.connector.connect(**mysql_config)
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()  # Fetch one row
        
        # cur.close()  # Close cursor after fetching
        
        con.close()
        
        if user:
            return redirect(url_for('home'))  # Redirect to home page after login
        else:
            return "Invalid username or password."
    return render_template('login.html')  # Render login form template
@app.route('/home')
def home():
    return render_template('home.html')
@app.route('/brewery-search', methods=['GET', 'POST'])
def brewery_search():
    if request.method == 'POST':
        search_query = request.form['search_query']
        search_type = request.form['search_type']   
        if search_type == 'by_city':
            response = requests.get(brewery_by_city_url.format(search_query))
        elif search_type == 'by_name':
            response = requests.get(brewery_by_name_url.format(search_query))
        elif search_type == 'by_type':
            response = requests.get(brewery_by_type_url.format(search_query))
        
        if response.status_code == 200:
            breweries = response.json()
            
            # Fetch rating for each brewery from the database
            for brewery in breweries:
                brewery_name = brewery['name']
                rating, description = fetch_review(brewery_name)  # Fetch rating and description for the brewery
                brewery['rating'] = rating
                brewery['description'] = description  # Assuming 'name' is the key for brewery name
            
            
            return render_template('brewery_search.html', breweries=breweries)
        else:
            return "Error: Unable to fetch brewery data."
    return render_template('brewery_search.html')
@app.route('/review')
def review():
    return render_template('brewery_rating.html')
from flask import redirect, url_for

@app.route('/add-review', methods=['POST'])
def add_review():
    if request.method == 'POST':
        brewery_name = request.form['brewery_name']
        rating = request.form['rating']
        description = request.form['description']
        
        # Connect to the database
        con = mysql.connector.connect(**mysql_config)
        cur = con.cursor()
        
        # Check if a review with the same brewery name already exists
        cur.execute("SELECT * FROM reviews WHERE brewery_name = %s", (brewery_name,))
        existing_review = cur.fetchone()
        
        if existing_review:
            # If a review with the same brewery name exists, update it
            try:
                cur.execute("UPDATE reviews SET rating = %s, description = %s WHERE brewery_name = %s", (rating, description, brewery_name))
                con.commit()
                return redirect(url_for('home'))  # Redirect to home page after updating review
            except mysql.connector.Error as err:
                print("Error updating review:", err)
            finally:
                cur.close()
                con.close()
        else:
            # If no review with the same brewery name exists, insert a new one
            try:
                cur.execute("INSERT INTO reviews (brewery_name, rating, description) VALUES (%s, %s, %s)", (brewery_name, rating, description))
                con.commit()
                return redirect(url_for('home'))  # Redirect to home page after adding review
            except mysql.connector.Error as err:
                print("Error inserting review:", err)
            finally:
                cur.close()
                con.close()
    
    # If the request method is not POST or if an error occurs, redirect to the review page
    return redirect(url_for('review'))
if __name__ == '__main__':
    app.run(debug=True)
