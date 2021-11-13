import sys,json
from flask import render_template, jsonify,request
from flask import Flask
import services
import argparse
import logging
import json
import subprocess
logging.getLogger().setLevel(logging.INFO)
app = Flask(__name__)

service_file="/srv/transformer_frontend/app/services.json"

def get_service(name):
    with  open(service_file) as s:
        services = json.load(s)
        return services[name]

@app.route('/',methods=['GET', 'POST'])
def run():

    if request.method == 'POST':
        #return " "
        json_data=request.get_json()

        sys.stderr.write(str(json_data))
    return jsonify(service.do(json_data))
    #return ""#service.do(json_data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Marian translation server')
    parser.add_argument('--list', help='show available servers', action='store_true')
    parser.add_argument('-p', '--port', dest='port', type=int,
                        help='port')
    parser.add_argument('-s','--service',dest='servName', type=str,
                        help='service')

    args = parser.parse_args()
    #inform_db(args.servName,args.port)
    serv_params=get_service(args.servName)
    print(serv_params)
    print("running service {} on host {} port {}".format(args.servName, "host", args.port))
    service=getattr(services,serv_params["class"])(serv_params["arguments"])
    HOST = "0.0.0.0"
    PORT = args.port
    app.run(host=HOST,port=PORT, threaded=False)
