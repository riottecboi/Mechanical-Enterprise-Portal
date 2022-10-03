from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from flask_wtf.csrf import CSRFProtect
from flask_env import MetaFlaskEnv
from datetime import timedelta
from app.utils import logger
import requests

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

@app.errorhandler(403)
def session_timeout(error):
    flash('Phiên đăng nhập hết hạn', 'warning')
    return redirect(url_for('login'), 302)

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
        r_login = requests.post(f"{app.config['BASE_URL']}/login", json={'username': int(username), 'password': password})
        response = r_login.json()
        if r_login.status_code == 200:
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
def menu():
    userAdmin = session.get('admin')
    userAPIkey = session.get('apikey')
    if userAPIkey is None:
        abort(403, description="Phiên đăng nhập hết hạn")
    userInfo = requests.get(f"{app.config['BASE_URL']}/info", params={'apikey': userAPIkey}, headers={'X-SECRET-KEY': session.get('apikey')})
    if userAdmin is True:
        getAllusers = requests.get(f"{app.config['BASE_URL']}/allUser", headers={'X-ADMIN-SECRET-KEY': session.get('apikey')})
        response = getAllusers.json()
        if getAllusers.status_code == 200:
            users = response
            return render_template('dashboard.html', users=users, cur_user=userInfo.json(), userType='Administrator')
    if userAdmin is False:
        return render_template('profile.html', cur_user=userInfo.json(), userType='User')

@app.route('/adminInfo', methods=['GET'])
def adminInfo():
    userAPIkey = session.get('apikey')
    userInfo = requests.get(f"{app.config['BASE_URL']}/info", params={'apikey': userAPIkey},
                            headers={'X-SECRET-KEY': session.get('apikey')})
    return render_template('profile.html', cur_user=userInfo.json(), userType='Administrator')

@app.route('/adduser', methods=['GET','POST'])
def adduser():
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
                flash('Không tạo được account', 'error')
                return redirect(url_for('adduser'))
    return render_template('adduser.html', userType='Administrator')

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