from api import app, dbase, generate_password_hash, cross_origin, CORS, check_password_hash
from flask import request, jsonify
from models import *
from flask_login import login_user, login_required, LoginManager, logout_user
import datetime as dt
import time
from sqlalchemy import and_, desc, extract
import png
import pyqrcode
from datetime import date, datetime, timedelta
import os
import string

lgdate = datetime.now()
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
  return Admin.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
@cross_origin(allow_headers=['Content-Type'])
def login():
  data = request.get_json()
  code = str(data['password'])
  user = Admin.query.filter_by(username=data['username']).first()
  if user is None:
    return jsonify({'message': 'Invalid username or password'})
  else:
    if check_password_hash(user.password, code):
      login_user(user, remember=True)
      print(login_user(user, remember=True))
      msg = "Logged in"
      logmessage = Logs(details=msg, log_date=lgdate)
      dbase.session.add(logmessage)
      dbase.session.commit()
      return jsonify({'message': 'Login Successful!'})
  return jsonify({'message': 'invalid password'})


@app.route('/logout', methods=['GET'])
@cross_origin(allow_headers=['Content-Type'])
@login_required
def logout():
  msg = "Logged out"
  logmessage = Logs(details=msg, log_date=lgdate)
  dbase.session.add(logmessage)
  dbase.session.commit()
  logout_user()
  return jsonify({'message': 'Logged out'})


@app.route('/newAdmin', methods=['POST'])
@cross_origin(allow_headers=['Content-Type'])
@login_required
def newAdmin():
    data = request.get_json()
    new = Admin.query.get(1)
    try:
        if data['username'] == '' or data['username'] is None:
          new.username = new.username
        else:
          new.username = data['username']
        if data['password'] == '':
          new.password = new.password
        else:
          new.password = generate_password_hash(data['password'], method='sha256')
        dbase.session.commit()
        msg = "username or password updated"
        logmessage = Logs(details=msg, log_date=lgdate)
        dbase.session.add(logmessage)
        dbase.session.commit()
        return jsonify({'message': 'successfull!'})
    except:
        return jsonify({'message': 'edit failed'})


@app.route('/newEmployee', methods=['POST'])
@login_required
@cross_origin(allow_headers=['Content-Type'])
def addemployee():
    data = request.get_json()
    now = datetime.now().strftime("%m%d%Y%H%M")
    # birth_date = Strip the time!!!!!!!!
    # birthdate = datetime.datetime.strptime(data['birth_date'], '%Y-%M-%d')
    new_employee = Employee(fname=data['fname'], mname=data['mname'], lname=data['lname'], position=data['position'],
                            code=data['code'], contact=data['contact'], email=data['email'],
                            birth_date=data['birth_date'],  gender=data['gender'], address=data['address'], employeestatus=1)

    #search for employee using QRCODE
    employee = Employee.query.filter_by(code=data['code']).first()
    if employee is None:
        print now
        dbase.session.add(new_employee)
        dbase.session.commit()
        msg = data['code'] + " employee added"
        logmessage = Logs(details=msg, log_date=lgdate)
        dbase.session.add(logmessage)
        dbase.session.commit()
        return jsonify({'message': 'New employee created!'})

    else:
        return jsonify({'message': 'Employee already created'})


@app.route('/view/', methods=['GET'])
@login_required
@cross_origin('*')
def viewEmployee():
    employess = Employee.query.filter_by(employeestatus=1).all()

    data = []
    if employess:
        for i in employess:
          data1 = {}
          data1['fname'] = i.fname
          data1['mname'] = i.mname
          data1['lname'] = i.lname
          data1['position'] = i.position
          data1['code'] = i.code
          data1['employeeid'] = i.employeeid
          data1['contact'] = i.contact
          data1['email'] = i.email
          data1['birth_date'] = str(i.birth_date)
          data1['gender'] = i.gender
          data1['address'] = i.address
          data1['late'] = i.late
          data1['absent'] = i.absent
          data1['overtime'] = i.overtimes
          data.append(data1)
        return jsonify({'users': data})
    else:
        return jsonify({'users': data})


@app.route('/viewOne/', methods=['GET', 'POST'])
@login_required
@cross_origin('*')
def viewOneEmployee():
    data = request.get_json()
    employess = Employee.query.filter_by(employeeid=data['id']).first()

    if employess:
          data1 = {}
          data1['lname'] = employess.lname
          data1['fname'] = employess.fname
          data1['mname'] = employess.mname
          data1['position'] = employess.position
          data1['code'] = employess.code
          data1['employeeid'] = employess.employeeid
          data1['contact'] = employess.contact
          data1['email'] = employess.email
          data1['birth_date'] = str(employess.birth_date)
          data1['gender'] = employess.gender
          data1['address'] = employess.address
          data1['late'] = employess.late
          data1['absent'] = employess.absent
          data1['overtime'] = employess.overtimes
          return jsonify({'users': data1})
    else:
        return jsonify({'message': 'no employee found'})


@app.route('/absentandlate/total', methods=['GET'])
def view_total():
  total = Employee.query.all()
  totaldata = []
  if not total:
     return jsonify({'total_data': totaldata})
  else:

     for i in total:
        data = {}
        data['name'] = i.fname + " " + i.mname + " " + i.lname
        data['late_total'] = i.late
        data['absent_total'] = i.absent
        data['overtime_total'] = i.overtimes
        totaldata.append(data)
     return jsonify({'total_data': totaldata})


@app.route('/viewDeactivated/', methods=['GET', 'POST'])
@login_required
@cross_origin('*')
def viewEmployeeDeactivated():
    employess = Employee.query.filter_by(employeestatus=0).all()

    data = []
    if employess:
        for i in employess:
            data1 = {}
            data1['fname'] = i.fname
            data1['mname'] = i.mname
            data1['lname'] = i.lname
            data1['position'] = i.position
            data1['code'] = i.code
            data1['employeeid'] = i.employeeid
            data1['contact'] = i.contact
            data1['email'] = i.email
            data1['birth_date'] = str(i.birth_date)
            data1['gender'] = i.gender
            data1['address'] = i.address
            data.append(data1)
        return jsonify({'users': data})
    else:
        return jsonify({'users': data})


@app.route('/search/', methods=['GET', 'POST'])
@login_required
@cross_origin('*')
def searchEmployee():
    data = request.get_json()
    employee1 = data['lname']
    notactive = []
    activate = Employee.query.filter(
        and_(Employee.lname == employee1, Employee.employeestatus == 0)).all()

    if activate is None:
        return jsonify({'message': 'not found'})
    else:
        for i in activate:
            data = {}
            data['fname'] = i.fname
            data['mname'] = i.mname
            data['lname'] = i.lname
            data['position'] = i.position
            data['code'] = i.code
            data['contact'] = i.contact
            data['email'] = i.email
            data['birth_date'] = str(i.birth_date)
            data['gender'] = i.gender
            data['address'] = i.address
            notactive.append(data)
        return jsonify({'message': notactive})


@app.route('/generate/qrcode', methods=['POST'])
@cross_origin('*')
@login_required
def genereate_code():
    data = request.get_json()
    qr = pyqrcode.create(data['code'])
    qr.png('code.png', scale=6)
    msg = "generate new code: " + data['code']
    logmessage = Logs(details=msg, log_date=lgdate)
    dbase.session.add(logmessage)
    dbase.session.commit()
    return jsonify({'message': 'QR Code Generated!'})


@app.route('/deactivate', methods=['GET', 'POST'])
@cross_origin('*')
@login_required
def delEmployee():

    data = request.get_json()
    #search for employee using QRCODE and if the employee is active
    employee = Employee.query.filter(
        and_(Employee.code == data['code'], Employee.employeestatus == 1)).first()
    # employee = Employee.query.filter_by(code=data['code']).first()
    if employee:
      # 1 for active
      # 0 for inactive
      #change the status to 0
      employee.employeestatus = 0
      dbase.session.add(employee)
      dbase.session.commit()
      msg = data['code'] + " deactivated"
      logmessage = Logs(details=msg, log_date=lgdate)
      dbase.session.add(logmessage)
      dbase.session.commit()
      return jsonify({'message': 'Employee deactivated'})
    else:
        return jsonify({'message': 'Employee is not found'})


@app.route('/activate', methods=['GET', 'POST'])
@cross_origin('*')
@login_required
def ReActEmployee():

    data = request.get_json()
    #search for employee using QRCODE and if the employee is active
    employee = Employee.query.filter(
        and_(Employee.code == data['code'], Employee.employeestatus == 0)).first()
    # employee = Employee.query.filter_by(code=data['code']).first()
    if employee:
        # 1 for active
        # 0 for inactive
        #change the status to 0
        employee.employeestatus = 1
        dbase.session.add(employee)
        dbase.session.commit()
        msg = data['code'] + " activated"
        logmessage = Logs(details=msg, log_date=lgdate)
        dbase.session.add(logmessage)
        dbase.session.commit()
        return jsonify({'message': 'Employee Activated'})
    else:
        return jsonify({'message': 'Employee is not found'})


@app.route('/edit/<string:user_id>', methods=['POST'])
@cross_origin(allow_headers=['Content-Type'])
@login_required
def edit(user_id):
    data = request.get_json()
    employee = Employee.query.filter_by(employeeid=user_id).first()
    if employee is None:
        return jsonify({'message': 'user not found'})
    else:
        try:
            # Check if the jsondata is empty, can be done here or front end.
            if data['fname'] == '' or data['fname'] is None:
                employee.fname = employee.fname
            else:
                employee.fname = data['fname']
            if data['mname'] == '':
                employee.mname = employee.mname
            else:
                employee.mname = data['mname']
            if data['lname'] == '':
                employee.lname = employee.lname
            else:
                employee.lname = data['lname']
            if data['position'] == '':
                employee.position = employee.position
            else:
                employee.position = data['position']
            if data['code'] == '':
                employee.code = employee.code
            else:
                employee.code = data['code']
            if data['contact'] == '':
                employee.contact = employee.contact
            else:
                employee.contact = data['contact']
            if data['email'] == '':
                employee.email = employee.email
            else:
                employee.email = data['email']
            if data['birth_date'] == '':
                employee.birth_date = employee.birth_date
            else:
                employee.birth_date = data['birth_date']
            if data['gender'] == '':
                employee.gender = employee.gender
            else:
                employee.gender = data['gender']
            if data['address'] == '':
                employee.address = employee.address
            else:
                employee.address = data['address']
            dbase.session.commit()
            msg = user_id + " updated"
            logmessage = Logs(details=msg, log_date=lgdate)
            dbase.session.add(logmessage)
            dbase.session.commit()
            return jsonify({'message': 'Success!'})
        except:
            return jsonify({'message': 'edit failed'})


@app.route('/company_summary/monthly/<string:dates>', methods=['GET'])
@cross_origin("*")
@login_required
def company_month(dates):
   dates = datetime.strptime(dates, "%Y-%m-%d")
   summary = Attendance.query.filter(extract('year', Attendance.date) == (dates.strftime("%Y")))\
       .filter(extract('month', Attendance.date) == (dates.strftime("%m"))).all()
   employees = []
   for employee in summary:
       employee_data = {}
       name = Employee.query.filter_by(employeeid=employee.employeeid).first()
       overtimee = Overtime.query.filter_by(employeeid=employee.employeeid).order_by(
           Overtime.overtimeDate.desc()).first()
       employee_data['name'] = name.fname + " " + name.mname + " " + name.lname
       if overtimee is None:
            employee_data['overtimeTotal'] = 0
       else:
            employee_data['overtimeTotal'] = overtimee.overtimeTotal
       employee_data['employeeid'] = employee.employeeid
       employee_data['lateTotal'] = employee.lateTotal
       employee_data['absentTotal'] = employee.absentTotal
       if employee.morningTimeIn is None:
          employee_data['morningTimeIn'] = "None"
       else:
          employee_data['morningTimeIn'] = (employee.morningTimeIn).strftime("%Y-%b-%d %I:%M %p")
       if employee.morningTimeOut is None:
          employee_data['morningTimeOut'] = "None"
       else:
          employee_data['morningTimeOut'] = (employee.morningTimeOut).strftime("%Y-%b-%d %I:%M %p")
       if employee.afterTimeIn is None:
          employee_data['afterTimeIn'] = "None"
       else:
          employee_data['afterTimeIn'] = (employee.afterTimeIn).strftime("%Y-%b-%d %I:%M %p")
       if employee.afterTimeOut is None:
          employee_data['afterTimeOut'] = "None"
       else:
          employee_data['afterTimeOut'] = (employee.afterTimeOut).strftime("%Y-%b-%d %I:%M %p")
       if employee.morningRemark is None:
          employee_data['morningRemark'] = "On time"
       else:
          employee_data['morningRemark'] = employee.morningRemark
       if employee.afterRemark is None:
          employee_data['afterRemark'] = "On time"
       else:
          employee_data['afterRemark'] = employee.afterRemark
       employee_data['morningStatus'] = employee.morningStatus
       employee_data['afterStatus'] = employee.afterStatus
       employee_data['morningDailyStatus'] = employee.morningDailyStatus
       employee_data['afterDailyStatus'] = employee.afterDailyStatus
       if (employee.morningTimeIn is None) and ( employee.morningTimeOut is None):
          employee_data['morningRemark'] = "Absent"
       if (employee.afterTimeIn is None) and (employee.afterTimeOut is None):
          employee_data['afterRemark'] = "Absent"
       employees.append(employee_data)
   return jsonify({'Employee': employees})


@app.route('/company_summary/weekly/<string:sort_date>', methods=['GET'])
@cross_origin("*")
@login_required
def company_week(sort_date):
   dates = string.replace(sort_date, "W", "")
   print dates
   year, week_number = dates.split("-")
   print year
   print week_number
   summary = Attendance.query.filter(Attendance.week_number == week_number).filter(
       extract('year', Attendance.date) == year).order_by(Attendance.week_number.desc()).all()
   employees = []
   if summary is None:
       return jsonify({"message": "No data to show"})
   for employee in summary:
       employee_data = {}
       name = Employee.query.filter_by(employeeid=employee.employeeid).first()
       overtimee = Overtime.query.filter_by(employeeid=employee.employeeid).order_by(
           Overtime.overtimeDate.desc()).first()
       employee_data['name'] = name.fname + " " + name.mname + " " + name.lname
       if overtimee is None:
            employee_data['overtimeTotal'] = 0
       else:
            employee_data['overtimeTotal'] = overtimee.overtimeTotal
       employee_data['employeeid'] = employee.employeeid
       employee_data['lateTotal'] = employee.lateTotal
       employee_data['absentTotal'] = employee.absentTotal
       if employee.morningTimeIn is None:
          employee_data['morningTimeIn'] = "None"
       else:
          employee_data['morningTimeIn'] = (
              employee.morningTimeIn).strftime("%Y-%b-%d %I:%M %p")
       if employee.morningTimeOut is None:
          employee_data['morningTimeOut'] = "None"
       else:
          employee_data['morningTimeOut'] = (
              employee.morningTimeOut).strftime("%Y-%b-%d %I:%M %p")
       if employee.afterTimeIn is None:
          employee_data['afterTimeIn'] = "None"
       else:
          employee_data['afterTimeIn'] = (
              employee.afterTimeIn).strftime("%Y-%b-%d %I:%M %p")
       if employee.afterTimeOut is None:
          employee_data['afterTimeOut'] = "None"
       else:
          employee_data['afterTimeOut'] = (
              employee.afterTimeOut).strftime("%Y-%b-%d %I:%M %p")
       if employee.morningRemark is None:
          employee_data['morningRemark'] = "On time"
       else:
          employee_data['morningRemark'] = employee.morningRemark
       if employee.afterRemark is None:
          employee_data['afterRemark'] = "On time"
       else:
          employee_data['afterRemark'] = employee.afterRemark
       employee_data['morningStatus'] = employee.morningStatus
       employee_data['afterStatus'] = employee.afterStatus
       employee_data['morningDailyStatus'] = employee.morningDailyStatus
       employee_data['afterDailyStatus'] = employee.afterDailyStatus
       if (employee.morningTimeIn is None) and (employee.morningTimeOut is None):
          employee_data['morningRemark'] = "Absent"
       if (employee.afterTimeIn is None) and (employee.afterTimeOut is None):
          employee_data['afterRemark'] = "Absent"
       employees.append(employee_data)
   return jsonify({'Employee': employees})


@app.route('/employee_summary/monthly/<int:emp_id>', methods=['GET'])
@cross_origin("*")
@login_required
def employee_monthly(emp_id):
   summary = Attendance.query.filter(
       Attendance.employeeid == emp_id).order_by(Attendance.date.desc()).all()
   employees = []
   for employee in summary:
       employee_data = {}
       name = Employee.query.filter_by(employeeid=employee.employeeid).first()
       overtimee = Overtime.query.filter_by(employeeid=employee.employeeid).order_by(
           Overtime.overtimeDate.desc()).first()
       employee_data['name'] = name.fname + " " + name.mname + " " + name.lname
       if overtimee is None:
            employee_data['overtimeTotal'] = 0
       else:
            employee_data['overtimeTotal'] = overtimee.overtimeTotal
       employee_data['employeeid'] = employee.employeeid
       employee_data['lateTotal'] = employee.lateTotal
       employee_data['absentTotal'] = employee.absentTotal
       if employee.morningTimeIn is None:
          employee_data['morningTimeIn'] = "None"
       else:
          employee_data['morningTimeIn'] = (employee.morningTimeIn).strftime("%Y-%b-%d %I:%M %p")
       if employee.morningTimeOut is None:
          employee_data['morningTimeOut'] = "None"
       else:
          employee_data['morningTimeOut'] = (employee.morningTimeOut).strftime("%Y-%b-%d %I:%M %p")
       if employee.afterTimeIn is None:
          employee_data['afterTimeIn'] = "None"
       else:
          employee_data['afterTimeIn'] = (employee.afterTimeIn).strftime("%Y-%b-%d %I:%M %p")
       if employee.afterTimeOut is None:
          employee_data['afterTimeOut'] = "None"
       else:
          employee_data['afterTimeOut'] = (employee.afterTimeOut).strftime("%Y-%b-%d %I:%M %p")
       if employee.morningRemark is None:
          employee_data['morningRemark'] = "On time"
       else:
          employee_data['morningRemark'] = employee.morningRemark
       if employee.afterRemark is None:
          employee_data['afterRemark'] = "On time"
       else:
          employee_data['afterRemark'] = employee.afterRemark
       employee_data['morningStatus'] = employee.morningStatus
       employee_data['afterStatus'] = employee.afterStatus
       employee_data['morningDailyStatus'] = employee.morningDailyStatus
       employee_data['afterDailyStatus'] = employee.afterDailyStatus
       if (employee.morningTimeIn is None) and (employee.morningTimeOut is None):
          employee_data['morningRemark'] = "Absent"
       if (employee.afterTimeIn is None) and (employee.afterTimeOut is None):
          employee_data['afterRemark'] = "Absent"
       employees.append(employee_data)
   return jsonify({'employee': employees})


@app.route('/employee_summary/weekly/<string:dates>/<int:emp_id>', methods=['GET'])
@cross_origin("*")
@login_required
def employee_week(dates, emp_id):
   dates = string.replace(dates, "W", "")
   print dates
   year, week_number = dates.split("-")
   print year
   print week_number
   summary = Attendance.query.filter(and_(Attendance.employeeid == emp_id, Attendance.week_number == week_number, extract(
       'year', Attendance.date) == year)).order_by(Attendance.week_number.desc()).all()
   employees = []
   if not summary:
      return jsonify({'employee': employees})
   for employee in summary:
       employee_data = {}
       name = Employee.query.filter_by(employeeid=employee.employeeid).first()
       overtimee = Overtime.query.filter_by(employeeid=employee.employeeid).order_by(
           Overtime.overtimeDate.desc()).first()
       employee_data['name'] = name.fname + " " + name.mname + " " + name.lname
       if overtimee is None:
            employee_data['overtimeTotal'] = 0
       else:
            employee_data['overtimeTotal'] = overtimee.overtimeTotal
       employee_data['employeeid'] = employee.employeeid
       employee_data['lateTotal'] = employee.lateTotal
       employee_data['absentTotal'] = employee.absentTotal
       if employee.morningTimeIn is None:
          employee_data['morningTimeIn'] = "None"
       else:
          employee_data['morningTimeIn'] = (employee.morningTimeIn).strftime("%Y-%b-%d %I:%M %p")
       if employee.morningTimeOut is None:
          employee_data['morningTimeOut'] = "None"
       else:
          employee_data['morningTimeOut'] = (employee.morningTimeOut).strftime("%Y-%b-%d %I:%M %p")
       if employee.afterTimeIn is None:
          employee_data['afterTimeIn'] = "None"
       else:
          employee_data['afterTimeIn'] = (employee.afterTimeIn).strftime("%Y-%b-%d %I:%M %p")
       if employee.afterTimeOut is None: 
          employee_data['afterTimeOut'] = "None"
       else:
          employee_data['afterTimeOut'] = (employee.afterTimeOut).strftime("%Y-%b-%d %I:%M %p")
       if employee.morningRemark is None:
          employee_data['morningRemark'] = "On time"
       else:
          employee_data['morningRemark'] = employee.morningRemark
       if employee.afterRemark is None:
          employee_data['afterRemark'] = "On time"
       else:
          employee_data['afterRemark'] = employee.afterRemark
       employee_data['morningStatus'] = employee.morningStatus
       employee_data['afterStatus'] = employee.afterStatus
       employee_data['morningDailyStatus'] = employee.morningDailyStatus
       employee_data['afterDailyStatus'] = employee.afterDailyStatus
       if (employee.morningTimeIn is None) and (employee.morningTimeOut is None):
          employee_data['morningRemark'] = "Absent"
       if (employee.afterTimeIn is None) and (employee.afterTimeOut is None):
          employee_data['afterRemark'] = "Absent"
       employees.append(employee_data)
   if len(employees) < 1:
        return jsonify({"message": "No data to show"})
   return jsonify({'employee': employees})


@app.route('/edit/login-time', methods=['POST'])
@cross_origin(allow_headers=['Content-Type'])
@login_required
def edit_time():
   data = request.get_json()

   morning1 = dt.datetime.strptime(data['morning_time_in_start'], "%H:%M")
   morning2 = dt.datetime.strptime(data['morning_time_out_start'], "%H:%M")
   morning3 = dt.datetime.strptime(data['morning_time_out_end'], "%H:%M")
   after1 = dt.datetime.strptime(data['afternoon_time_in_start'], "%H:%M")
   after2 = dt.datetime.strptime(data['afternoon_time_out_start'], "%H:%M")
   after3 = dt.datetime.strptime(data['afternoon_time_out_end'], "%H:%M")
   new_time = Admin.query.filter_by(id=1).first()
   if new_time is None:
       return jsonify({'Message': 'Edit failed'})
   else:
       try:
           # new morning log time
           # morning time in start
           if morning1 == '':
               new_time.morning_time_in_start = new_time.morning_time_in_start
           else:
               new_time.morning_time_in_start = morning1
           # morning time out start
           if morning2 == '':
               new_time.morning_time_out_start = new_time.morning_time_out_start
           else:
               new_time.morning_time_out_start = morning2
           # morning time out end
           if morning3 == '':
               new_time.morning_time_out_end = new_time.morning_time_out_end
           else:
               new_time.morning_time_out_end = morning3
           # new afternoon log time
           # afternoon time in start
           if after1 == '':
               new_time.afternoon_time_in_start = new_time.afternoon_time_in_start
           else:
               new_time.afternoon_time_in_start = after1
           # afternoon time out start
           if after2 == '':
               new_time.afternoon_time_out_start = new_time.afternoon_time_out_start
           else:
               new_time.afternoon_time_out_start = after2
           # afternoon time out end
           if after3 == '':
               new_time.afternoon_time_out_end = new_time.afternoon_time_out_end
           else:
               new_time.afternoon_time_out_end = after3
           dbase.session.commit()
           msg = "timein or timeout edited"
           logmessage = Logs(details=msg, log_date=lgdate)
           dbase.session.add(logmessage)
           dbase.session.commit()
           return jsonify({'message': 'Success!'})
       except:
           return jsonify({'message': 'failed'})


@app.route('/TimeIn/', methods=['POST'])
def timein():
   now = datetime.now().strftime("%m%d%Y%H%M")
   datenow1 = datetime.now().strftime("%m%d%Y")
   datenow3 = datetime.now().strftime("%Y-%m-%d")
   y, m, d = datenow3.split("-")
   datenow2 = dt.date(int(y), int(m), int(d))
   datenow = datetime.strptime(str(datenow1), "%m%d%Y")
   week_no = datetime.strptime(str(datenow1), "%m%d%Y").isocalendar()[1]
   timeAdmin = Admin.query.get(1)

   morning7 = timeAdmin.morning_time_in_start.strftime("%H%M")
   morning9 = timeAdmin.morning_time_out_start.strftime("%H%M")
   morning12 = timeAdmin.morning_time_out_end.strftime("%H%M")
   afte1 = timeAdmin.afternoon_time_in_start.strftime("%H%M")
   afte6 = timeAdmin.afternoon_time_out_start.strftime("%H%M")
   afte7 = timeAdmin.afternoon_time_out_end.strftime("%H%M")

   m7 = ''.join([datenow1, morning7])
   m9 = ''.join([datenow1, morning9])
   m12 = ''.join([datenow1, morning12])
   o10 = ''.join([datenow1, "2200"])

   a1 = ''.join([datenow1, afte1])
   a6 = ''.join([datenow1, afte6])
   a7 = ''.join([datenow1, afte7])

   # 1 for active and 0 for inactive
   data = request.get_json()
   employee = Employee.query.filter(
       and_(Employee.code == data['code'], Employee.employeestatus == 1)).first()
   if not employee:
      return jsonify({'message': 'user not found'})
   empID = employee.employeeid
   attendancenNew = Attendance(employeeid=empID)
   PersonalTimeIN = PersonalTime.query.filter(and_(PersonalTime.employeeid == empID, PersonalTime.date == str(
       datenow))).order_by(PersonalTime.date.desc()).first()

   if employee is None:
      return jsonify({'message': 'user not found'})
   else:
      if PersonalTimeIN is None:

         atts = Attendance.query.filter(and_(Attendance.employeeid == empID, Attendance.date == str(
             datenow))).order_by(Attendance.date.desc()).first()
         # ////////////////////////////IF ID IS NOT LISTED IN THE ATTENDACE CRETAE NEW///////////////////////////////#
         if atts is None:

               dbase.session.add(attendancenNew)
               dbase.session.commit()

               atts = Attendance.query.filter_by(
                   employeeid=empID).order_by(Attendance.date.desc()).first()
               print atts
               print '1st'
               atts.date = datenow
               atts.week_number = week_no
               dbase.session.commit()
               employee1 = Overtime.query.filter(and_(
                   Overtime.employeeid == empID, Overtime.overtimeStatus == 1, Overtime.overtimeDate == datenow2)).first()
               dates = Attendance.query.filter_by(date=datenow).first()
               if dates:
                  print '444546456646546465465465464654654654654'

               else:
                  dbase.session.add(attendancenNew)
                  dbase.session.commit()
                  print '0987654321=-098765'

               # nowdate = atts.date
               if (now >= m7) and (now <= m9):
                  if atts.morningStatus == 0 and atts.afterStatus == 0:
                     if atts.morningTimeOut is None:
                           atts.morningStatus = 1
                           atts.morningTimeIn = datetime.now()
                           atts.morningDailyStatus = 'not late'
                           print "aaaaaaa"
                           dbase.session.commit()
                           return jsonify({'message': 'not late'})
                     else:
                           print 'bbbbbbbbbbbbbbbbbbbbbbb'
                           return jsonify({'message': 'you cannot time in twice'})
                  elif atts.morningStatus == 1 and atts.afterStatus == 0:
                     print 'ccccccccc'
                     return jsonify({'message': 'no time out at this time'})
                  elif atts.morningStatus == 0 and atts.afterStatus == 1:
                     if atts.morningTimeOut is None:
                           atts.afterStatus = 0
                           atts.morningStatus = 1
                           atts.afterTimeOut = datetime.now()
                           atts.morningTimeIn = datetime.now()
                           atts.morningDailyStatus = 'not late'
                           dbase.session.commit()
                           print'ddddddddddddd'
                           return jsonify({'message': 'not late, kindly dont forget to timeout in morning'})
                     else:
                           print'eeeeeeeeeeeeeee'
                           return jsonify({'message': 'you cannot time in twice'})
                  elif atts.morningStatus == 1 and atts.afterStatus == 1:
                     atts.afterStatus = 0
                     atts.afterTimeOut = datetime.now()
                     dbase.session.commit()
                     print'fffffffffffff'
                     return jsonify({'message': 'no time out at this time'})

               elif (now > m9) and (now <= m12):
                  if atts.morningStatus == 0 and atts.afterStatus == 0:
                     if atts.morningTimeOut is None:
                           atts.morningStatus = 1
                           atts.lateTotal = 1
                           employee.late = employee.late + 1
                           atts.morningDailyStatus = 'late'
                           atts.morningTimeIn = datetime.now()
                           # atts.morningRemark = wala pa nabutang
                           print 'ggggggggggg'
                           dbase.session.commit()
                           return jsonify({'message': 'late'})
                     else:
                           print'hhhhhhhhhhhhhhhhhh'
                           return jsonify({'message': 'you cannot time in twice'})
                  elif atts.morningStatus == 1 and atts.afterStatus == 0:
                     if atts.morningTimeOut is None:
                           atts.morningStatus = 0
                           atts.morningTimeOut = datetime.now()
                           # atts.morningRemark = wala pa nabutang
                           print 'iiiiiiiiiiii'
                           dbase.session.commit()
                           return jsonify({'message': 'time out'})
                     else:
                           print'jjjjjjjjjjjjjj'
                           return jsonify({'message': 'you cannot time in twice'})
                  elif atts.morningStatus == 0 and atts.afterStatus == 1:
                     if atts.morningTimeOut is None:
                           atts.afterStatus = 0
                           atts.morningStatus = 1
                           atts.afterTimeOut = datetime.now()
                           atts.morningTimeIn = datetime.now()
                           atts.morningDailyStatus = 'late'
                           # atts.morningRemark = wala pa nabutang
                           print 'kkkkkkkkkkkkk'
                           dbase.session.commit()
                           return jsonify({'message': 'late, kindly dont forget to timeout in morning'})
                     else:
                           print'lllllllllllllllll'
                           return jsonify({'message': 'you cannot time in twice'})
                  elif atts.morningStatus == 1 and atts.afterStatus == 1:
                     if atts.morningTimeOut is None:
                           atts.afterStatus = 0
                           atts.morningStatus = 0
                           atts.afterTimeOut = datetime.now()
                           atts.morningTimeOut = datetime.now()
                           print 'mmmmmmmmmmmmmmm'
                           dbase.session.commit()
                           return jsonify({'message': 'time out'})
                     else:
                           print'nnnnnnnnnnnnnn'
                           return jsonify({'message': 'you cannot time in twice'})
               elif (now > m12) and (now <= a1):  # 12 -7pm
                  if atts.morningStatus == 0 and atts.afterStatus == 0:
                     if atts.afterTimeOut is None:
                           atts.afterStatus = 1
                           atts.afterDailyStatus = 'not late'
                           atts.afterTimeIn = datetime.now()
                           # atts.morningRemark = wala pa nabutang
                           print 'ooooooooooo'
                           dbase.session.commit()
                           print'ppppppppppppppp'
                           return jsonify({'message': 'time in for afternoon'})
                     else:
                           print'qqqqqqqqqqqqqq'
                           return jsonify({'message': 'you cannot time in twice'})
                  elif atts.morningStatus == 1 and atts.afterStatus == 0:
                     if atts.afterTimeOut is None:
                           atts.morningStatus = 0
                           atts.morningTimeOut = datetime.now()
                           # atts.morningRemark = wala pa nabutang
                           print 'rrrrrrrrrrrrrrrr'
                           dbase.session.commit()
                           return jsonify({'message': 'time out for morning'})
                     else:
                           print'ssssssssssssssss'
                           return jsonify({'message': 'you cannot time in twice'})
                  elif atts.morningStatus == 0 and atts.afterStatus == 1:
                     print'tttttttttttttttttt'
                     return jsonify({'message': 'no time out for afternoon at this time'})
                  elif atts.morningStatus == 1 and atts.afterStatus == 1:
                     atts.morningStatus = 0
                     atts.morningTimeOut = datetime.now()
                     dbase.session.commit()
                     print'uuuuuuuuuuuuuuuuuuuu'
                     return jsonify({'message': 'no time out for afternoon at this time'})

               elif (now > a1) and (now <= a6):
                  if atts.morningStatus == 0 and atts.afterStatus == 0:
                     if atts.afterTimeOut is None:
                           atts.afterStatus = 1
                           atts.lateTotal = 1
                           employee.late = employee.late + 1
                           atts.afterDailyStatus = 'late'
                           atts.afterTimeIn = datetime.now()
                           # atts.morningRemark = wala pa nabutang
                           dbase.session.commit()
                           print'vvvvvvvvvvvvvvvvvv'
                           return jsonify({'message': 'late'})
                     else:
                           print'wwwwwwwwwwwwwwwwww'
                           return jsonify({'message': 'you cannot time in twice'})
                  elif atts.morningStatus == 1 and atts.afterStatus == 0:
                     if atts.afterTimeOut is None:
                           atts.morningStatus = 0
                           atts.afterStatus = 1
                           atts.morningTimeOut = datetime.now()
                           atts.lateTotal = 1
                           employee.late = employee.late + 1
                           atts.afterDailyStatus = 'late'
                           atts.afterTimeIn = datetime.now()
                           # atts.morningRemark = wala pa nabutang
                           print'xxxxxxxxxxxxxxxxxxxxxx'
                           return jsonify({'message': 'time out'})
                     else:
                           print'yyyyyyyyyyyyyyyyy'
                           return jsonify({'message': 'you cannot time in twice'})
                  elif atts.morningStatus == 0 and atts.afterStatus == 1:
                     atts.afterStatus = 0
                     atts.afterTimeOut = datetime.now()
                     dbase.session.commit()
                     print'zzzzzzzzzzzzzzzzzzzzzz'
                     return jsonify({'message': 'time out'})
                  elif atts.morningStatus == 1 and atts.afterStatus == 1:
                     atts.afterStatus = 0
                     atts.morningStatus = 0
                     atts.afterTimeOut = datetime.now()
                     atts.morningTimeOut = datetime.now()
                     dbase.session.commit()
                     print'1111111111111'
                     return jsonify({'message': 'time out'})

               elif now > a6 and now <= a7:
                  if employee1.overtimeInStatus == 0:
                     employee1.overtimeInStatus = 1
                     employee1.overtimeIn = datetime.now()

                  if atts.morningStatus == 0 and atts.afterStatus == 0:
                     print'R`'
                     absents()
                     dbase.session.commit()
                     return jsonify({'message': 'no time in for this time'})

                  elif atts.morningStatus == 1 and atts.afterStatus == 0:
                     atts.morningStatus = 0
                     atts.morningTimeOut = datetime.now()
                     dbase.session.commit()
                     print'S`'
                     absents()
                     return jsonify({'message': 'not time in for afternoon'})

                  elif atts.morningStatus == 0 and atts.afterStatus == 1:
                     atts.afterStatus = 0
                     atts.afterTimeOut = datetime.now()
                     dbase.session.commit()
                     print'T`'
                     absents()
                     return jsonify({'message': 'time out for afternoon'})

                  elif atts.morningStatus == 1 and atts.afterStatus == 1:
                     atts.morningStatus = 0
                     atts.afterStatus = 0
                     atts.morningTimeOut = datetime.now()
                     atts.afterTimeOut = datetime.now()
                     dbase.session.commit()
                     print'U`'
                     absents()
                     return jsonify({'message': 'time out for afternoon and morning'})

               elif now > a7 and now <= o10:
                  if employee1:
                           if employee1.overtimeInStatus == 0:
                              employee1.overtimeInStatus = 1
                              employee1.overtimeIn = datetime.now()
                              dbase.session.commit()
                              return jsonify({'message': 'Overtime time in success'})
                           elif employee1.overtimeInStatus == 1:
                              employee1.overtimeOut = datetime.now()
                              dbase.session.commit()
                              return jsonify({'message': 'Overtime time out success'})

         # ////////// ///////////////////////////////IF ID IS EXISTING/////////////////////////////////////////////////////////
         elif atts:
               dates = Attendance.query.filter_by(
                   date=datenow).order_by(Attendance.date.desc()).first()
               print dates
               atts = Attendance.query.filter(and_(Attendance.employeeid == empID, Attendance.date == datenow)).order_by(
                   Attendance.date.desc()).first()
               # dbase.session.commit()
               # date1 = atts.date
               print "second"
               dates = Attendance.query.filter_by(date=datenow).first()
               employee1 = Overtime.query.filter(and_(
                   Overtime.employeeid == empID, Overtime.overtimeStatus == 1, Overtime.overtimeDate == datenow2)).first()

               if dates:
                  pass
               else:
                  dbase.session.add(attendancenNew)
                  dbase.session.commit()
                  atts.date = datenow
                  print atts.date + 'jfjfjfjfjfjfjfhfnr nvjfnfnhmfn'
                  dbase.session.commit()

                  print '1234567890-'
                  print datenow + "mkmkmkkmkkkmkmkmkkkmkmkmk"
                  atts = Attendance.query.filter(
                      and_(Attendance.employeeid == empID, Attendance.date == datenow)).order_by(
                      Attendance.date.desc()).first()
         # ///////////////////////////////////////////CHECK IF THE DATE IS SAME//////////////////////////////////////
               if atts.date == datenow:

                  # ////////////////////////IF DATE IS SAME////////////////////////////#
                  print atts.date + 'nabuang siya'
                  if now >= m7 and now <= m9:
                     if atts.morningStatus == 0 and atts.afterStatus == 0:
                           if atts.morningTimeOut is None:
                              atts.morningStatus = 1
                              atts.morningTimeIn = datetime.now()
                              atts.morningDailyStatus = 'not late'
                              print "AAAAAAAAAAAAAAAA"
                              dbase.session.commit()
                              return jsonify({'message': 'not late'})
                           else:
                              print'BBBBBBBBBBBBBBBBBBBBB'
                              return jsonify({'message': 'you cannot time in twice'})
                     elif atts.morningStatus == 1 and atts.afterStatus == 0:
                           print 'CCCCCCCCCCCCCCCC'
                           return jsonify({'message': 'no time out at this time'})
                     elif atts.morningStatus == 0 and atts.afterStatus == 1:
                           if atts.morningTimeOut is None:
                              atts.afterStatus = 0
                              atts.morningStatus = 1
                              atts.afterTimeOut = datetime.now()
                              atts.morningTimeIn = datetime.now()
                              atts.morningDailyStatus = 'not late'
                              dbase.session.commit()
                              print'DDDDDDDDDDDDDDDDDD'
                              return jsonify({'message': 'not late, kindly dont forget to timeout in morning'})
                           else:
                              print'EEEEEEEEEEEEEEEEEE'
                              return jsonify({'message': 'you cannot time in twice'})
                     elif atts.morningStatus == 1 and atts.afterStatus == 1:
                           atts.afterStatus = 0
                           atts.afterTimeOut = datetime.now()
                           dbase.session.commit()
                           print'FFFFFFFFFFFFFFFF'
                           return jsonify({'message': 'no time out at this time'})

                  elif now > m9 and now <= m12:
                     if atts.morningStatus == 0 and atts.afterStatus == 0:
                           if atts.morningTimeOut is None:
                              atts.morningStatus = 1
                              atts.lateTotal = 1
                              employee.late = employee.late + 1
                              atts.morningDailyStatus = 'late'
                              atts.morningTimeIn = datetime.now()
                              # atts.morningRemark = wala pa nabutang
                              print 'GGGGGGGGGGGGGGGGGGGGGGGGG'
                              dbase.session.commit()
                              return jsonify({'message': 'late'})
                           else:
                              print'HHHHHHHHHHHHHHHHHHHHHHHHHHH'
                              return jsonify({'message': 'you cannot time in twice'})
                     elif atts.morningStatus == 1 and atts.afterStatus == 0:
                           if atts.morningTimeOut is None:
                              atts.morningStatus = 0
                              atts.morningTimeOut = datetime.now()
                              # atts.morningRemark = wala pa nabutang
                              print 'IIIIIIIIIIIIIIIIII'
                              dbase.session.commit()
                              return jsonify({'message': 'time out'})
                           else:
                              print'JJJJJJJJJJJJJJJ'
                              return jsonify({'message': 'you cannot time in twice'})
                     elif atts.morningStatus == 0 and atts.afterStatus == 1:
                           if atts.morningTimeOut is None:
                              atts.afterStatus = 0
                              atts.morningStatus = 1
                              atts.afterTimeOut = datetime.now()
                              atts.morningTimeIn = datetime.now()
                              atts.morningDailyStatus = 'late'
                              # atts.morningRemark = wala pa nabutang
                              print'KKKKKKKKKKKK'
                              dbase.session.commit()
                              return jsonify({'message': 'late, kindly dont forget to timeout in morning'})
                           else:
                              print'LLLLLLLLLLLLLLLLLL'
                              return jsonify({'message': 'you cannot time in twice'})
                     elif atts.morningStatus == 1 and atts.afterStatus == 1:
                           if atts.morningTimeOut is None:
                              atts.afterStatus = 0
                              atts.morningStatus = 0
                              atts.afterTimeOut = datetime.now()
                              atts.morningTimeOut = datetime.now()
                              dbase.session.commit()
                              print'MMMMMMMMMMMMMMMMMM'
                              return jsonify({'message': 'time out'})
                           else:
                              print'NNNNNNNNNNNNNN'
                              return jsonify({'message': 'you cannot time in twice'})
                  elif now > m12 and now <= a1:  # 12 -7pm
                     if atts.morningStatus == 0 and atts.afterStatus == 0:
                           if atts.afterTimeOut is None:
                              atts.afterStatus = 1
                              atts.afterDailyStatus = 'not late'
                              atts.afterTimeIn = datetime.now()
                              # atts.morningRemark = wala pa nabutang
                              print 'OOOOOOOOOOOOOOOOOO'
                              dbase.session.commit()
                              return jsonify({'message': 'time in for afternoon'})
                           else:
                              print'PPPPPPPPPPPPPPPPPPPPPPP'
                              return jsonify({'message': 'you cannot time in twice'})
                     elif atts.morningStatus == 1 and atts.afterStatus == 0:
                           if atts.afterTimeOut is None:
                              atts.morningStatus = 0
                              atts.morningTimeOut = datetime.now()
                              # atts.morningRemark = wala pa nabutang
                              print 'QQQQQQQQQQQQQQQQQQQ'
                              dbase.session.commit()
                              return jsonify({'message': 'time out for morning'})
                           else:
                              print'RRRRRRRRRRRRRRR'
                              return jsonify({'message': 'you cannot time in twice'})
                     elif atts.morningStatus == 0 and atts.afterStatus == 1:
                           print'SSSSSSSSSSSSSSSSSSSSS'
                           return jsonify({'message': 'no time out for afternoon at this time'})
                     elif atts.morningStatus == 1 and atts.afterStatus == 1:
                           atts.morningStatus = 0
                           atts.morningTimeOut = datetime.now()
                           dbase.session.commit()
                           print'TTTTTTTTTTTTTTT'
                           return jsonify({'message': 'no time out for afternoon at this time'})
                  elif now > a1 and now <= a6:
                     if atts.morningStatus == 0 and atts.afterStatus == 0:
                           if atts.afterTimeOut is None:
                              atts.afterStatus = 1
                              atts.lateTotal = 1
                              employee.late = employee.late + 1
                              atts.afterDailyStatus = 'late'
                              atts.afterTimeIn = datetime.now()
                              # atts.morningRemark = wala pa nabutang
                              print 'UUUUUUUUUUUUUUUUU'
                              dbase.session.commit()
                              return jsonify({'message': 'late'})
                           else:
                              print'VVVVVVVVVVVV'
                              return jsonify({'message': 'you cannot time in twice'})
                     elif atts.morningStatus == 1 and atts.afterStatus == 0:
                           if atts.afterTimeOut is None:
                              atts.morningStatus = 0
                              atts.afterStatus = 1
                              atts.morningTimeOut = datetime.now()
                              atts.lateTotal = 1
                              employee.late = employee.late + 1
                              atts.afterDailyStatus = 'late'
                              atts.afterTimeIn = datetime.now()
                              # atts.morningRemark = wala pa nabutang
                              print 'WWWWWWWWWWWWWWWWWWWW'
                              dbase.session.commit()
                              return jsonify({'message': '"time in for afternoon." (time out for morning next time,) '})
                           else:
                              print'XXXXXXXXXXXXXXX'
                              return jsonify({'message': 'you cannot time in twice'})
                     elif atts.morningStatus == 0 and atts.afterStatus == 1:
                           atts.afterStatus = 0
                           atts.afterTimeOut = datetime.now()
                           dbase.session.commit()
                           print'YYYYYYYYYYYYYYYY'
                           return jsonify({'message': 'time out'})
                     elif atts.morningStatus == 1 and atts.afterStatus == 1:
                           atts.afterStatus = 0
                           atts.morningStatus = 0
                           atts.afterTimeOut = datetime.now()
                           atts.morningTimeOut = datetime.now()
                           dbase.session.commit()
                           print'ZZZZZZZZZZZZZZZZZZZZ'
                           return jsonify({'message': 'time out'})

                  elif now > a6 and now <= a7:
                     if employee1.overtimeInStatus == 0:
                           employee1.overtimeInStatus = 1
                           employee1.overtimeIn = datetime.now()

                     if atts.morningStatus == 0 and atts.afterStatus == 0:
                           print'R`'
                           absents()
                           dbase.session.commit()
                           return jsonify({'message': 'no time in for this time'})

                     elif atts.morningStatus == 1 and atts.afterStatus == 0:
                           atts.morningStatus = 0
                           atts.morningTimeOut = datetime.now()
                           dbase.session.commit()
                           print'S`'
                           absents()
                           return jsonify({'message': 'not time in for afternoon'})

                     elif atts.morningStatus == 0 and atts.afterStatus == 1:
                           atts.afterStatus = 0
                           atts.afterTimeOut = datetime.now()
                           dbase.session.commit()
                           print'T`'
                           absents()
                           return jsonify({'message': 'time out for afternoon'})

                     elif atts.morningStatus == 1 and atts.afterStatus == 1:
                           atts.morningStatus = 0
                           atts.afterStatus = 0
                           atts.morningTimeOut = datetime.now()
                           atts.afterTimeOut = datetime.now()
                           dbase.session.commit()
                           print'U`'
                           absents()
                           return jsonify({'message': 'time out for afternoon and morning'})

                  elif now > a7 and now <= o10:
                     if employee1:
                           if employee1.overtimeInStatus == 0:
                              employee1.overtimeInStatus = 1
                              employee1.overtimeIn = datetime.now()
                              dbase.session.commit()
                              return jsonify({'message': 'Overtime time in success'})
                           elif employee1.overtimeInStatus == 1:
                              employee1.overtimeOut = datetime.now()
                              dbase.session.commit()
                              return jsonify({'message': 'Overtime time out success'})

   # ///////////////////////////////////////IF DATE IS NOT THE SAME CREATE NEW ATTENDANCE////////////////////////
               else:

                  atts = Attendance.query.filter(
                      and_(Attendance.employeeid == empID, Attendance.date == datenow)).order_by(
                      Attendance.date.desc()).first()

                  print "last"

                  employee1 = Overtime.query.filter(and_(
                      Overtime.employeeid == empID, Overtime.overtimeStatus == 1, Overtime.overtimeDate == datenow2)).first()

                  if (now >= m7) and (now <= m9):
                     if atts.morningStatus == 0 and atts.afterStatus == 0:
                           if atts.morningTimeOut is None:
                              atts.morningStatus = 1
                              atts.morningTimeIn = datetime.now()
                              atts.morningDailyStatus = 'not late'
                              print "9999999999999999999999"
                              dbase.session.commit()
                              return jsonify({'message': 'not late'})
                           else:
                              print'8888888888888888888888'
                              return jsonify({'message': 'you cannot time in twice'})
                     elif atts.morningStatus == 1 and atts.afterStatus == 0:
                           print '777777777777777777777777'
                           return jsonify({'message': 'no time out at this time'})
                     elif atts.morningStatus == 0 and atts.afterStatus == 1:
                           if atts.morningTimeOut is None:
                              atts.afterStatus = 0
                              atts.morningStatus = 1
                              atts.afterTimeOut = datetime.now()
                              atts.morningTimeIn = datetime.now()
                              atts.morningDailyStatus = 'not late'
                              dbase.session.commit()
                              print'66666666666666666666665454565'
                              return jsonify({'message': 'not late, kindly dont forget to timeout in morning'})
                           else:
                              print'555555555555555555555555555'
                              return jsonify({'message': 'you cannot time in twice'})
                     elif atts.morningStatus == 1 and atts.afterStatus == 1:
                           atts.afterStatus = 0
                           atts.afterTimeOut = datetime.now()
                           dbase.session.commit()
                           print'444441254'
                           return jsonify({'message': 'no time out at this time'})

                  elif now > m9 and now <= m12:
                     if atts.morningStatus == 0 and atts.afterStatus == 0:
                           if atts.morningTimeOut is None:
                              atts.morningStatus = 1
                              atts.lateTotal = 1
                              employee.late = employee.late + 1
                              atts.morningDailyStatus = 'late'
                              atts.morningTimeIn = datetime.now()
                              # atts.morningRemark = wala pa nabutang
                              print '3'
                              dbase.session.commit()
                              return jsonify({'message': 'late'})
                           else:
                              print'2'
                              return jsonify({'message': 'you cannot time in twice'})
                     elif atts.morningStatus == 1 and atts.afterStatus == 0:
                           if atts.morningTimeOut is None:
                              atts.morningStatus = 0
                              atts.morningTimeOut = datetime.now()
                              # atts.morningRemark = wala pa nabutang
                              print '1'
                              dbase.session.commit()
                              return jsonify({'message': 'time out'})
                           else:
                              print'A`'
                              return jsonify({'message': 'you cannot time in twice'})
                     elif atts.morningStatus == 0 and atts.afterStatus == 1:
                           if atts.morningTimeOut is None:
                              atts.afterStatus = 0
                              atts.morningStatus = 1
                              atts.afterTimeOut = datetime.now()
                              atts.morningTimeIn = datetime.now()
                              atts.morningDailyStatus = 'late'
                              # atts.morningRemark = wala pa nabutang
                              dbase.session.commit()
                              print'B`'
                              return jsonify({'message': 'late, kindly dont forget to timeout in morning'})
                           else:
                              print'C`'
                              return jsonify({'message': 'you cannot time in twice'})
                     elif atts.morningStatus == 1 and atts.afterStatus == 1:
                           if atts.morningTimeOut is None:
                              atts.afterStatus = 0
                              atts.morningStatus = 0
                              atts.afterTimeOut = datetime.now()
                              atts.morningTimeOut = datetime.now()
                              dbase.session.commit()
                              print'D`'
                              return jsonify({'message': 'time out'})
                           else:
                              print'E`'
                              return jsonify({'message': 'you cannot time in twice'})
                  elif (now > m12) and (now <= a1):  # 12 -7pm
                     if atts.morningStatus == 0 and atts.afterStatus == 0:
                           if atts.afterTimeOut is None:
                              atts.afterStatus = 1
                              atts.afterDailyStatus = 'not late'
                              atts.afterTimeIn = datetime.now()
                              # atts.morningRemark = wala pa nabutang
                              print 'F`'
                              dbase.session.commit()
                              return jsonify({'message': 'time in for afternoon'})
                           else:
                              print'G`'
                              return jsonify({'message': 'you cannot time in twice'})
                     elif atts.morningStatus == 1 and atts.afterStatus == 0:
                           if atts.afterTimeOut is None:
                              atts.morningStatus = 0
                              atts.morningTimeOut = datetime.now()
                              # atts.morningRemark = wala pa nabutang
                              print 'H`'
                              dbase.session.commit()
                              return jsonify({'message': 'time out for morning'})
                           else:
                              print'I`'
                              return jsonify({'message': 'you cannot time in twice'})
                     elif atts.morningStatus == 0 and atts.afterStatus == 1:
                           print'J`'
                           return jsonify({'message': 'no time out for afternoon at this time'})
                     elif atts.morningStatus == 1 and atts.afterStatus == 1:
                           atts.morningStatus = 0
                           atts.morningTimeOut = datetime.now()
                           dbase.session.commit()
                           print'K`'
                           return jsonify({'message': 'no time out for afternoon at this time'})
                  elif now > a1 and now <= a6:
                     if atts.morningStatus == 0 and atts.afterStatus == 0:
                           if atts.afterTimeOut is None:
                              atts.afterStatus = 1
                              atts.lateTotal = 1
                              employee.late = employee.late + 1
                              atts.afterDailyStatus = 'late'
                              atts.afterTimeIn = datetime.now()
                              # atts.morningRemark = wala pa nabutang
                              print 'L`'
                              dbase.session.commit()
                              return jsonify({'message': 'late'})
                           else:
                              print'M`'
                              return jsonify({'message': 'you cannot time in twice'})
                     elif atts.morningStatus == 1 and atts.afterStatus == 0:
                           if atts.afterTimeOut is None:
                              atts.morningStatus = 0
                              atts.afterStatus = 1
                              atts.morningTimeOut = datetime.now()
                              atts.lateTotal = 1
                              employee.late = employee.late + 1
                              atts.afterDailyStatus = 'late'
                              atts.afterTimeIn = datetime.now()
                              # atts.morningRemark = wala pa nabutang
                              print 'N`'
                              dbase.session.commit()
                              return jsonify({'message': 'time out'})
                           else:
                              print'O`'
                              return jsonify({'message': 'you cannot time in twice'})
                     elif atts.morningStatus == 0 and atts.afterStatus == 1:
                           atts.afterStatus = 0
                           atts.afterTimeOut = datetime.now()
                           dbase.session.commit()
                           print'P`'
                           return jsonify({'message': 'time out'})
                     elif atts.morningStatus == 1 and atts.afterStatus == 1:
                           atts.afterStatus = 0
                           atts.morningStatus = 0
                           atts.afterTimeOut = datetime.now()
                           atts.morningTimeOut = datetime.now()
                           dbase.session.commit()
                           print'Q`'
                           return jsonify({'message': 'time out'})

                  elif now > a6 and now <= a7:
                     if employee1.overtimeInStatus == 0:
                           employee1.overtimeInStatus = 1
                           employee1.overtimeIn = datetime.now()

                     if atts.morningStatus == 0 and atts.afterStatus == 0:
                           print'R`'
                           absents()
                           dbase.session.commit()
                           return jsonify({'message': 'no time in for this time'})

                     elif atts.morningStatus == 1 and atts.afterStatus == 0:
                           atts.morningStatus = 0
                           atts.morningTimeOut = datetime.now()
                           dbase.session.commit()
                           print'S`'
                           absents()
                           return jsonify({'message': 'not time in for afternoon'})

                     elif atts.morningStatus == 0 and atts.afterStatus == 1:
                           atts.afterStatus = 0
                           atts.afterTimeOut = datetime.now()
                           dbase.session.commit()
                           print'T`'
                           absents()
                           return jsonify({'message': 'time out for afternoon'})

                     elif atts.morningStatus == 1 and atts.afterStatus == 1:
                           atts.morningStatus = 0
                           atts.afterStatus = 0
                           atts.morningTimeOut = datetime.now()
                           atts.afterTimeOut = datetime.now()
                           dbase.session.commit()
                           print'U`'
                           absents()
                           return jsonify({'message': 'time out for afternoon and morning'})
                  elif now > a7 and now <= o10:
                     if employee1:
                           if employee1.overtimeInStatus == 0:
                              employee1.overtimeInStatus = 1
                              employee1.overtimeIn = datetime.now()
                              dbase.session.commit()
                              return jsonify({'message': 'Overtime time in success'})
                           elif employee1.overtimeInStatus == 1:
                              employee1.overtimeOut = datetime.now()
                              employee1.overtimeInStatus == 2
                              dbase.session.commit()
                              return jsonify({'message': 'Overtime time out success'})
                           else:
                              return jsonify({'message': 'Request for overtime '})
                     else:
                           return jsonify({'message': 'Please request overtime first!'})
      else:
         print('sulod syas personal bay!')
         morning7 = PersonalTimeIN.morningTimeIn
         morning9 = PersonalTimeIN.morningTimeOut
         morning12 = PersonalTimeIN.morningTimeOutend
         after1 = PersonalTimeIN.afterTimeIn
         after6 = PersonalTimeIN.afterTimeOut
         after7 = PersonalTimeIN.afterTimeOutend
         return(personalTime_in(morning7, morning9, morning12,
                         after1, after6, after7, empID))


@app.route('/set/personalTime', methods=['POST'])
def set_time():
   data = request.get_json()
   #ako ra edit aning line sa ubos
   personal_time = PersonalTime(employeeid=data['id'], morningTimeIn=data['morningIn'], morningTimeOut=data['morningOut'], morningTimeOutend=data['morningOutend'],
                                afterTimeIn=data['afterIn'], afterTimeOut=data['afterOut'], afterTimeOutend=data['afterOutend'], date=data['date'])
   dbase.session.add(personal_time)
   dbase.session.commit()
   return jsonify({'message': 'Individual Time added!'})


def personalTime_in(morning7, morning9, morning12, afte1, afte6, afte7, empID):
   now = datetime.now().strftime("%m%d%Y%H%M")
   datenow1 = datetime.now().strftime("%m%d%Y")
   datenow3 = datetime.now().strftime("%Y-%m-%d")
   y, m, d = datenow3.split("-")
   datenow2 = dt.date(int(y), int(m), int(d))
   datenow = datetime.strptime(str(datenow1), "%m%d%Y")
   week_no = datetime.strptime(str(datenow1), "%m%d%Y").isocalendar()[1]

   morning7 = morning7.strftime("%H%M")
   print(morning7)
   morning9 = morning9.strftime("%H%M")
   print(morning9)
   morning12 = morning12.strftime("%H%M")
   print(morning12)

   afte1 = afte1.strftime("%H%M")
   print(afte1)
   afte6 = afte6.strftime("%H%M")
   print(afte6)
   afte7 = afte7.strftime("%H%M")
   print(afte7)

   m7 = ''.join([datenow1, morning7])
   m9 = ''.join([datenow1, morning9])
   m12 = ''.join([datenow1, morning12])
   o10 = ''.join([datenow1, "2200"])

   a1 = ''.join([datenow1, afte1])
   a6 = ''.join([datenow1, afte6])
   a7 = ''.join([datenow1, afte7])

   # 1 for active and 0 for inactive
   attendancenNew = Attendance(employeeid=empID)
   employee = Employee.query.filter(
       and_(Employee.employeeid == empID, Employee.employeestatus == 1)).first()
   if not employee:
      return jsonify({'message': 'user not found'})
   atts = Attendance.query.filter(and_(Attendance.employeeid == empID, Attendance.date == str(
       datenow))).order_by(Attendance.date.desc()).first()
   # ////////////////////////////IF ID IS NOT LISTED IN THE ATTENDACE CRETAE NEW///////////////////////////////#
   if not atts:

      dbase.session.add(attendancenNew)
      dbase.session.commit()

      atts = Attendance.query.filter_by(
          employeeid=empID).order_by(Attendance.date.desc()).first()
      print atts
      print '1st'
      atts.date = datenow
      atts.week_number = week_no
      dbase.session.commit()
      employee1 = Overtime.query.filter(and_(
          Overtime.employeeid == empID, Overtime.overtimeStatus == 1, Overtime.overtimeDate == datenow2)).first()
      dates = Attendance.query.filter_by(date=datenow).first()
      if dates:
         print '444546456646546465465465464654654654654'
         pass
      else:
         dbase.session.add(attendancenNew)
         dbase.session.commit()
         print '0987654321=-098765'
      # nowdate = atts.date
      if (now >= m7) and (now <= m9):
         if atts.morningStatus == 0 and atts.afterStatus == 0:
            if atts.morningTimeOut is None:
               atts.morningStatus = 1
               atts.morningTimeIn = datetime.now()
               atts.morningDailyStatus = 'not late'
               print "aaaaaaa"
               dbase.session.commit()
               return jsonify({'message': 'not late'})
            else:
               print 'bbbbbbbbbbbbbbbbbbbbbbb'
               return jsonify({'message': 'you cannot time in twice'})
         elif atts.morningStatus == 1 and atts.afterStatus == 0:
            print 'ccccccccc'
            return jsonify({'message': 'no time out at this time'})
         elif atts.morningStatus == 0 and atts.afterStatus == 1:
            if atts.morningTimeOut is None:
               atts.afterStatus = 0
               atts.morningStatus = 1
               atts.afterTimeOut = datetime.now()
               atts.morningTimeIn = datetime.now()
               atts.morningDailyStatus = 'not late'
               dbase.session.commit()
               print'ddddddddddddd'
               return jsonify({'message': 'not late, kindly dont forget to timeout in morning'})
            else:
               print'eeeeeeeeeeeeeee'
               return jsonify({'message': 'you cannot time in twice'})
         elif atts.morningStatus == 1 and atts.afterStatus == 1:
            atts.afterStatus = 0
            atts.afterTimeOut = datetime.now()
            dbase.session.commit()
            print'fffffffffffff'
            return jsonify({'message': 'no time out at this time'})
      elif (now > m9) and (now <= m12):
         if atts.morningStatus == 0 and atts.afterStatus == 0:
            if atts.morningTimeOut is None:
               atts.morningStatus = 1
               atts.lateTotal = 1
               employee.late = employee.late + 1
               atts.morningDailyStatus = 'late'
               atts.morningTimeIn = datetime.now()
               # atts.morningRemark = wala pa nabutang
               print 'ggggggggggg'
               dbase.session.commit()
               return jsonify({'message': 'late'})
            else:
               print'hhhhhhhhhhhhhhhhhh'
               return jsonify({'message': 'you cannot time in twice'})
         elif atts.morningStatus == 1 and atts.afterStatus == 0:
            if atts.morningTimeOut is None:
               atts.morningStatus = 0
               atts.morningTimeOut = datetime.now()
               # atts.morningRemark = wala pa nabutang
               print 'iiiiiiiiiiii'
               dbase.session.commit()
               return jsonify({'message': 'time out'})
            else:
               print'jjjjjjjjjjjjjj'
               return jsonify({'message': 'you cannot time in twice'})
         elif atts.morningStatus == 0 and atts.afterStatus == 1:
            if atts.morningTimeOut is None:
               atts.afterStatus = 0
               atts.morningStatus = 1
               atts.afterTimeOut = datetime.now()
               atts.morningTimeIn = datetime.now()
               atts.morningDailyStatus = 'late'
               # atts.morningRemark = wala pa nabutang
               print 'kkkkkkkkkkkkk'
               dbase.session.commit()
               return jsonify({'message': 'late, kindly dont forget to timeout in morning'})
            else:
               print'lllllllllllllllll'
               return jsonify({'message': 'you cannot time in twice'})
         elif atts.morningStatus == 1 and atts.afterStatus == 1:
            if atts.morningTimeOut is None:
               atts.afterStatus = 0
               atts.morningStatus = 0
               atts.afterTimeOut = datetime.now()
               atts.morningTimeOut = datetime.now()
               print 'mmmmmmmmmmmmmmm'
               dbase.session.commit()
               return jsonify({'message': 'time out'})
            else:
               print'nnnnnnnnnnnnnn'
               return jsonify({'message': 'you cannot time in twice'})
      elif (now > m12) and (now <= a1):  # 12 -7pm
         if atts.morningStatus == 0 and atts.afterStatus == 0:
            if atts.afterTimeOut is None:
               atts.afterStatus = 1
               atts.afterDailyStatus = 'not late'
               atts.afterTimeIn = datetime.now()
               # atts.morningRemark = wala pa nabutang
               print 'ooooooooooo'
               dbase.session.commit()
               print'ppppppppppppppp'
               return jsonify({'message': 'time in for afternoon'})
            else:
               print'qqqqqqqqqqqqqq'
               return jsonify({'message': 'you cannot time in twice'})
         elif atts.morningStatus == 1 and atts.afterStatus == 0:
            if atts.afterTimeOut is None:
               atts.morningStatus = 0
               atts.morningTimeOut = datetime.now()
               # atts.morningRemark = wala pa nabutang
               print 'rrrrrrrrrrrrrrrr'
               dbase.session.commit()
               return jsonify({'message': 'time out for morning'})
            else:
               print'ssssssssssssssss'
               return jsonify({'message': 'you cannot time in twice'})
         elif atts.morningStatus == 0 and atts.afterStatus == 1:
            print'tttttttttttttttttt'
            return jsonify({'message': 'no time out for afternoon at this time'})
         elif atts.morningStatus == 1 and atts.afterStatus == 1:
            atts.morningStatus = 0
            atts.morningTimeOut = datetime.now()
            dbase.session.commit()
            print'uuuuuuuuuuuuuuuuuuuu'
            return jsonify({'message': 'no time out for afternoon at this time'})
      elif (now > a1) and (now <= a6):
         if atts.morningStatus == 0 and atts.afterStatus == 0:
            if atts.afterTimeOut is None:
               atts.afterStatus = 1
               atts.lateTotal = 1
               employee.late = employee.late + 1
               atts.afterDailyStatus = 'late'
               atts.afterTimeIn = datetime.now()
               # atts.morningRemark = wala pa nabutang
               dbase.session.commit()
               print'vvvvvvvvvvvvvvvvvv'
               return jsonify({'message': 'late'})
            else:
               print'wwwwwwwwwwwwwwwwww'
               return jsonify({'message': 'you cannot time in twice'})
         elif atts.morningStatus == 1 and atts.afterStatus == 0:
            if atts.afterTimeOut is None:
               atts.morningStatus = 0
               atts.afterStatus = 1
               atts.morningTimeOut = datetime.now()
               atts.lateTotal = 1
               employee.late = employee.late + 1
               atts.afterDailyStatus = 'late'
               atts.afterTimeIn = datetime.now()
               # atts.morningRemark = wala pa nabutang
               print'xxxxxxxxxxxxxxxxxxxxxx'
               return jsonify({'message': 'time out'})
            else:
               print'yyyyyyyyyyyyyyyyy'
               return jsonify({'message': 'you cannot time in twice'})
         elif atts.morningStatus == 0 and atts.afterStatus == 1:
            atts.afterStatus = 0
            atts.afterTimeOut = datetime.now()
            dbase.session.commit()
            print'zzzzzzzzzzzzzzzzzzzzzz'
            return jsonify({'message': 'time out'})
         elif atts.morningStatus == 1 and atts.afterStatus == 1:
            atts.afterStatus = 0
            atts.morningStatus = 0
            atts.afterTimeOut = datetime.now()
            atts.morningTimeOut = datetime.now()
            dbase.session.commit()
            print'1111111111111'
            return jsonify({'message': 'time out'})

      elif now > a6 and now <= a7:
         if employee1.overtimeInStatus == 0:
            employee1.overtimeInStatus = 1
            employee1.overtimeIn = datetime.now()

         if atts.morningStatus == 0 and atts.afterStatus == 0:
            print'R`'
            absents()
            dbase.session.commit()
            return jsonify({'message': 'no time in for this time'})

         elif atts.morningStatus == 1 and atts.afterStatus == 0:
            atts.morningStatus = 0
            atts.morningTimeOut = datetime.now()
            dbase.session.commit()
            print'S`'
            absents()
            return jsonify({'message': 'not time in for afternoon'})

         elif atts.morningStatus == 0 and atts.afterStatus == 1:
            atts.afterStatus = 0
            atts.afterTimeOut = datetime.now()
            dbase.session.commit()
            print'T`'
            absents()
            return jsonify({'message': 'time out for afternoon'})

         elif atts.morningStatus == 1 and atts.afterStatus == 1:
            atts.morningStatus = 0
            atts.afterStatus = 0
            atts.morningTimeOut = datetime.now()
            atts.afterTimeOut = datetime.now()
            dbase.session.commit()
            print'U`'
            absents()
            return jsonify({'message': 'time out for afternoon and morning'})

      elif now > a7 and now <= o10:
         if employee1:
            if employee1.overtimeInStatus == 0:
               employee1.overtimeInStatus = 1
               employee1.overtimeIn = datetime.now()
               dbase.session.commit()
               return jsonify({'message': 'Overtime time in success'})
            elif employee1.overtimeInStatus == 1:
               employee1.overtimeOut = datetime.now()
               dbase.session.commit()
               return jsonify({'message': 'Overtime time out success'})

   # ////////// ///////////////////////////////IF ID IS EXISTING/////////////////////////////////////////////////////////
   elif atts:
      dates = Attendance.query.filter_by(
          date=datenow).order_by(Attendance.date.desc()).first()
      print dates
      atts = Attendance.query.filter(and_(Attendance.employeeid == empID, Attendance.date == datenow)).order_by(
          Attendance.date.desc()).first()
      # dbase.session.commit()
      # date1 = atts.date
      print "second"
      dates = Attendance.query.filter_by(date=datenow).first()
      employee1 = Overtime.query.filter(and_(
          Overtime.employeeid == empID, Overtime.overtimeStatus == 1, Overtime.overtimeDate == datenow2)).first()

      if dates:
         pass
      else:
         dbase.session.add(attendancenNew)
         dbase.session.commit()
         atts.date = datenow
         print atts.date + 'jfjfjfjfjfjfjfhfnr nvjfnfnhmfn'
         dbase.session.commit()

         print '1234567890-'
         print datenow + "mkmkmkkmkkkmkmkmkkkmkmkmk"
         atts = Attendance.query.filter(
             and_(Attendance.employeeid == empID, Attendance.date == datenow)).order_by(
             Attendance.date.desc()).first()
   # ///////////////////////////////////////////CHECK IF THE DATE IS SAME//////////////////////////////////////
      if atts.date == datenow:
         # ////////////////////////IF DATE IS SAME////////////////////////////#
         print atts.date + 'nabuang siya'
         if now >= m7 and now <= m9:
            if atts.morningStatus == 0 and atts.afterStatus == 0:
               if atts.morningTimeOut is None:
                  atts.morningStatus = 1
                  atts.morningTimeIn = datetime.now()
                  atts.morningDailyStatus = 'not late'
                  print "AAAAAAAAAAAAAAAA"
                  dbase.session.commit()
                  return jsonify({'message': 'not late'})
               else:
                  print'BBBBBBBBBBBBBBBBBBBBB'
                  return jsonify({'message': 'you cannot time in twice'})
            elif atts.morningStatus == 1 and atts.afterStatus == 0:
               print 'CCCCCCCCCCCCCCCC'
               return jsonify({'message': 'no time out at this time'})
            elif atts.morningStatus == 0 and atts.afterStatus == 1:
               if atts.morningTimeOut is None:
                  atts.afterStatus = 0
                  atts.morningStatus = 1
                  atts.afterTimeOut = datetime.now()
                  atts.morningTimeIn = datetime.now()
                  atts.morningDailyStatus = 'not late'
                  dbase.session.commit()
                  print'DDDDDDDDDDDDDDDDDD'
                  return jsonify({'message': 'not late, kindly dont forget to timeout in morning'})
               else:
                  print'EEEEEEEEEEEEEEEEEE'
                  return jsonify({'message': 'you cannot time in twice'})
            elif atts.morningStatus == 1 and atts.afterStatus == 1:
               atts.afterStatus = 0
               atts.afterTimeOut = datetime.now()
               dbase.session.commit()
               print'FFFFFFFFFFFFFFFF'
               return jsonify({'message': 'no time out at this time'})

         elif now > m9 and now <= m12:
            if atts.morningStatus == 0 and atts.afterStatus == 0:
               if atts.morningTimeOut is None:
                  atts.morningStatus = 1
                  atts.lateTotal = 1
                  employee.late = employee.late + 1
                  atts.morningDailyStatus = 'late'
                  atts.morningTimeIn = datetime.now()
                  # atts.morningRemark = wala pa nabutang
                  print 'GGGGGGGGGGGGGGGGGGGGGGGGG'
                  dbase.session.commit()
                  return jsonify({'message': 'late'})
               else:
                  print'HHHHHHHHHHHHHHHHHHHHHHHHHHH'
                  return jsonify({'message': 'you cannot time in twice'})
            elif atts.morningStatus == 1 and atts.afterStatus == 0:
               if atts.morningTimeOut is None:
                  atts.morningStatus = 0
                  atts.morningTimeOut = datetime.now()
                  # atts.morningRemark = wala pa nabutang
                  print 'IIIIIIIIIIIIIIIIII'
                  dbase.session.commit()
                  return jsonify({'message': 'time out'})
               else:
                  print'JJJJJJJJJJJJJJJ'
                  return jsonify({'message': 'you cannot time in twice'})
            elif atts.morningStatus == 0 and atts.afterStatus == 1:
               if atts.morningTimeOut is None:
                  atts.afterStatus = 0
                  atts.morningStatus = 1
                  atts.afterTimeOut = datetime.now()
                  atts.morningTimeIn = datetime.now()
                  atts.morningDailyStatus = 'late'
                  # atts.morningRemark = wala pa nabutang
                  print'KKKKKKKKKKKK'
                  dbase.session.commit()
                  return jsonify({'message': 'late, kindly dont forget to timeout in morning'})
               else:
                  print'LLLLLLLLLLLLLLLLLL'
                  return jsonify({'message': 'you cannot time in twice'})
            elif atts.morningStatus == 1 and atts.afterStatus == 1:
               if atts.morningTimeOut is None:
                  atts.afterStatus = 0
                  atts.morningStatus = 0
                  atts.afterTimeOut = datetime.now()
                  atts.morningTimeOut = datetime.now()
                  dbase.session.commit()
                  print'MMMMMMMMMMMMMMMMMM'
                  return jsonify({'message': 'time out'})
               else:
                  print'NNNNNNNNNNNNNN'
                  return jsonify({'message': 'you cannot time in twice'})
         elif now > m12 and now <= a1:  # 12 -7pm
            if atts.morningStatus == 0 and atts.afterStatus == 0:
               if atts.afterTimeOut is None:
                  atts.afterStatus = 1
                  atts.afterDailyStatus = 'not late'
                  atts.afterTimeIn = datetime.now()
                  # atts.morningRemark = wala pa nabutang
                  print 'OOOOOOOOOOOOOOOOOO'
                  dbase.session.commit()
                  return jsonify({'message': 'time in for afternoon'})
               else:
                  print'PPPPPPPPPPPPPPPPPPPPPPP'
                  return jsonify({'message': 'you cannot time in twice'})
            elif atts.morningStatus == 1 and atts.afterStatus == 0:
               if atts.afterTimeOut is None:
                  atts.morningStatus = 0
                  atts.morningTimeOut = datetime.now()
                  # atts.morningRemark = wala pa nabutang
                  print 'QQQQQQQQQQQQQQQQQQQ'
                  dbase.session.commit()
                  return jsonify({'message': 'time out for morning'})
               else:
                  print'RRRRRRRRRRRRRRR'
                  return jsonify({'message': 'you cannot time in twice'})
            elif atts.morningStatus == 0 and atts.afterStatus == 1:
               print'SSSSSSSSSSSSSSSSSSSSS'
               return jsonify({'message': 'no time out for afternoon at this time'})
            elif atts.morningStatus == 1 and atts.afterStatus == 1:
               atts.morningStatus = 0
               atts.morningTimeOut = datetime.now()
               dbase.session.commit()
               print'TTTTTTTTTTTTTTT'
               return jsonify({'message': 'no time out for afternoon at this time'})
         elif now > a1 and now <= a6:
            if atts.morningStatus == 0 and atts.afterStatus == 0:
               if atts.afterTimeOut is None:
                  atts.afterStatus = 1
                  atts.lateTotal = 1
                  employee.late = employee.late + 1
                  atts.afterDailyStatus = 'late'
                  atts.afterTimeIn = datetime.now()
                  # atts.morningRemark = wala pa nabutang
                  print 'UUUUUUUUUUUUUUUUU'
                  dbase.session.commit()
                  return jsonify({'message': 'late'})
               else:
                  print'VVVVVVVVVVVV'
                  return jsonify({'message': 'you cannot time in twice'})
            elif atts.morningStatus == 1 and atts.afterStatus == 0:
               if atts.afterTimeOut is None:
                  atts.morningStatus = 0
                  atts.afterStatus = 1
                  atts.morningTimeOut = datetime.now()
                  atts.lateTotal = 1
                  employee.late = employee.late + 1
                  atts.afterDailyStatus = 'late'
                  atts.afterTimeIn = datetime.now()
                  # atts.morningRemark = wala pa nabutang
                  print 'WWWWWWWWWWWWWWWWWWWW'
                  dbase.session.commit()
                  return jsonify({'message': '"time in for afternoon." (time out for morning next time,) '})
               else:
                  print'XXXXXXXXXXXXXXX'
                  return jsonify({'message': 'you cannot time in twice'})
            elif atts.morningStatus == 0 and atts.afterStatus == 1:
               atts.afterStatus = 0
               atts.afterTimeOut = datetime.now()
               dbase.session.commit()
               print'YYYYYYYYYYYYYYYY'
               return jsonify({'message': 'time out'})
            elif atts.morningStatus == 1 and atts.afterStatus == 1:
               atts.afterStatus = 0
               atts.morningStatus = 0
               atts.afterTimeOut = datetime.now()
               atts.morningTimeOut = datetime.now()
               dbase.session.commit()
               print'ZZZZZZZZZZZZZZZZZZZZ'
               return jsonify({'message': 'time out'})

         elif now > a6 and now <= a7:
            if employee1.overtimeInStatus == 0:
               employee1.overtimeInStatus = 1
               employee1.overtimeIn = datetime.now()

            if atts.morningStatus == 0 and atts.afterStatus == 0:
               print'R`'
               absents()
               dbase.session.commit()
               return jsonify({'message': 'no time in for this time'})

            elif atts.morningStatus == 1 and atts.afterStatus == 0:
               atts.morningStatus = 0
               atts.morningTimeOut = datetime.now()
               dbase.session.commit()
               print'S`'
               absents()
               return jsonify({'message': 'not time in for afternoon'})

            elif atts.morningStatus == 0 and atts.afterStatus == 1:
               atts.afterStatus = 0
               atts.afterTimeOut = datetime.now()
               dbase.session.commit()
               print'T`'
               absents()
               return jsonify({'message': 'time out for afternoon'})

            elif atts.morningStatus == 1 and atts.afterStatus == 1:
               atts.morningStatus = 0
               atts.afterStatus = 0
               atts.morningTimeOut = datetime.now()
               atts.afterTimeOut = datetime.now()
               dbase.session.commit()
               print'U`'
               absents()
               return jsonify({'message': 'time out for afternoon and morning'})

         elif now > a7 and now <= o10:
            if employee1:
               if employee1.overtimeInStatus == 0:
                  employee1.overtimeInStatus = 1
                  employee1.overtimeIn = datetime.now()
                  dbase.session.commit()
                  return jsonify({'message': 'Overtime time in success'})
               elif employee1.overtimeInStatus == 1:
                  employee1.overtimeOut = datetime.now()
                  dbase.session.commit()
                  return jsonify({'message': 'Overtime time out success'})
   # ///////////////////////////////////////IF DATE IS NOT THE SAME CREATE NEW ATTENDANCE////////////////////////
      else:
         atts = Attendance.query.filter(
             and_(Attendance.employeeid == empID, Attendance.date == datenow)).order_by(
             Attendance.date.desc()).first()
         print "last"
         employee1 = Overtime.query.filter(and_(
             Overtime.employeeid == empID, Overtime.overtimeStatus == 1, Overtime.overtimeDate == datenow2)).first()
         if (now >= m7) and (now <= m9):
            if atts.morningStatus == 0 and atts.afterStatus == 0:
               if atts.morningTimeOut is None:
                  atts.morningStatus = 1
                  atts.morningTimeIn = datetime.now()
                  atts.morningDailyStatus = 'not late'
                  print "9999999999999999999999"
                  dbase.session.commit()
                  return jsonify({'message': 'not late'})
               else:
                  print'8888888888888888888888'
                  return jsonify({'message': 'you cannot time in twice'})
            elif atts.morningStatus == 1 and atts.afterStatus == 0:
               print '777777777777777777777777'
               return jsonify({'message': 'no time out at this time'})
            elif atts.morningStatus == 0 and atts.afterStatus == 1:
               if atts.morningTimeOut is None:
                  atts.afterStatus = 0
                  atts.morningStatus = 1
                  atts.afterTimeOut = datetime.now()
                  atts.morningTimeIn = datetime.now()
                  atts.morningDailyStatus = 'not late'
                  dbase.session.commit()
                  print'66666666666666666666665454565'
                  return jsonify({'message': 'not late, kindly dont forget to timeout in morning'})
               else:
                  print'555555555555555555555555555'
                  return jsonify({'message': 'you cannot time in twice'})
            elif atts.morningStatus == 1 and atts.afterStatus == 1:
               atts.afterStatus = 0
               atts.afterTimeOut = datetime.now()
               dbase.session.commit()
               print'444441254'
               return jsonify({'message': 'no time out at this time'})

         elif now > m9 and now <= m12:
            if atts.morningStatus == 0 and atts.afterStatus == 0:
               if atts.morningTimeOut is None:
                  atts.morningStatus = 1
                  atts.lateTotal = 1
                  employee.late = employee.late + 1
                  atts.morningDailyStatus = 'late'
                  atts.morningTimeIn = datetime.now()
                  # atts.morningRemark = wala pa nabutang
                  print '3'
                  dbase.session.commit()
                  return jsonify({'message': 'late'})
               else:
                  print'2'
                  return jsonify({'message': 'you cannot time in twice'})
            elif atts.morningStatus == 1 and atts.afterStatus == 0:
               if atts.morningTimeOut is None:
                  atts.morningStatus = 0
                  atts.morningTimeOut = datetime.now()
                  # atts.morningRemark = wala pa nabutang
                  print '1'
                  dbase.session.commit()
                  return jsonify({'message': 'time out'})
               else:
                  print'A`'
                  return jsonify({'message': 'you cannot time in twice'})
            elif atts.morningStatus == 0 and atts.afterStatus == 1:
               if atts.morningTimeOut is None:
                  atts.afterStatus = 0
                  atts.morningStatus = 1
                  atts.afterTimeOut = datetime.now()
                  atts.morningTimeIn = datetime.now()
                  atts.morningDailyStatus = 'late'
                  # atts.morningRemark = wala pa nabutang
                  dbase.session.commit()
                  print'B`'
                  return jsonify({'message': 'late, kindly dont forget to timeout in morning'})
               else:
                  print'C`'
                  return jsonify({'message': 'you cannot time in twice'})
            elif atts.morningStatus == 1 and atts.afterStatus == 1:
               if atts.morningTimeOut is None:
                  atts.afterStatus = 0
                  atts.morningStatus = 0
                  atts.afterTimeOut = datetime.now()
                  atts.morningTimeOut = datetime.now()
                  dbase.session.commit()
                  print'D`'
                  return jsonify({'message': 'time out'})
               else:
                  print'E`'
                  return jsonify({'message': 'you cannot time in twice'})
         elif (now > m12) and (now <= a1):  # 12 -7pm
            if atts.morningStatus == 0 and atts.afterStatus == 0:
               if atts.afterTimeOut is None:
                  atts.afterStatus = 1
                  atts.afterDailyStatus = 'not late'
                  atts.afterTimeIn = datetime.now()
                  # atts.morningRemark = wala pa nabutang
                  print 'F`'
                  dbase.session.commit()
                  return jsonify({'message': 'time in for afternoon'})
               else:
                  print'G`'
                  return jsonify({'message': 'you cannot time in twice'})
            elif atts.morningStatus == 1 and atts.afterStatus == 0:
               if atts.afterTimeOut is None:
                  atts.morningStatus = 0
                  atts.morningTimeOut = datetime.now()
                  # atts.morningRemark = wala pa nabutang
                  print 'H`'
                  dbase.session.commit()
                  return jsonify({'message': 'time out for morning'})
               else:
                  print'I`'
                  return jsonify({'message': 'you cannot time in twice'})
            elif atts.morningStatus == 0 and atts.afterStatus == 1:
               print'J`'
               return jsonify({'message': 'no time out for afternoon at this time'})
            elif atts.morningStatus == 1 and atts.afterStatus == 1:
               atts.morningStatus = 0
               atts.morningTimeOut = datetime.now()
               dbase.session.commit()
               print'K`'
               return jsonify({'message': 'no time out for afternoon at this time'})
         elif now > a1 and now <= a6:
            if atts.morningStatus == 0 and atts.afterStatus == 0:
               if atts.afterTimeOut is None:
                  atts.afterStatus = 1
                  atts.lateTotal = 1
                  employee.late = employee.late + 1
                  atts.afterDailyStatus = 'late'
                  atts.afterTimeIn = datetime.now()
                  # atts.morningRemark = wala pa nabutang
                  print 'L`'
                  dbase.session.commit()
                  return jsonify({'message': 'late'})
               else:
                  print'M`'
                  return jsonify({'message': 'you cannot time in twice'})
            elif atts.morningStatus == 1 and atts.afterStatus == 0:
               if atts.afterTimeOut is None:
                  atts.morningStatus = 0
                  atts.afterStatus = 1
                  atts.morningTimeOut = datetime.now()
                  atts.lateTotal = 1
                  employee.late = employee.late + 1
                  atts.afterDailyStatus = 'late'
                  atts.afterTimeIn = datetime.now()
                  # atts.morningRemark = wala pa nabutang
                  print 'N`'
                  dbase.session.commit()
                  return jsonify({'message': 'time out'})
               else:
                  print'O`'
                  return jsonify({'message': 'you cannot time in twice'})
            elif atts.morningStatus == 0 and atts.afterStatus == 1:
               atts.afterStatus = 0
               atts.afterTimeOut = datetime.now()
               dbase.session.commit()
               print'P`'
               return jsonify({'message': 'time out'})
            elif atts.morningStatus == 1 and atts.afterStatus == 1:
               atts.afterStatus = 0
               atts.morningStatus = 0
               atts.afterTimeOut = datetime.now()
               atts.morningTimeOut = datetime.now()
               dbase.session.commit()
               print'Q`'
               return jsonify({'message': 'time out'})

         elif now > a6 and now <= a7:
            if employee1.overtimeInStatus == 0:
               employee1.overtimeInStatus = 1
               employee1.overtimeIn = datetime.now()

            if atts.morningStatus == 0 and atts.afterStatus == 0:
               print'R`'
               absents()
               dbase.session.commit()
               return jsonify({'message': 'no time in for this time'})

            elif atts.morningStatus == 1 and atts.afterStatus == 0:
               atts.morningStatus = 0
               atts.morningTimeOut = datetime.now()
               dbase.session.commit()
               print'S`'
               absents()
               return jsonify({'message': 'not time in for afternoon'})

            elif atts.morningStatus == 0 and atts.afterStatus == 1:
               atts.afterStatus = 0
               atts.afterTimeOut = datetime.now()
               dbase.session.commit()
               print'T`'
               absents()
               return jsonify({'message': 'time out for afternoon'})

            elif atts.morningStatus == 1 and atts.afterStatus == 1:
               atts.morningStatus = 0
               atts.afterStatus = 0
               atts.morningTimeOut = datetime.now()
               atts.afterTimeOut = datetime.now()
               dbase.session.commit()
               print'U`'
               absents()
               return jsonify({'message': 'time out for afternoon and morning'})
         elif now > a7 and now <= o10:
            if employee1:
               if employee1.overtimeInStatus == 0:
                  employee1.overtimeInStatus = 1
                  employee1.overtimeIn = datetime.now()
                  dbase.session.commit()
                  return jsonify({'message': 'Overtime time in success'})
               elif employee1.overtimeInStatus == 1:
                  employee1.overtimeOut = datetime.now()
                  employee1.overtimeInStatus == 2
                  dbase.session.commit()
                  return jsonify({'message': 'Overtime time out success'})
               else:
                  return jsonify({'message': 'Request for overtime '})
            else:
               return jsonify({'message': 'Please request overtime first!'})


def absents():
    datenow1 = datetime.now().strftime("%m%d%Y")
    employs = Employee.query.filter_by(employeestatus=1).all()
    employees = []
    for i in employs:
        employees.append(i.employeeid)

    present = Attendance.query.filter(
        and_(Attendance.date == datenow1, Attendance.absentTotal == 0)).all()
    presents = []

    if present:
        for e in present:
            presents.append(e.employeeid)

        absent = []
        for i in employees:
            # print "this" + str(i)
            for j in presents:
                if i == j:
                    pass
                else:
                    absent.append(i)

        for i in absent:
            v = Attendance.query.filter(
                and_(Attendance.employeeid == i, Attendance.absentTotal == None)).first()
            emp_ = Employee.query.filter_by(employeeid=i).first()
            if v:
                absent = Attendance(employeeid=i)
                dbase.session.add(absent)
                dbase.session.commit()
                absent.absentTotal = 1
                emp_.absent = emp_.absent + 1
                absent.date = datenow1
                dbase.session.commit()
            else:
                pass
        else:
            pass


@app.route('/remark/<string:codes>', methods=['GET', 'POST'])
def add_remarks(codes):
  data = request.get_json()
  ids = Employee.query.filter_by(code=codes).first() 
  print ids
  remarks = Attendance.query.filter_by(employeeid=ids.employeeid).order_by(Attendance.date.desc()).first()
  if remarks.morningDailyStatus == "late":
    if remarks.morningRemark is None:
      remarks.morningRemark = data['reason']
      dbase.session.commit()
      return jsonify({'message': 'Remark added'})
    else:
      pass
  elif remarks.afterDailyStatus == "late":
    if remarks.afterRemark is None:
      remarks.afterRemark = data['reason']
      dbase.session.commit()
      return jsonify({'message': 'Remark added'})
    else:
      pass


@app.route('/autoTimeOut/', methods=['GET', 'POST'])
def auto_TimeOut():
  timeout = Overtime.query.filter(and_(
      Overtime.overtimeid == 1, Overtime.overtimeDate == lgdate).order_by(Overtime.overtimeDate.desc())).all()
  if timeout is None:
    pass
  else:
    for i in timeout:
      i.overtimeInStatus = 0
      dbase.session.commit()


@app.route('/overtime/request', methods=['POST'])
def request_overtime():
   data = request.get_json()
   employee = Employee.query.filter_by(code=data['code']).first()
   if not employee:
        return jsonify({'message': 'Employee not found'})
   overtime = Overtime.query.filter(and_(Overtime.employeeid == employee.employeeid,
                                         Overtime.overtimeStatus == 1, Overtime.overtimeDate == data['dates'])).first()
   if overtime:
       return jsonify({'message': 'Request already sent, Please wait for the admin to approve'})
   else:
       dates = str(data['dates'])
       y, m, d = dates.split("-")
       dates = dt.date(int(y), int(m), int(d))
       datetostring = dates.strftime("%m%d%Y")
       datenow = datetime.now().strftime("%m%d%Y")
       if datetostring >= datenow:
            if dates is not None:
                new_overtime = Overtime(
                    employeeid=employee.employeeid, overtimeDate=dates)
                dbase.session.add(new_overtime)
                dbase.session.commit()
                return jsonify({'message': 'Request Created'})
       else:
            return jsonify({'message': 'Date requested is not valid'})


@app.route('/view/overtime/requests', methods=['GET'])
@login_required
@cross_origin(allow_headers=['Content-Type'])
def view_requests():
   overtime1 = Overtime.query.filter_by(overtimeStatus=0).all()
   print(overtime1)
   overtimers = []
   if not overtime1:
       print('ddsdsdsdsd if')
       return jsonify({'employee': overtimers})
   else:

       print('else')
       for overtimee in overtime1:
           print('ovahtime')
           employee = Employee.query.filter_by(
               employeeid=overtimee.employeeid).first()
           employee_data = {}
           employee_data['name'] = employee.fname + \
               " " + employee.mname + " " + employee.lname
           employee_data['id'] = str(employee.employeeid)
           employee_data['date'] = str(overtimee.overtimeDate)
           overtimers.append(employee_data)
       return jsonify({'employee': overtimers})
   print('random return')
   return jsonify({'employee': overtimers})


@app.route('/approve/request', methods=['POST'])
@login_required
@cross_origin(allow_headers=['Content-Type'])
def approve():
   data = request.get_json()
   overtime = Overtime.query.filter(and_(
       Overtime.overtimeStatus == 0, Overtime.employeeid == int(data['id']))).first()
   emp_ = Employee.query.filter_by(employeeid=data['id']).first()
   if overtime is None:
       return jsonify({'message': 'Error'})
   else:
       overtime.overtimeStatus = 1
       overtime.overtimeTotal = 1
       emp_.overtimes = emp_.overtimes + 1
       dbase.session.commit()
       name = Employee.query.filter_by(employeeid=data['id']).first()
       msg = name.fname + " " + name.lname + " overtime request has been approved"
       logmessage = Logs(details=msg, log_date=lgdate)
       dbase.session.add(logmessage)
       dbase.session.commit()
       logsid = Logs.query.filter_by(
           logStatus=0).order_by(desc(Logs.logID)).first()
       logsid.logStatus = 1
       logsid.counter = 1
       dbase.session.commit()
       return jsonify({'message': 'Overtime approved successfuly!'})


@app.route('/decline/request', methods=['POST'])
@login_required
@cross_origin(allow_headers=['Content-Type'])
def decline():
   data = request.get_json()
   overtime = Overtime.query.filter(and_(Overtime.overtimeStatus == 0, Overtime.employeeid == int(
       data['id']))).order_by(Overtime.overtimeDate.desc()).first()
   if not overtime:
      return jsonify({'message': 'Error'})
   else:
      overtime.overtimeStatus = 2
      dbase.session.commit()
      name = Employee.query.filter_by(employeeid=data['id']).first()
      msg = name.fname + " " + name.lname + " overtime request has been declined"
      logmessage = Logs(details=msg, log_date=lgdate)
      dbase.session.add(logmessage)
      dbase.session.commit()
      logsid = Logs.query.filter_by(
          logStatus=0).order_by(desc(Logs.logID)).first()
      logsid.logStatus = 1
      logsid.counter = 1
      dbase.session.commit()
      return jsonify({'message': 'Overtime declined successfuly!'})


@app.route('/view/logs', methods=['GET'])
def notifications():
    log = Logs.query.filter(and_(Logs.logStatus == 1, Logs.counter == 1)).all()
    count = 0
    if not log:
        return jsonify({'message': 'No logs to show', 'count': count})

    logs = []
    for i in log:
        log_data = {}
        log_data['logdetails'] = i.details
        logs.append(log_data)
        count = count + 1

    return jsonify({'Notification': logs, 'count': count})


@app.route('/view/admin/logs', methods=['GET'])
@login_required
@cross_origin("*")
def view_logs():
    log = Logs.query.all()
    if not log:
        return jsonify({'message': 'No logs to show'})
    logs = []
    for i in log:
        log_data = {}
        log_data['logdetails'] = i.details
        log_data['logdate'] = i.log_date
        logs.append(log_data)
    return jsonify({'adminlogs': logs})

# @app.route('/unseencounter', methods=['GET'])
# def counterunseen():
#     log = Logs.query.count(counter=1)
#     if not log:
#         return jsonify({'message': 'No logs to show'})
#     else:
#         return jsonify({'adminlogs': log})


@app.route('/seen', methods=['GET'])
def counterunseen():
    log = Logs.query.filter_by(counter=1).all()
    if not log:
        return jsonify({'message': 'No logs to show'})
    else:
        for i in log:
            i.counter = 0
            dbase.session.commit()
        return jsonify({'adminlogs': 'done'})

@app.route('/autotimeout/', methods=['POST'])
def otTimeout():
    nowtime = datetime.now().strftime("%H%M")
    # nowdate = datetime.now().strftime("%Y-%d-%m")
    timeout = "2200"
    timeout1 = "2300"
    emp = Overtime.query.filter_by(overtimeInStatus=1).all()
    if emp:
        if nowtime >= timeout and nowtime <= timeout1:
            for i in emp:
                i.overtimeInStatus = 2
                dbase.session.commit()
            return jsonify({"message": "timeout "})
    else:
        pass
        return jsonify({"message": 'not time yet'})
    return jsonify({"message": nowtime})

@app.route('/view/overtimelog', methods=['GET'])
@login_required
@cross_origin("*")
def overtimelog():
   otlog = Overtime.query.all()
   logs = []
   if not otlog:
      return jsonify({'Overtimelog': logs})
   for ot in otlog:
      overtime_data = {}
      print(ot)
      print(ot.employeeid)
      name = Employee.query.filter_by(employeeid=ot.employeeid).first()
      overtime_data['name'] = name.fname + " " + name.mname + " " + name.lname
      if ot.overtimeIn is None:
         overtime_data['timein'] = "None"
      else:
         overtime_data['timein'] = (ot.overtimeIn).strftime("%Y-%b-%d %I:%M %p")
      if ot.overtimeOut is None:
         overtime_data['timeout'] = "None"
      else:
         overtime_data['timeout'] = (ot.overtimeOut).strftime("%Y-%b-%d %I:%M %p")
      overtime_data['date'] = str(ot.overtimeDate)
      logs.append(overtime_data)
   return jsonify({'Otlog': logs})

@app.route('/timeInOut/logs', methods=['GET'])
def timeInOut():
   summary = Attendance.query.all()
   employees = []
   for employee in summary:
       name = Employee.query.filter_by(employeeid=employee.employeeid).first()
       employee_data = {}
       employee_data['fname'] = name.fname
       if employee.morningTimeIn is None:
          employee_data['morningTimeIn'] = "None"
       else:
          employee_data['morningTimeIn'] = (employee.morningTimeIn).strftime("%Y-%b-%d %I:%M %p")
       
       if employee.afterTimeIn is None:
          employee_data['afterTimeIn'] = "None"
       else:
          employee_data['afterTimeIn'] = (employee.afterTimeIn).strftime("%Y-%b-%d %I:%M %p")
       employees.append(employee_data)
   return jsonify({'Employee': employees})