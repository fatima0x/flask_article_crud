📝 Flask CRUD Blog App

A simple Flask web application that performs full CRUD (Create, Read, Update, Delete) operations for managing blog articles.
This project demonstrates how to connect Flask with a MySQL database, handle dynamic routes, and render data using Jinja templates.

🚀 Features

Add new articles

Edit existing articles

Delete articles

View all articles from MySQL database

View a single article page dynamically

User-friendly dashboard interface

🛠️ Tech Stack

Backend: Flask (Python)

Database: MySQL

Frontend: HTML, CSS, Bootstrap

Templating Engine: Jinja2

⚙️ Installation & Setup

Clone the repository

git clone https://github.com/fatima.0x/flask_crud_app.git
cd flask-crud-app


*Create a virtual environment*

python -m venv venv
venv\Scripts\activate


Install dependencies

pip install -r requirements.txt


Configure MySQL

Create a database named myflaskapp

Update your database credentials in app.py:

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'yourpassword'
app.config['MYSQL_DB'] = 'myflaskapp'


Run the application

python app.py


Visit in browser

http://127.0.0.1:5000/
