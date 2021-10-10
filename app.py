import datetime
import json
import csv
import re
import os
from flask import Flask, request, render_template_string, render_template, g

LOGS_FILE = "data/logs.csv"

# Class-based application configuration
class ConfigClass(object):
    """ Flask application config """
    # Flask settings
    SECRET_KEY = 'kitty'

with open("data/users.json") as f:
    users = json.load(f)
user_tokens = [i["token"] for i in users]

def get_user_by_token(token):
    for user in users:
        if user["token"] == token:
            return user
def get_user_by_id(id):
    for user in users:
        if user["id"] == id:
            return user

def create_app():
    """ Flask application factory """
    
    # Create Flask app load app.config
    app = Flask(__name__)
    app.config.from_object(__name__+'.ConfigClass')

    @app.route('/')
    def home_page():
        return {"meesage" : "hello world!"}

    @app.route('/api/login', methods=["POST"])
    def login():
        token = request.json["token"]
        if token in user_tokens:
            return {
                "message" : "Success",
                "user" : get_user_by_token(token)
            }
        else:
            return {
            "message" : "Unauthorized"
        }, 403


    @app.route('/api/users/<id>', methods=["GET"])
    def users(id):
        user = get_user_by_id(int(id))
        if user is not None:
            user = user.copy()
            user.pop("token")
            return user
        else:
            return {
                "message" : "user does not exists"
            }, 400

    @app.route('/api/messages', methods=["GET", "POST"])
    def messages():
        user = get_user_by_token(request.headers["token"])

        if user == None:
            return {
                "message" : "Unauthorized"
            }, 403

        if request.method == "GET":
            with open(LOGS_FILE,"r") as f:
                reader = csv.DictReader(f,delimiter = ",")
                messages = [i for i in reader]
            return {"messages" : messages}
    
        msg = request.json
        
        if list(msg.keys()) != ["message", "timestamp", "channel"]:
            return {
                "message" : "Invalid log"
            }
        
        with open(LOGS_FILE,"r") as f:
            reader = csv.reader(f,delimiter = ",")
            data = list(reader)
            id = len([i for i in data if i[2]==msg["channel"]])

        msg["author_name"] = user["name"]
        msg["id"] = id

        with open(LOGS_FILE, 'a+', newline='') as f:
            w = csv.DictWriter(f, msg.keys())
            w.writerow(msg)


        return {"id" : id}

    @app.route("/logger/<channel>/<token>")
    def logger_site(channel, token):
        user = get_user_by_token(token)

        if user == None:
            return render_template_string("invalid token"), 403
        else:

            return render_template("logger.html", channel=channel, token=token), 200

    return app


# Start development web server
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=os.environ.get("PORT"), debug=True)
