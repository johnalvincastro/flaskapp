from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from flask_mysqldb import MySQL 
import yaml
 
app = Flask(__name__)
Bootstrap(app)

#Config DB
db = yaml.load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)

#adding data into databse INSERT A USER
@app.route('/add_user', methods=['GET', 'POST']) 
def index():
    if request.method == 'POST':
        # Fetch form data
        userDetails = request.form
        name = userDetails['name']
        email = userDetails['email']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(name, email) VALUES(%s, %s)", (name, email))
        mysql.connection.commit()
        cur.close()
        return 'success'

    return render_template('index.html')

#GET added list of USERS
@app.route('/users')
def users():
       cur = mysql.connection.cursor()
       resultValue = cur.execute("SELECT * FROM users")
       if resultValue > 0:
        userDetails = cur.fetchall()
        return render_template('users.html', userDetails=userDetails)

@app.route('/user_login')
def my_form():
        return render_template('login_form.html')


#User login check
@app.route('/user_login', methods=['POST']) 
def authenticateStaff():
    # Fetch staff data from database 
    username = request.form['username'] #username = wsId of staffWorksFor
    password = request.form['password']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM staffWorksFor WHERE wsId='" + username +"' and password='" + password + "'")
    data = cur.fetchone()
    print(data) #logs data retrieved into the console
    if data is None:
        return "Username or password is wrong"
    else:
        return "Logged in successfully as user ID " + username

if __name__ == '__main__':
    app.run(debug=True) 
