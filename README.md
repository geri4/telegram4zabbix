# Telegram bot for Zabbix

## Requirments
* Zabbix server
* Nginx
* Python 2.7
* SSL certificate

## Installation

Installation steps testing on Ubuntu 14.04 and Debian 8

1. Install software
`apt-get install python-flask python-pip nginx uwsgi uwsgi-plugin-python`

2. Create virtualhost file /etc/nginx/sites-enabled/telegram:
```
upstream flask_serv {
    server unix:/tmp/flask.sock;
}

server {
    listen 443;
    ssl on;
    ssl_certificate /etc/ssl/private/geri4.ru.crt;
    ssl_certificate_key /etc/ssl/private/geri4.ru.key;
    server_name telegram.geri4.ru;

    location / {
        uwsgi_pass flask_serv;
        include uwsgi_params;
    }
}
```

3. Create uWSGI application file /etc/uwsgi/apps-enabled/flask.xml:
```
<uwsgi>
    <socket>/tmp/flask.sock</socket>
    <pythonpath>/opt/telegram-bot/</pythonpath>
    <module>telegramhook:app</module>
    <plugins>python27</plugins>
</uwsgi>
```
