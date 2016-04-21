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

#### 3.Create nginx virtualhost file /etc/nginx/sites-enabled/telegram:
```
upstream telegram4zabbix {
    server 192.168.78.4:9090;
}

server {
    listen       80;
    listen       443 ssl;
    server_name  telegram.geri4.ru;
    charset  utf-8;
    if ( $scheme = "http" ) {
         rewrite ^/(.*)$     https://$host/$1 permanent;
    }
    access_log  /var/log/nginx/$host.access.log;
    keepalive_timeout   70;

    #HTTPS
    ssl_certificate      /etc/letsencrypt/live/geri4.ru/fullchain.pem;
    ssl_certificate_key  /etc/letsencrypt/live/geri4.ru/privkey.pem;
    ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets on;
    ssl_session_ticket_key current.key;
    ssl_session_ticket_key prev.key;
    ssl_session_ticket_key prevprev.key;
    ssl_prefer_server_ciphers on;
    ssl_ciphers 'ECDH+AESGCM:ECDH+AES256:ECDH+AES128:DH+3DES:!ADH:!AECDH:!MD5';
    ssl_dhparam /etc/nginx/dhparam.pem;
    ssl_stapling on;
    ssl_stapling_verify on;
    ssl_trusted_certificate /etc/letsencrypt/live/geri4.ru/fullchain.pem;
    resolver 8.8.8.8 8.8.4.4;

    location /.well-known/acme-challenge {
        root /var/www/letsencrypt;
    }

    location / {
        proxy_pass http://telegram4zabbix;
        proxy_http_version 1.1;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
```

#### 4.Create uWSGI application file /etc/uwsgi/apps-enabled/telegram4zabbix.ini:
```
[uwsgi]
http-socket = :9090
pythonpath = /opt/telegram4zabbix/
module = telegramhook:app
plugins = python27
```

#### 5.Clone repository and other things:
```
cd /opt
git clone https://github.com/Geri4/telegram4zabbix.git
chown -R www-data: /opt/telegram4zabbix
chmod ug+rwx -R telegram4zabbix
pip install pickledb simplejson pyzabbix python-telegram-bot
touch /var/log/telegram.log
chown zabbix: /var/log/telegram.log
```

#### 5.Create file /opt/telegram4zabbix/config.py and add following variables:
```
TelegramBotToken='164444419:BBERDQsjJBG_lx8qPQsAFLDCMIc1XxhINlw'
ZabbixServerUrl='https://zabbix.example.com'
ZabbixUsername='gerasimov'
ZabbixPassword='qwerty123'
DBFile='/opt/telegram4zabbix/telegram.db'
WebHookUrl='https://telegram.example.org/hook'
ChatPassword='verysecret'
LogFile='/var/log/telegram.log'
```

#### 6.Restart daemons:
```
service uwsgi restart
service nginx reload
```

#### 7.Set webhook: `curl https://telegram.example.com/set_webhook`

#### 8.Add new mediatype in zabbix server.
1)Create link telegram-sent script on zabbix default alert folder: `ln -s /opt/telegram4zabbix/telegram-sent.py /usr/lib/zabbix/alertscripts/telegram-sent.py`   
2)Go to Administration->Media types->Create media type   
3)Set following:    
```
Name='Telegram'
Type='Script'
Script name='telegram-sent.py'
Script parameters:
{ALERT.SENDTO}
{ALERT.SUBJECT}
{ALERT.MESSAGE}
```
4) Add new media to zabbix user from which you need receive alerts, in 'Sent to' field write any address.   
5) Create Action in zabbix, open Configuration->Actions->Create action, set following:
Action tab:
```
Name: Telegram
Default subject: {TRIGGER.STATUS}: {TRIGGER.NAME}
Default message: 
{TRIGGER.STATUS}: {TRIGGER.NAME}
Host: {HOSTNAME}
Trigger severity: {TRIGGER.SEVERITY}
Original event ID: {EVENT.ID}

Recovery subject: {TRIGGER.STATUS}: {TRIGGER.NAME}
Recovery message:
{TRIGGER.STATUS}: {TRIGGER.NAME}
Host: {HOSTNAME}
Trigger severity: {TRIGGER.SEVERITY}
Original event ID: {EVENT.ID}
```
Conditions tab:
```
Type of calculation: And/Or
Conditions:
Maintenance status not in maintenance
Trigger value = PROBLEM
```
Operations tab:
Add step that send telegram message to specified zabbix users or groups.

#### 9.All done! Send message to your telegram bot and enter password.
