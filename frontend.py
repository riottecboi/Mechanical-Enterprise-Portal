from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_env import MetaFlaskEnv
from datetime import timedelta
from app.utils import logger
from functools import wraps
import requests, os

app = Flask(__name__)

class Configuration(metaclass=MetaFlaskEnv):
    SECRET_KEY = "supersecretkey"
    BASE_URL = 'http://127.0.0.1:8080'

try:
    app.config.from_pyfile('settings.cfg')
except FileNotFoundError:
    app.config.from_object(Configuration)

csrf = CSRFProtect(app)

app.config['SESSION_COOKIE_SECURE']=True
app.permanent_session_lifetime = timedelta(minutes=30)

@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)
    session.modified = True

@app.errorhandler(CSRFError)
def handle_csrf_error():
    flash('Phiên đăng nhập hết hạn', 'warning')
    return redirect(url_for('login'))

@app.errorhandler(500)
def internal_error(error):
    flash('Phiên đăng nhập hết hạn', 'warning')
    return redirect(url_for('login'))

def session_checker(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get('apikey') is None:
            flash('Phiên đăng nhập hết hạn', 'warning')
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return wrapper

@app.route('/', methods=['GET'])
def index():
    return redirect(url_for('login'), code=302)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if session.get('apikey') is not None:
            return redirect(url_for('menu'))
        return render_template('index.html')
    username = request.form.get('username')
    password = request.form.get('password')
    try:
        r_login = requests.post(f"{app.config['BASE_URL']}/login", json={'username': username, 'password': password})
        response = r_login.json()
        if r_login.status_code == 200:
            session['username'] = username
            session['apikey'] = response['apikey']
            session['admin'] = response['is_admin']
            session['edit'] = response['is_edit']
            session['view'] = response['is_view']
        else:
            flash('Tên đăng nhập / mật khẩu sai', 'error')
            logger.info(response['message'])
            return redirect(url_for('login'))
    except Exception as e:
        logger.info('Exception occurred: {}'.format(str(e)))
        return render_template('index.html')

    return redirect(url_for('menu'))

@app.route('/forgot', methods=['GET'])
def forgot():
    flash('Vui lòng liên hệ ban quản trị để được cấp lại mật khẩu', 'info')
    return redirect(url_for('login'))

@app.route('/menu', methods=['GET', 'POST'])
@session_checker
def menu():
    try:
        userAdmin = session.get('admin')
        userAPIkey = session.get('apikey')
        userInfo = requests.get(f"{app.config['BASE_URL']}/info", params={'apikey': userAPIkey}, headers={'X-SECRET-KEY': session.get('apikey')})
        if userAdmin is True:
            getAllusers = requests.get(f"{app.config['BASE_URL']}/allUser", headers={'X-ADMIN-SECRET-KEY': session.get('apikey')})
            response = getAllusers.json()
            if getAllusers.status_code == 200:
                users = response
                return render_template('dashboard.html', users=users, cur_user=userInfo.json(), userType='Administrator')
        if userAdmin is False:
            return render_template('profile.html', cur_user=userInfo.json(), userType='User', page='user')
    except Exception as e:
        abort(500)

@app.route('/adminInfo', methods=['GET'])
@session_checker
def adminInfo():
    return render_template('profile.html',  userType='Administrator', page='admin')

@app.route('/changepassword', methods=['POST'])
@session_checker
def changepassword():
    currentpw = request.form.get('currentpw')
    newpw = request.form.get('newpw')
    re_newpw = request.form.get('re-newpw')
    json_d = {
         'username': session.get('username'),
         'currentpw': currentpw,
         'password': newpw,
         'confirm_password': re_newpw
    }
    changePWD = requests.put(f"{app.config['BASE_URL']}/changepassword", json=json_d,
                            headers={'X-ADMIN-SECRET-KEY': session.get('apikey')})
    if changePWD.status_code == 200:
        flash('Cập nhật tài khoản thành công', 'info')
        return redirect(url_for('adminInfo'))
    else:
        if changePWD.status_code == 304:
            flash('Tài khoản chưa được cập nhật', 'warning')
        else:
            flash('Tài khoản người dùng không tồn tại', 'error')
        return redirect(url_for('adminInfo'))

@app.route('/adduser', methods=['GET','POST'])
@session_checker
def adduser():
    try:
        if request.method == 'POST':
            msnv = request.form.get('msnv')
            fullname = request.form.get('fullname')
            dob = request.form.get('dob')
            gender = request.form.get('gender')
            tel = request.form.get('tel')
            idcard = request.form.get('idcard')
            ethnic = request.form.get('ethnic')
            nationality = request.form.get('nationality')
            address = request.form.get('address')
            ward = request.form.get('ward')
            district = request.form.get('district')
            city = request.form.get('city')
            group = request.form.get('group')
            sector = request.form.get('sector')
            title = request.form.get('title')
            position = request.form.get('position')
            unit = request.form.get('unit')
            newpw = request.form.get('newpw')
            re_newpw = request.form.get('re-newpw')
            if newpw == re_newpw:
                json_d = {
                    'username': msnv,
                    'password': newpw,
                    'confirm_password': re_newpw,
                    'msnv': msnv,
                    'fullname': fullname,
                    'department': unit,
                    'gender': gender,
                    'vehicle': title,
                    'position': position,
                    'dob': dob,
                    'sector': sector,
                    'tel': tel,
                    'id_card': idcard,
                    'ethnic': ethnic,
                    'nationality': nationality,
                    'address': address,
                    'ward': ward,
                    'district': district,
                    'city': city,
                    'target_group': group
                }
                r_signup = requests.post(f"{app.config['BASE_URL']}/signup",  json=json_d, headers={'X-ADMIN-SECRET-KEY': session.get('apikey')})
                if r_signup.status_code == 200:
                    flash('Tạo account mới thành công', 'info')
                    return redirect(url_for('adduser'))
                else:
                    if r_signup.status_code == 304:
                        flash('Mật khẩu không trùng khớp', 'warning')
                    else:
                        flash('Tài khoản người dùng đã tồn tại', 'error')
                    return redirect(url_for('adduser'))
        return render_template('adduser.html', userType='Administrator')
    except Exception as e:
        abort(500)
@app.route('/edit', methods=['POST'])
@session_checker
def edit():
    try:
        msnv = request.form.get('msnv')
        fullname = request.form.get('fullname')
        dob = request.form.get('dob')
        gender = request.form.get('gender')
        tel = request.form.get('tel')
        idcard = request.form.get('idcard')
        ethnic = request.form.get('ethnic')
        nationality = request.form.get('nationality')
        address = request.form.get('address')
        ward = request.form.get('ward')
        district = request.form.get('district')
        city = request.form.get('city')
        group = request.form.get('group')
        sector = request.form.get('sector')
        title = request.form.get('title')
        position = request.form.get('position')
        unit = request.form.get('unit')
        currentpw = request.form.get('currentpw')
        newpw = request.form.get('newpw')
        re_newpw = request.form.get('re-newpw')
        json_d = {
            'username': msnv,
            'currentpw': currentpw,
            'password': newpw,
            'confirm_password': re_newpw,
            'msnv': msnv,
            'fullname': fullname,
            'department': unit,
            'gender': gender,
            'vehicle': title,
            'position': position,
            'dob': dob,
            'sector': sector,
            'tel': tel,
            'id_card': idcard,
            'ethnic': ethnic,
            'nationality': nationality,
            'address': address,
            'ward': ward,
            'district': district,
            'city': city,
            'target_group': group
        }
        r_signup = requests.put(f"{app.config['BASE_URL']}/edit", json=json_d,
                                 headers={'X-ADMIN-SECRET-KEY': session.get('apikey')})
        if r_signup.status_code == 200:
            flash('Cập nhật tài khoản thành công', 'info')
            return redirect(url_for('user', id=json_d['username']))
        else:
            if r_signup.status_code == 304:
                flash('Tài khoản chưa được cập nhật', 'warning')
            else:
                flash('Tài khoản người dùng không tồn tại', 'error')
            return redirect(url_for('user', id=json_d['username']))
    except Exception as e:
        abort(500)

@app.route('/user', methods=['GET'])
@session_checker
def user():
    if 'id' in request.args:
        userAdmin = session.get('admin')
        if userAdmin is True:
            type = 'Administrator'
        else:
            type = 'User'
        userInfo = requests.get(f"{app.config['BASE_URL']}/info", params={'username': request.args.get('id')},
                            headers={'X-SECRET-KEY': session.get('apikey')})
        if userInfo.status_code == 404:
            flash('Không thể lấy được thông tin người dùng', 'error')
            return redirect(url_for('menu'))
        userinfo = userInfo.json()
        if type == 'User':
            if userinfo['msnv'] != session.get('username'):
                flash('Không có quyền để xem thông tin người dùng', 'error')
                return redirect(url_for('menu'))
        return render_template('profile.html', cur_user=userinfo, userType=type, page='user')
    else:
        flash('Không thể lấy được thông tin người dùng', 'error')
        return redirect(url_for('menu'))

@app.route('/delete', methods=['POST'])
@session_checker
def delete():
    if 'id' in request.args:
        userDel = requests.delete(f"{app.config['BASE_URL']}/delUser", params={'username': request.args.get('id')},
                                  headers={'X-ADMIN-SECRET-KEY': session.get('apikey')})
        if userDel.status_code == 200:
            flash('Xóa tài khoản {} thành công'.format(request.args.get('id')), 'info')
            return redirect(url_for('menu'))
        else:
            flash('Xóa tài khoản {} không thành công'.format(request.args.get('id')), 'warning')
            return redirect(url_for('menu'))
    else:
        flash('Không thể lấy được thông tin người dùng', 'error')
        return redirect(url_for('menu'))

# @app.route('/adminDelete', methods=['POST'])
# @session_checker
# def admindelete():
#

@app.route('/excelupdate', methods=['GET','POST'])
@session_checker
def excelupdate():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            path = f"/tmp/{uploaded_file.filename}"
            with open(path, 'wb') as e:
                e.write(uploaded_file.read())
            try:
                userAccounts = requests.post(f"{app.config['BASE_URL']}/signupMultipleUserbyExcel",  params={'filepath': path}, headers={'X-ADMIN-SECRET-KEY': session.get('apikey')})
                if userAccounts.status_code == 200:
                    users = userAccounts.json()
                    return redirect(url_for('menu'))
            except Exception as e:
                os.remove(path)
                return redirect(url_for('excelupdate'))
    return render_template('upload.html')

@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    logger.info('Logout successful')
    return redirect(url_for('login'))

@app.route('/testTemplate', methods=['GET'])
def test():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run()