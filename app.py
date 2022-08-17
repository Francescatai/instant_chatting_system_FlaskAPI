from flask import Flask, request, send_from_directory, url_for, render_template
from flask_socketio import SocketIO, emit
# 生成頭像
from flask_avatars import Avatars, Identicon
import os
from hashlib import md5

from utils import restful

BAS_DIR = os.path.dirname(__file__)

app = Flask(__name__)
app.config['AVATARS_SAVE_PATH'] = os.path.join(BAS_DIR, "media", "avatars")

# cors_allowed_origins="*":允許所有跨域訪問
socketio = SocketIO(app, cors_allowed_origins="*")

avatars = Avatars(app)

online_users = []


@app.route("/")
def index():
    return render_template("index.html")


# 取得頭像
@app.route('/media/avatars/<path:filename>')
def get_avatar(filename):
    return send_from_directory(app.config['AVATARS_SAVE_PATH'], filename)


@socketio.on("connect")
def connect():
    print("ip:" + request.remote_addr)
    # socketIO隨機分配的用戶id
    print("sid:" + request.sid)


@socketio.on("disconnect")
def disconnect():
    sid = request.sid
    for user in online_users:
        if user['sid'] == sid:
            online_users.remove(user)
            emit("user offline", {"user": user}, broadcast=True)
            break


@socketio.on("login")
def login(data):
    username = data.get("username")
    if not username:
        return restful.params_error("請輸入用戶名")
    for user in online_users:
        if user['username'] == username:
            return restful.params_error("此用戶名已經存在")
    filenames = Identicon().generate(md5(username.encode("utf-8")).hexdigest())
    avatar_name = filenames[2]
    avatar_url = url_for("get_avatar", filename=avatar_name)
    user = {"username": username, "ip": request.remote_addr, "avatar": avatar_url, "sid": request.sid}
    users = online_users.copy()
    online_users.append(user)
    emit("user online", {"user": user}, broadcast=True)
    return restful.ok(data={"user": user, "online_users": users})


@socketio.on("send message")
def send_message(data):
    to = data.get('to')
    if not to:
        return restful.params_error("請選擇傳送用戶")
    for user in online_users:
        if user['sid'] == to:
            break
    else:
        return restful.params_error("此用戶不存在或已下線")
    message = data.get('message')
    if not message:
        return restful.params_error("請輸入訊息")
    # room:發送給指定對象
    emit("receive message", {"message": message, "from": request.sid}, room=[to])
    return restful.ok()


if __name__ == '__main__':
    socketio.run(app, debug=True)
