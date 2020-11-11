from flask import Flask, render_template, request, redirect, flash, url_for, session, g
from flask_bootstrap import Bootstrap
from flask_mysqldb import MySQL
import yaml
import datetime

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
# basic template for inspiration do not uncomment for the app
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


# User login check for staffSELEC
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
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO visit(visitID, pid, illness, adDate, disDate) VALUES(%s, %s, %s, %s, NULL)",
                    (visitID, patientID, illness, admitDate))
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
        return render_template('user_dash.html', patientData=patientData)

# Section for patient sign in
@app.route('/patient_login')
def patient_form():
    return render_template('patient_login_form.html')


# User login check for staff
@app.route('/patientdash', methods=['POST'])
def authenticatePatient():

    # Fetch staff data from database
    patientID = request.form['patID']  # username = patID
    patientPW = request.form['patPW']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Patient WHERE pid='" +
                patientID + "' and password='" + patientPW + "'")
    data = cur.fetchone()  # user data from the database - returns a tuple
    print(data)  # logs data retrieved into the console
    mysql.connection.commit()
    cur.close()
    # Fetch visit details
    cur2 = mysql.connection.cursor()
    cur2.execute(
        "SELECT * FROM visit WHERE pid='" + patientID + "'")
    visit = cur2.fetchall()
    print(visit)
    mysql.connection.commit()
    cur2.close()
  # Fetch visit details
    cur3 = mysql.connection.cursor()
    cur3.execute(
        "SELECT T.rxId, name, prescribeDate, expireDate FROM Medicine M JOIN takesMedicine T ON (M.rxid = T.rxId) WHERE patientId='" + patientID + "'")
    myrx = cur3.fetchall()
    print(myrx)
    mysql.connection.commit()
    cur3.close()
    if data is None:
        return "Username or password is wrong"
    else:
        # return "Logged in successfully as user ID " + username
        return render_template('patient_dash.html', data=data, visit=visit, myrx=myrx)

# NEW Rx to patient
@app.route('/newRx', methods=['POST'])
def createNewRx():
    if request.method == 'POST':
        # Fetch form data
        rxForm = request.form
        pid = rxForm['rxToPid']
        rx = rxForm['rxID']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO takesMedicine(rxId,patientId) VALUES(%s, %s)",
                    (rx, pid))
        mysql.connection.commit()
        cur.close()
        # return 'success'
        flash("Rx Added")
        return render_template('user_dash.html')

    return redirect(url_for('authenticateStaff'))

# Discharge patient
@app.route('/disch', methods=['POST'])
def dischargePatient():
    if request.method == 'POST':
        # Fetch form data
        dischg = request.form
        pid = dischg['pidDisch']
        disDate = dischg['disDate']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE visit SET disDate= %s WHERE pid = %s",
                    (disDate, pid))
        mysql.connection.commit()
        cur.close()
        # return 'success'
        flash("Patient Discharged")
        return render_template('user_dash.html')

    return redirect(url_for('authenticateStaff'))


@app.route('/em_login')
def equip_form():
    return render_template('eqmanager_login_form.html')

# User login check for staff


@app.route('/em_dash', methods=['POST'])
def authenticateEM():

    # Fetch staff data from database
    username = request.form['emName']
    password = request.form['empw']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM equipmentManager WHERE id='" +
                username + "' and password='" + password + "'")
    emData = cur.fetchone()  # user data from the database - returns a tuple
    print(emData)  # logs data retrieved into the console
    if emData is None:
        return "Username or password is wrong"
    else:
        return render_template('eqdash.html', emData=emData)

# NEW equiment to equipmentType


@app.route('/addEquipment', methods=['POST'])
def addEquip():
    if request.method == 'POST':
        # Fetch form data
        addEq = request.form
        eqid = addEq['eid']
        eqtype = addEq['etype']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO patientCareEquipment(id,type) VALUES(%s, %s)",
                    (eqid, eqtype))
        mysql.connection.commit()
        cur.close()
        flash("Added Equipment")
        return render_template('eqdash.html')

    return redirect(url_for('authenticateEm'))


@app.route('/getEqs')
def getEquip():
    # Fetch equipment details
    cur2 = mysql.connection.cursor()
    resultValue = cur2.execute("SELECT * FROM patientCareEquipment")
    if resultValue > 0:
        equips = cur2.fetchall()
        print(equips)
        mysql.connection.commit()
        cur2.close()
        return render_template('eqdash.html', equips=equips)
    else: 
        flash("Equipment List Empty")
        return render_template('eqdash.html')


@app.route('/removeEq', methods=['POST'])
def removeEquip():
    deleteEq = request.form
    eqid = deleteEq['equipID']
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM patientCareEquipment WHERE id = '" + eqid + "'")
    mysql.connection.commit()
    cur.close()
    flash("Equipment Deleted")
    return render_template('eqdash.html')

# CODE FOR ADMIN BELOW

@app.route('/admin_login')
def admin_form():
    return render_template('admin_login_form.html')

# Admin Login check credentials
@app.route('/admin_dashboard', methods=['POST'])
def authenticateAdmin():

    # fetch admin data from database
    username = request.form['username']
    password = request.form['password']
    cur = mysql.connection.cursor()
    cur.execute("SELECT* FROM administrator WHERE adminId ='" + username
    + "' and password = '" + password + "'" )
    
    data = cur.fetchone() #user data from the database  -retures a tuple
    cur2 = mysql.connection.cursor()
    cur2.execute("SELECT * FROM manages WHERE adminId = '"+ username +"'")
    hospitalID = cur2.fetchone()
    print(hospitalID)

    # viewing what the admins see

    if data is None:
        return "Username or password is wrong"
    else:
        return render_template('admin_dash.html', data=data, hospitalID=hospitalID )



@app.route('/addStaff', methods=['POST'])
def newstaff():
    if request.method == 'POST':
        #Fetch form data
        N_staff = request.form
        wsid = N_staff['StaffID']
        name = N_staff['StaffName']
        hospitalID = N_staff['HospID']
        password = N_staff['StaffPW']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO staffWorksFor(wsid, name, hospitalID, password) VALUES(%s, %s, %s, %s)",
                    (wsid, name, hospitalID, password))
        mysql.connection.commit()           
        cur.close()
        
       # return 'success'
    
        flash("Staff Added")
        return render_template('admin_dash.html')

    return redirect(url_for('authenticateAdmin'))


@app.route('/deleteStaff',methods=['POST'])
def deletestaff():
        #fetch from data
        D_Staff=request.form
        wsid = D_Staff["StaffID"]
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM staffWorksFor WHERE wsid='"+ wsid +"'")
        mysql.connection.commit()
        cur.close()
        flash("Staff deleted")
        return render_template('admin_dash.html')

@app.route('/adminview')
def adminv():
    #fetch from data
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM visit")
    patient = cur.fetchall()
    print(patient)
    return render_template('admin_dash.html', patient=patient)



if __name__ == '__main__':
    app.run(debug=True)
