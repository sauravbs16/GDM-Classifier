import grpc
import gdm_pb2
import gdm_pb2_grpc
import logging
import time
import argparse
import random
import time


parser =  argparse.ArgumentParser(
    prog="GDM Simulator",
    description="Runs the GDM simulator")

parser.add_argument("--hostname", type=str, default="localhost", help="hostname of the GDM server")
parser.add_argument("--port", type=int, default=50051, help="port exposed by the GDM server")
parser.add_argument("--interval", type=int, default=3600*2, help="interval(secs) between each simulation sample")

name_bank = ["hudson", "archer", "asher", 
             "harrison", "brighton", "felix", 
             "henry", "ava", "violet", 
             "scarlett", "charlotte", "audrey", 
             "evelyn", "hazel", "liam", "Noah", "oliver",
            "james", "elijah", "william", "henry", "lucas", 
            "benjamin", "theodore", "mateo"]

# user same password for all
password = "asdalkhs;dfqweqw"

class Opts:
    def __init__(self):
        self.server_url = ""
        self.interval = 0

    def __init__(self, server_url, interval):
        self.server_url = server_url
        self.interval = interval

def create_signup(stub: gdm_pb2_grpc.GdmStub):
    user = gdm_pb2.SignUpRequest(
       user =  gdm_pb2.User(
        user_id="team8",
        password_hash="asdalkhs;dfqweqw",
        age= random.randint(16, 60),
        bmi = random.randrange(18, 40) + random.random(),
        height=random.randrange(90, 300),
        obesity=False,
        ethnicity=random.choice([gdm_pb2.Ethnicity.IND, gdm_pb2.Ethnicity.GBR, gdm_pb2.Ethnicity.OTH]),
        gravida=False
       )
    )
    ack = stub.SignUp(user)
    logging.info("success: %s. %s", ack.success, ack.msg)


def sign_in(stub: gdm_pb2_grpc.GdmStub):
    cred = gdm_pb2.SignInRequest(
        user_id="team8",
        password_hash="asdalkhs;dfqweqw"
    )
    ack = stub.SignIn(cred)
    logging.info("success: %s. %s", ack.success, ack.msg)

def get_user(stub: gdm_pb2_grpc.GdmStub):
    request = gdm_pb2.GetUserRequest(
        user_id="team8"
    )
    user = stub.GetUser(request)
    logging.info("user: %s", user)



def get_samples(stub: gdm_pb2_grpc.GdmStub):
    samples = stub.GetSamples(gdm_pb2.GetSamplesRequest(
        user_id="team8"
    ))
    logging.info(samples)

def write_sample(stub: gdm_pb2_grpc.GdmStub):
    sample = gdm_pb2.WriteSampleRequest(
       sample= gdm_pb2.Sample(
        timestamp = time.time_ns(),
        user_id="team8",
        ogtt1h=random.randrange(2, 10) + random.random(),
        ogtt2h=random.randrange(2, 10) + random.random()
       )
    )
    ack = stub.WriteSample(sample)
    logging.info("success: %s. %s", ack.success, ack.msg)

def start_simulation(stub: gdm_pb2_grpc.GdmStub, interval: int):
    ack = False
    while not ack:
        user_id = random.choice(name_bank)
        bmi = random.randrange(17, 40) + random.random()
        obese = False
        if bmi > 30:
            obese = True
        user = gdm_pb2.SignUpRequest(
        user =  gdm_pb2.User(
            user_id=user_id,
            password_hash=password,
            age= random.randint(16, 60),
            bmi = bmi,
            height=random.randrange(120, 200),
            obesity=obese,
            ethnicity=random.choice([gdm_pb2.Ethnicity.IND, gdm_pb2.Ethnicity.GBR, gdm_pb2.Ethnicity.OTH]),
            gravida=random.choice([True, False])))
        ack = stub.SignUp(user)
    logging.info("simulation create sign up, success: %s. %s", ack.success, ack.msg)
    while True:
        sample = gdm_pb2.WriteSampleRequest(
            sample= gdm_pb2.Sample(
            timestamp = time.time_ns(),
            user_id=user_id,
            ogtt1h=random.randrange(2, 10) + random.random(),
            ogtt2h=random.randrange(2, 10) + random.random())
        )
        ack = stub.WriteSample(sample)
        logging.info("simulation generate sample, success: %s. %s", ack.success, ack.msg)
        time.sleep(interval)


def run(opts: Opts):
    logging.info("Simulator started")
    with grpc.insecure_channel(opts.server_url) as channel:
        stub = gdm_pb2_grpc.GdmStub(channel)
        logging.info("-------------- Starting simulation --------------")
        start_simulation(stub, opts.interval)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format=''
    )
    args = parser.parse_args()
    opts = Opts(
        server_url= "{}:{}".format(args.hostname, args.port),
        interval = args.interval
    ) 
    run(opts)