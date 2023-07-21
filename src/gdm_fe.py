from flask import Flask, request, render_template, redirect, url_for, session
from flask_session import Session
from flask_cors import CORS
import argparse
import logging
import grpc
import gdm_pb2
import gdm_pb2_grpc

server_url = ""
parser =  argparse.ArgumentParser(
    prog="GDM Front End Server",
    description="Runs the GDM Front end server")

parser.add_argument("--server_url", type=str, default="localhost:50051", help="URL of the GDM backend server")
parser.add_argument("--host", type=str, default="0.0.0.0", help="host of this server. e.g (localhost, 0.0.0.0, etc)")
parser.add_argument("--port", type=int, default=8080, help="port exposed by this server")

# Todos
# Stop collecting BMI, we can infer that from that from BMI
# Hash passwords before passing them along.

class Opts:
    def __init__(self):
        self.server_url = ""

    def __init__(self, server_url):
        self.server_url = server_url


app = Flask(__name__, template_folder='front_end/views/template', static_folder='front_end/views/static')
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
cors = CORS(app)
Session(app)


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        if  session.get("user_id"):
            return redirect(url_for("dashboard"))
        return render_template('login.html')
    if request.method == "POST":
        request_json = request.get_json()
        with grpc.insecure_channel(server_url) as channel:
            stub = gdm_pb2_grpc.GdmStub(channel)
            cred = gdm_pb2.SignInRequest(
                user_id=request_json["user_id"],
                password_hash=request_json["password"]
            )
            logging.info("user_id: %s, passed: %s", cred.user_id, cred.password_hash)
            ack = stub.SignIn(cred)
            logging.info("success: %s. %s", ack.success, ack.msg)
            if ack.success:
                session['user_id'] = request_json["user_id"]
            return str(ack.success)

@app.route('/signup', methods=['POST'])
def signup():
    if request.method == "POST":
        request_json = request.get_json()
        with grpc.insecure_channel(server_url) as channel:
            stub = gdm_pb2_grpc.GdmStub(channel)
            user = gdm_pb2.SignUpRequest(
                user=gdm_pb2.User(
                    user_id=request_json["user_id"],
                    password_hash=request_json["password"],
                    bmi = float(request_json["bmi"]),
                    age=int(request_json["age"]),
                    height=float(request_json["height"]),
                    obesity=request_json["obesity"],
                    ethnicity=request_json["ethnicity"],
                    gravida=request_json["is_first_pregnancy"]
                )
            )
            logging.info("user: %s", user)
            ack = stub.SignUp(user)
            logging.info("success: %s. %s", ack.success, ack.msg)
            if not ack.success:
                return (ack.msg)
            session['user_id'] = request_json["user_id"]
            return str(ack.success)
          
    
@app.route('/dashboard', methods=['GET'])
def dashboard():
    if request.method == "GET":
        if not session.get("user_id"):
            return redirect(url_for("login"))
        
        with grpc.insecure_channel(server_url) as channel:
            stub = gdm_pb2_grpc.GdmStub(channel)
            req = gdm_pb2.GetUserRequest(
                user_id=session.get("user_id")
            )
            resp = stub.GetUser(req)
        return render_template('dashboard.html',
                               user_id = resp.user.user_id,
                               age = resp.user.age,
                               bmi = resp.user.bmi,
                               gdm = "False")


@app.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('user_id', None)
   return redirect(url_for('login'))



if __name__ == '__main__':
   logging.basicConfig(
        level=logging.INFO,
        format=''
    )
   args = parser.parse_args()
   server_url = args.server_url
   logging.info("Starting server on port %s", args.port)
   app.run(args.host, args.port)
