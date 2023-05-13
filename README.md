# MiddleMan - Flask application for custom web request interception and moderation

Run this application, capture web requests and pass them to another endpoint,
or moderate the request parameters first, using custom written functions (optionally adding them to a Redis queue).

## Usage
1). in [config.json](config.json) define optional log and redis settings, as well as any of the services you would like to run.
Each of the services will be available as an endpoint at [address>]/[service] e.g. http://127.0.0.1/myService

2). For each of the services you should specify path keywords that suggest the parameters need processing. 
   If there comes a request to [address]\[service]\[~path] the parameters will be subjected to all of the processing functions (**processors**) defined in the [config.json](config.json) under that service and that path. 
   
2a). For each **processor** named in the config, a function with the same name should exist in the [processors.py](processors.py). Each of those functions should have params and data as an input as well as the output.

2b). If the processing functions for said path should be redis queued, specify the parameter **redis** under that path in [config.json](config.json) and set it to **1**. 
Aslo make sure that the Redis queuing is set to available for the whole project (parameter **on** is set to **1** under the main **redis** definition inside the [config.json](config.json)).

3). For each service you must provide a **target** url, to which the service will pass the request, after the params and data is processed. If no processing is defined, the params will be sent as received.

## Usage example
Some of the usage is already defined within the project in [config.json](config.json):

    {
      "log": "", 
      "redis": {
        "url": "redis://127.0.0.1",
        "port": "6379",
        "on": 1
      },
      "services": {
        "solr": {
          "paths" : {
            "select": {
              "processors": ["sort_default"]
            },
            "update" : {
              "processors": ["index_media"],
              "redis": 1
            }
          },
          "target" : "http://127.0.0.1:8983/solr/"
        }
      }
    }
        

- No logging will take place;
- The Redis is **on** for this prject, and it is run on the provided **url** and **port**;
- One **service**, named **solr** is defined;
- It redirects request to http://127.0.0.1:8983/solr/, as defined by the **target** param.
- If request arrives to /solr/\*select\*, it will be processed using the **sort_default** function in [processors.py](processors.py);
- if it arrives to /solr/\*update\* it will be processed using the **index_media** function defined in the same file, but this will go through the redis queue.

The idea of this is to enrich the solr queries outputted by an application (in this case *Omeka S*) 
before passing them further to the actual apache solr server.

## Instalation example

(as apache site using wsgi on ubuntu)

install redis and other requirements:

    sudo apt install redis
    redis-cli --version
    sudo systemctl status redis
    sudo apt install python3-pip
    sudo -H pip3 install flask redis rq

install middleman:

    cd /var/www
    sudo git clone https://github.com/procesaur/MiddleMan.git
    cd /etc/apache2/sites-available/
    sudo nano middleman.conf

paste:

    <VirtualHost *:5002>
    WSGIDaemonProcess middleman user=www-data group=www-data threads=5
            WSGIScriptAlias / /var/www/MiddleMan/middleman.wsgi
    
            <Directory /var/www/MiddleMan>
                    WSGIProcessGroup middleman
                    WSGIApplicationGroup %{GLOBAL}
                    Order deny,allow
                    Deny from all
                    Allow from 127.0.0.1 ::1/128 <ADRESA SERVERA>
            </Directory>
    </VirtualHost>

exit nano

    sudo -H pip3 install xmltodict

    sudo a2ensite middleman
    sudo service apache2 restart
    sudo nano /etc/systemd/system/rqworker@.service


paste:

    [Unit]
    Description=RQ Worker
    After=network.target
    
    [Service]
    Type=simple
    WorkingDirectory=/var/www/MiddleMan
    Environment=LANG=en_US.UTF-8
    Environment=LC_ALL=en_US.UTF-8
    Environment=LC_LANG=en_US.UTF-8
    ExecStart=/usr/local/bin/rq worker
    ExecReload=/bin/kill -s HUP $MAINPID
    ExecStop=/bin/kill -s TERM $MAINPID
    PrivateTmp=true
    Restart=always
    User=www-data
    
    [Install]
    WantedBy=multi-user.target

exit nano

    sudo systemctl enable rqworker
    sudo service rqworker start

** if you want to use the provided extensions for omeka and solr, you will also need https://github.com/procesaur/TExASe installed on your server.
