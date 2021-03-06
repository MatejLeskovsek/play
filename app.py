import datetime
from flask import Flask
from flask import request
import pymongo
import requests
from webargs import fields
from flask_apispec import use_kwargs, marshal_with
from flask_apispec import FlaskApiSpec
from marshmallow import Schema
from flask_cors import CORS, cross_origin
import sys
from circuitbreaker import circuit
import logging
import socket
from logging.handlers import SysLogHandler
import json
import asyncio

app = Flask(__name__)
app.config.update({
    'APISPEC_SWAGGER_URL': '/plopenapi',
    'APISPEC_SWAGGER_UI_URL': '/plswaggerui'
})
docs = FlaskApiSpec(app, document_options=False)

cors = CORS(app)
service_name = "play_core_service"
service_ip = "play-core-service"

ecostreet_core_service = "ecostreet-core-service"
database_core_service = "database-core-service"
admin_core_service = "admin-core-service"
configuration_core_service = "configuration-core-service"

class ContextFilter(logging.Filter):
    hostname = socket.gethostname()
    def filter(self, record):
        record.hostname = ContextFilter.hostname
        return True

syslog = SysLogHandler(address=('logs3.papertrailapp.com', 17630))
syslog.addFilter(ContextFilter())
format = '%(asctime)s %(hostname)s TimeProject: %(message)s'
formatter = logging.Formatter(format, datefmt='%b %d %H:%M:%S')
syslog.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(syslog)
logger.setLevel(logging.INFO)

class NoneSchema(Schema):
    response = fields.Str()

# FALLBACK
@app.errorhandler(404)
def not_found(e):
    return "The API call destination was not found.", 404


def fallback_circuit():
    logger.info("Configuration microservice: Circuit breaker fallback accessed")
    return "The service is temporarily unavailable.", 500

async def send_sms(number, token):
    logger.info("Play microservice: asynchronously sending sms\n")
    url = "https://gateway.sms77.io/api/sms?p=ViGMg6uyACMM2Q2vnXEBJBkOOZnefE26eJz1qGucKiJ8OgYm2l3SzizfRDC7bEDx&to="+ number +"&text=[THIS IS WHERE YOUR DATA WOULD BE IF I HAD ONE MORE DAY]&from=ProjectTime"
    response = requests.request("GET", url)
    logger.info("Play microservice: asynchronous sms sent\n")
    return None

# SMS
@app.route("/plsms", methods=["POST"])
@use_kwargs({'number': fields.Str(), "AccessToken": fields.Str()})
@marshal_with(NoneSchema, description='200 OK', code=200)
@circuit(failure_threshold=1, recovery_timeout=10, fallback_function=fallback_circuit)
def sms():
    logger.info("Play microservice: /plsms accessed\n")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    async_call = loop.run_until_complete(send_sms(request.form["number"], request.form["AccessToken"]))
    logger.info("Play microservice: /plsms finished\n")
    return {"response": "200"}, 200
docs.register(sms)

# HEALTH PAGE
@app.route("/")
@marshal_with(NoneSchema, description='200 OK', code=200)
@circuit(failure_threshold=1, recovery_timeout=10, fallback_function=fallback_circuit)
def health():
    return {"response": "200"}, 200
docs.register(health)

# HOME PAGE
@app.route("/pl")
@marshal_with(NoneSchema, description='200 OK', code=200)
@circuit(failure_threshold=1, recovery_timeout=10, fallback_function=fallback_circuit)
def hello_world():
    return {"response": "Play microservice."}, 200
docs.register(hello_world)

# HOLIDAY CALL
@app.route("/plgetholidays")
@marshal_with(NoneSchema, description='200 OK', code=200)
@marshal_with(NoneSchema, description='Something went wrong.', code=500)
@circuit(failure_threshold=1, recovery_timeout=10, fallback_function=fallback_circuit)
def get_holidays():
    logger.info("Play microservice: /plgetholidays accessed\n")
    try:
        response = requests.get("https://teaching.lavbic.net/api/prazniki/iskanje/leto/2022")
        logger.info("Play microservice: /plgetholidays finished\n")
        return {"response": json.loads(response.text)}, 200
    except:
        logger.info("Play microservice: /plgetholidays hit an error\n")
        return {"response": "External API currently unavailable."}, 500
docs.register(get_holidays)

# GET GAMES
@app.route("/plgetgames", methods=["POST"])
@use_kwargs({'AccessToken': fields.Str()})
@marshal_with(NoneSchema, description='200 OK', code=200)
@marshal_with(NoneSchema, description='Something went wrong.', code=500)
@circuit(failure_threshold=1, recovery_timeout=10, fallback_function=fallback_circuit)
def get_games():
    logger.info("Play microservice: /plgetgames accessed\n")
    try:
        url = 'http://' + database_core_service + '/dbgetgames'
        response = requests.post(url, data={"AccessToken": request.form["AccessToken"]})
        logger.info("Play microservice: /plgetgames finished\n")
        return {"response": response.text}, 200
    except:
        logger.info("Play microservice: /plgetgames hit an error\n")
        return {"response": "Something went wrong."}, 500 
docs.register(hello_world)

# JOIN GAME 
@app.route("/pljoingame", methods=["PUT"])
@use_kwargs({'AccessToken': fields.Str()})
@marshal_with(NoneSchema, description='200 OK', code=200)
@marshal_with(NoneSchema, description='Something went wrong.', code=500)
@circuit(failure_threshold=1, recovery_timeout=10, fallback_function=fallback_circuit)
def join_game():
    logger.info("Play microservice: /pljoingame accessed\n")
    try:
        url = 'http://' + database_core_service + '/dbjoingame'
        response = requests.put(url, data={"name": request.form["name"], "AccessToken": request.form["AccessToken"]})
        logger.info("Play microservice: /pljoingame finished\n")
        return {"response": response.text}, 200
    except:
        logger.info("Play microservice: /pljoingame hit an error\n")
        return {"response": "Something went wrong."}, 500 
docs.register(join_game)


# LEAVE GAME
@app.route("/plleavegame", methods=["DELETE"])
@use_kwargs({'AccessToken': fields.Str()})
@marshal_with(NoneSchema, description='200 OK', code=200)
@marshal_with(NoneSchema, description='Something went wrong.', code=500)
@circuit(failure_threshold=1, recovery_timeout=10, fallback_function=fallback_circuit)
def leave_game():
    logger.info("Play microservice: /plleavegame accessed\n")
    try:
        url = 'http://' + database_core_service + '/dbleavegame'
        response = requests.delete(url, data={"name": request.form["name"], "AccessToken": request.form["AccessToken"]})
        logger.info("Play microservice: /plleavegame finished\n")
        return {"response": response.text}, 200
    except:
        logger.info("Play microservice: /plleavegame hit an error\n")
        return {"response": "Something went wrong."}, 500 
docs.register(leave_game)
 
# SERVICE IP UPDATE FUNCTION
@app.route("/plupdate_ip", methods = ['PUT'])
@use_kwargs({'name': fields.Str(), 'ip': fields.Str()})
@marshal_with(NoneSchema, description='200 OK', code=200)
@marshal_with(NoneSchema, description='Something went wrong', code=500)
@circuit(failure_threshold=1, recovery_timeout=10, fallback_function=fallback_circuit)
def update_ip():
    global ecostreet_core_service
    global configuration_core_service
    global database_core_service
    global admin_core_service
    global service_ip
    global service_name
    logger.info("Play microservice: /plupdate_ip accessed\n")
    
    service_ip = request.form["ip"]
    
    data = {"name": service_name, "ip": service_ip}
    try:
        url = 'http://' + configuration_core_service + '/cfupdate'
        response = requests.put(url, data=data)
        logger.info("Play microservice: /plupdate_ip finished\n")
        return {"response": response.text}, 200
    except:
        logger.info("Play microservice: /plupdate_ip hit an error\n")
        return {"response": "Something went wrong."}, 500
docs.register(update_ip)

# FUNCTION TO UPDATE IP'S OF OTHER SERVICES
@app.route("/plconfig", methods = ['PUT'])
@use_kwargs({'name': fields.Str(), 'ip': fields.Str()})
@marshal_with(NoneSchema, description='200 OK', code=200)
@marshal_with(NoneSchema, description='Something went wrong', code=500)
@circuit(failure_threshold=1, recovery_timeout=10, fallback_function=fallback_circuit)
def config_update():
    global ecostreet_core_service
    global configuration_core_service
    global database_core_service
    global admin_core_service
    global service_ip
    global service_name
    logger.info("Play microservice: /plconfig accessed\n")
    
    try:
        microservice = str(request.form["name"])
        ms_ip = request.form["ip"]
        if microservice == "database_core_service":
            database_core_service = ms_ip
        if microservice == "ecostreet_core_service":
            ecostreet_core_service = ms_ip
        if microservice == "admin_core_service":
            admin_core_service = ms_ip
        if microservice == "configuration_core_service":
            configuration_core_service = ms_ip
        logger.info("Play microservice: /plconfig finished\n")
        return {"response": "200 OK"}, 200
    except Exception as err:
        logger.info("Play microservice: /plconfig hit an error\n")
        return {"response": "Something went wrong."}, 500
docs.register(config_update)

# FUNCTION TO GET CURRENT CONFIG 
@app.route("/plgetconfig")
@marshal_with(NoneSchema, description='200 OK', code=200)
@circuit(failure_threshold=1, recovery_timeout=10, fallback_function=fallback_circuit)
def get_config():
    global ecostreet_core_service
    global configuration_core_service
    global database_core_service
    global admin_core_service
    global service_ip
    global service_name
    logger.info("Play microservice: /plgetconfig accessed\n")
    logger.info("Play microservice: /plgetconfig finished\n")
    
    return {"response": str([ecostreet_core_service, configuration_core_service, database_core_service, admin_core_service])}, 200
docs.register(get_config)

# METRICS FUNCTION
@app.route("/plmetrics")
@marshal_with(NoneSchema, description='200 OK', code=200)
@marshal_with(NoneSchema, description='METRIC CHECK FAIL', code=500)
@circuit(failure_threshold=1, recovery_timeout=10, fallback_function=fallback_circuit)
def get_health():
    logger.info("Play microservice: /plmetrics accessed\n")
    start = datetime.datetime.now()
    try:
        url = 'http://' + database_core_service + '/cfhealthcheck'
        response = requests.get(url)
    except Exception as err:
        logger.info("Play microservice: /plmetrics hit an error\n")
        return {"response": "METRIC CHECK FAIL: configuration unavailable"}, 500
    end = datetime.datetime.now()
    
    start2 = datetime.datetime.now()
    try:
        url = 'http://' + ecostreet_core_service + '/lghealthcheck'
        response = requests.get(url)
    except Exception as err:
        logger.info("Play microservice: /plmetrics hit an error\n")
        return {"response": "METRIC CHECK FAIL: login service unavailable"}, 500
    end2 = datetime.datetime.now()
    
    delta1 = end-start
    crt = delta1.total_seconds() * 1000
    delta2 = end2-start2
    lrt = delta2.total_seconds() * 1000
    health = {"metric check": "successful", "database response time": crt, "login response time": lrt}
    logger.info("Play microservice: /plmetrics finished\n")
    return {"response": str(health)}, 200
docs.register(get_health)

# HEALTH CHECK
@app.route("/plhealthcheck")
@marshal_with(NoneSchema, description='200 OK', code=200)
@circuit(failure_threshold=1, recovery_timeout=10, fallback_function=fallback_circuit)
def send_health():
    logger.info("Play microservice: /plhealthcheck accessed\n")
    try:
        url = 'http://' + ecostreet_core_service + '/lg'
        response = requests.get(url)
        url = 'http://' + configuration_core_service + '/cf'
        response = requests.get(url)
        url = 'http://' + database_core_service + '/db'
        response = requests.get(url)
    except Exception as err:
        logger.info("Play microservice: /plhealthcheck hit an error\n")
        return {"response": "Healthcheck fail: depending services unavailable"}, 500
    logger.info("Play microservice: /plhealthcheck finished\n")
    return {"response": "200 OK"}, 200
docs.register(send_health)
