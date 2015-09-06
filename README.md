# Telegram bot for Zabbix

## Requirments
* Zabbix server
* Nginx
* Python 2.7
* SSL certificate

## Installation

Installation steps testing on Ubuntu 14.04 and Debian 8

#### 1.Register telegram bot and save HTTP API key

#### 2.Install software  
`apt-get install python-flask python-pip nginx uwsgi uwsgi-plugin-python`

#### 3.Create virtualhost file /etc/nginx/sites-enabled/telegram:
```
upstream flask_serv {
    server unix:/tmp/flask.sock;
}

server {
    listen 443;
    ssl on;
    ssl_certificate /etc/ssl/private/example.com.crt;
    ssl_certificate_key /etc/ssl/private/example.com.key;
    server_name telegram.example.com;

    location / {
        uwsgi_pass flask_serv;
        include uwsgi_params;
    }
}
```

#### 4.Create uWSGI application file /etc/uwsgi/apps-enabled/flask.xml:
```
<uwsgi>
    <socket>/tmp/flask.sock</socket>
    <pythonpath>/opt/telegram4zabbix/</pythonpath>
    <module>telegramhook:app</module>
    <plugins>python27</plugins>
</uwsgi>
```

#### 5.Clone repository and other things:
```
cd /opt
git clone https://github.com/Geri4/telegram4zabbix.git
chown -R www-data: /opt/telegram4zabbix
chmod ug+rwx -R telegram-bot/
pip install pickledb simplejson pyzabbix python-telegram-bot
touch /var/log/telegram.log
chown zabbix: /var/log/telegram.log
```

#### 5.Edit variables in /opt/telegram4zabbix/*.py

#### 6.Restart daemons:
```
service uwsgi restart
service nginx reload
```

#### 7.Set webhook: `curl https://telegram.example.com/set_webhook`

#### 8.Add new mediatype in zabbix server, point to /opt/telegram4zabbix/telegram-sent.py

#### 9.All done! Send message to your telegram bot and enter password.
