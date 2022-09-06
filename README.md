# instant_chatting_system_flask_api
## 介紹
用Flask結合SocketIO及VUE3搭建一個簡易版即時聊天系統
![](https://i.imgur.com/IV5JJYh.png)
![](https://i.imgur.com/TGCNHhn.png)


## 使用技術及工具


|    前端   | 後端       | 雲端 |
| -------- | --------| -------- |
| VUE3     |Python-Flask|AWS EC2(Ubantu 20.04)
  VUEX     |Flask-SocketIO|Nginx|
  less



## 在AWS EC2佈署
開啟EC2執行個體並使用金鑰連線
```
 ssh -i "[金鑰名].pem" ubuntu@[公有 IPv4 DNS]
```
更新下載源
```
$ sudo apt update
```
新增資料夾並從git pull respo
```
$ mkdir chatsystem
$ cd chatsystem
$ git init
$ git remote add origin [git respo網址]
$ git pull origin main
```
創建虛擬環境並安裝相關套件
```
$ python3 -m venv venv
$ source venv/bin/activate
$ pip3 install -r requirements.txt
```
安裝gunicorn
```
$pip3 install gunicorn
```
執行gunicorn
```
$ gunicorn --worker-class eventlet -w 1 app:app
```
nginx反向代理設定(支持SocketIO負載平衡)
```
upstream socketio_nodes {
    ip_hash;

    server 127.0.0.1:5000;
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
    # to scale the app, just add more nodes here
}

server {
    listen 80;
    server_name [server name];

    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:5000;
    }

    location /static {
        alias <path-to-your-application>/static;
        expires 30d;
    }

    location /socket.io {
        include proxy_params;
        proxy_http_version 1.1;
        proxy_buffering off;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_pass http://socketio_nodes/socket.io;
    }
}
```
