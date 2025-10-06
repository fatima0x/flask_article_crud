from flask import Flask, request,render_template,flash,redirect,url_for,session,logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
#from data import Articles

app= Flask(__name__)

#Articles= Articles()
app.secret_key='secret123'
#config mysql
app.config['MYSQL_HOST']='localhost'

app.config['MYSQL_USER']='flaskuser'
app.config['MYSQL_PASSWORD']='flaskpass'
app.config['MYSQL_DB']='myflaskapp'
app.config['MYSQL_CURSORCLASS']='DictCursor'

#init mysql
mysql= MySQL(app)


#@app.route('/testdb')
##detestdb():
    #try:
     #   cur = mysql.connection.cursor()
      #  cur.execute("SELECT DATABASE();")   # check which DB we’re connected to
       # db_name = cur.fetchone()
        #return f"Connected successfully to database: {db_name}"
    #except Exception as e:
     #   return f"Database connection failed: {str(e)}"

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

#articles route
@app.route('/articles')
def articles():
    # create cursor 
    cur= mysql.connection.cursor()
    result= cur.execute("SELECT * FROM articles")
    articles= cur.fetchall()
    if result>0:
        return render_template('articles.html', articles=articles)
    else:
        msg= 'No Articles Found'
        return render_template('articles.html', msg=msg)
    cur.close()

#Single page article
@app.route('/article/<string:id>/')
def article(id):
    cur= mysql.connection.cursor()
    
    result= cur.execute("SELECT * FROM articles WHERE id= %s", [id])
    
    article= cur.fetchone()
    return render_template('article.html', article=article)



#Register Form Class

class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

#User register route
@app.route('/register', methods=['GET', 'POST'])
def register():
        form = RegisterForm(request.form)
        if request.method == 'POST' and form.validate():
            name = form.name.data
            email = form.email.data
            username = form.username.data
            password = sha256_crypt.encrypt(str(form.password.data))
            #create cursor
            cur= mysql.connection.cursor()
            cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))
            #commit the db
            mysql.connection.commit()
            cur.close()
            flash('You are now registered and can log in', 'success')
            return redirect(url_for('login'))
        
            
        return render_template('register.html', form=form)
    
#login route
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username= request.form['username']
        password_candidate= request.form['password']
        
        #create cursor
        cur= mysql.connection.cursor()
        result= cur.execute("SELECT * FROM users WHERE username= %s", [username])
        if result>0:
            data= cur.fetchone()
            password= data['password']
            
            if sha256_crypt.verify(password_candidate, password):
                session['logged_in']= True
                session['username']= username
                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error= 'Invalid login'
                return render_template('login.html', error=error)
            #close the connection
            cur.close()
            
        else:
            error= 'Username not found'
            return render_template('login.html', error=error)
    return render_template('login.html')

#Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

#Logout route
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


#Dashboard route
@app.route('/dashboard')
@is_logged_in
def dashboard():
    # create cursor 
    cur= mysql.connection.cursor()
    result= cur.execute("SELECT * FROM articles")
    articles= cur.fetchall()
    if result>0:
        return render_template('dashboard.html', articles=articles)
    else:
        msg= 'No Articles Found'
        return render_template('dashboard.html', msg=msg)
    cur.close()
    


    
    
#Article form class
class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=200)])
    body = TextAreaField('Body', [validators.Length(min=30)])

# Add Article
@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data
        
        #create cursor
        cur= mysql.connection.cursor()
        cur.execute("INSERT INTO articles(title, body, author) VALUES(%s, %s, %s)", (title, body, session['username']))
        #commit the db
        mysql.connection.commit()
        cur.close()
        flash('Article Created', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('add_article.html', form=form)


#Edit Article
@app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_article(id):
    #create cursor
    cur= mysql.connection.cursor()
    result= cur.execute("SELECT * FROM articles WHERE id= %s", [id])
    article= cur.fetchone()
    #Get form
    form = ArticleForm(request.form)
    
    #populate article form fields
    form.title.data= article['title']
    form.body.data= article['body']
    if request.method == 'POST' and form.validate():
        title = request.form['title']
        body = request.form['body']
        
        #create cursor
        cur= mysql.connection.cursor()
        cur.execute("UPDATE articles SET title=%s, body=%s WHERE id= %s", (title, body, id))
        #commit the db
        mysql.connection.commit()
        cur.close()
        flash('Article Updated', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('edit_article.html', form=form)


#Delete Article
@app.route('/delete_article/<string:id>', methods=['POST'])
@is_logged_in
def delete_article(id):
    #create cursor
    cur= mysql.connection.cursor()
    cur.execute("DELETE FROM articles WHERE id= %s", [id])
    #commit the db
    mysql.connection.commit()
    cur.close()
    flash('Article Deleted', 'success')
    return redirect(url_for('dashboard'))




    

if __name__ == '__main__':
    app.run(debug=True)