# database-web
The investor database website

## To see the website on your local machine:
We recommend creating a virtual environment. You will need Anaconda/Miniconda for this.

### Linux
```console
$ git clone https://github.com/BfE-DataAnalytics/database-web.git
$ cd database-web
$ conda create --name dbweb python=3.6
$ source activate dbweb
(dbweb) $ pip install flask, flask-migrate, flask-wtf, flask-sqlalchemy, flask-migrate, flask-login
(dbweb) $ export FLASK_APP=run.py
(dbweb) $ flask run
```

### MacOS
```console
$ git clone https://github.com/BfE-DataAnalytics/database-web.git
$ cd database-web
$ export PATH=~/anaconda3/bin:$PATH
$ conda create --name dbweb python=3.6
$ source activate dbweb
$ virtualenv venv
$ source venv/bin/activate
(dbweb) $ pip install flask, flask-migrate, flask-wtf, flask-sqlalchemy, flask-migrate, flask-login 
(dbweb) $ export FLASK_APP=run.py
(dbweb) $ flask run
```

In the URL, add:
/viewGE 
/viewUE
/userrating 
to view GE,UE,user rating respectively

Please also pip install:

flask

flask-wtf

flask-sqlalchemy

flask-migrate

