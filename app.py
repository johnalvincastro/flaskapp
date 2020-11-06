from flask import Flask, render_template, request, redirect, flash, url_for, session, g
from flask_bootstrap import Bootstrap
from flask_mysqldb import MySQL
import yaml

app = Flask(__name__)
app.secret_key = 'hush'
Bootstrap(app)

# Config DB
db = yaml.load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)

# adding data into databse INSERT A USER
# @app.route('/add_user', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         # Fetch form data
#         userDetails = request.form
#         name = userDetails['name']
#         email = userDetails['email']
#         cur = mysql.connection.cursor()
#         cur.execute("INSERT INTO users(name, email) VALUES(%s, %s)", (name, email))
#         mysql.connection.commit()
#         cur.close()
#         return 'success'

#     return render_template('index.html')

# GET added list of USERS - modify to obtain list of users
# @app.route('/users')
# def users():
#        cur = mysql.connection.cursor()
#        resultValue = cur.execute("SELECT * FROM users")
#        if resultValue > 0:
#         userDetails = cur.fetchall()
#         return render_template('users.html', userDetails=userDetails)


@app.route('/')
def mainpg():
    return render_template('index.html')


@app.route('/user_login')
def my_form():
    return render_template('login_form.html')


# User login check
@app.route('/dashboard', methods=['POST'])
def authenticateStaff():

    # Fetch staff data from database
    username = request.form['username']  # username = wsId of staffWorksFor
    password = request.form['password']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM staffWorksFor WHERE wsId='" +
                username + "' and password='" + password + "'")
    data = cur.fetchone()  # user data from the database - returns a tuple
    print(data)  # logs data retrieved into the console
    cur2 = mysql.connection.cursor()
    cur2
    cur2.execute(
        "SELECT position FROM staff_Position P JOIN staffWorksFor S ON (P.wsID = S.wsID) WHERE S.wsID='"+username+"' ")
    pos = cur2.fetchone()
    print(pos)

    if data is None:
        return "Username or password is wrong"
    else:
        # return "Logged in successfully as user ID " + username
        # return render_template('user_dash.html', username = username)
        return render_template('user_dash.html', data=data, pos=pos)


@app.route('/addPatient', methods=['POST'])
def admit():
    if request.method == 'POST':
        # Fetch form data
        patientDetails = request.form
        pid = patientDetails['patientID']
        dateofBirth = patientDetails['patientDOB']
        name = patientDetails['patientName']
        password = patientDetails['patientPW']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO Patient(pid, dateofBirth, name, password) VALUES(%s, %s, %s, %s)",
                    (pid, dateofBirth, name, password))
        mysql.connection.commit()
        cur.close()
        # return 'success'
        flash("Patient Added")
        return render_template('user_dash.html')

    return redirect(url_for('authenticateStaff'))


@app.route('/newVisit', methods=['POST'])
def createVisit():
    if request.method == 'POST':
        # Fetch form data
        patientDetails = request.form
        visitID = patientDetails['visitID']
        patientID = patientDetails['patientID']
        illness = patientDetails['illness']
        admitDate = patientDetails['admitDate']
        disDate = '2999-12-30'
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO visit(visitID, pid, illness, adDate, disDate) VALUES(%s, %s, %s, %s,%s)",
                    (visitID, patientID, illness, admitDate, disDate))
        mysql.connection.commit()
        cur.close()
        # return 'success'
        flash("New Visit")
        return render_template('user_dash.html')

    return redirect(url_for('authenticateStaff'))


# GET added list of patients
@app.route('/getPatientData')
def patients():
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM patient")
    if resultValue > 0:
        patientData = cur.fetchall()
        print(patientData)
        return render_template('user_dash.html', patientData = patientData)


if __name__ == '__main__':
    app.run(debug=True)
