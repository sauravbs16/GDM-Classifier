import logging
from concurrent import futures
from google.protobuf.json_format import MessageToDict, ParseDict
import grpc
import pymongo
import gdm_pb2
import gdm_pb2_grpc
import argparse
import pickle
import pandas as pd
import os

# TODO: create an RPC that returns row for the classifier


samples_collection_name = "samples"
user_collection_name = "users"
gdm_database_name = "gdm"

fn = os.path.join(os.path.dirname(__file__), 'clf.pkl')
model = pickle.load(open(fn, "rb"))

parser =  argparse.ArgumentParser(
    prog="GDM Server",
    description="Runs the GDM server")

parser.add_argument("--mongo_url", type=str, default="mongodb://localhost:27017/", help="url of the mongo server.")
parser.add_argument("--port", type=int, default=50051, help="port that the server exposes")

class Opts:
    def __init__(self):
        self.db_url = ""
        self.port = ""
    def __init__(self, db_url, port):
        self.db_url = db_url
        self.port = port

def getUser(dbClient, user_id:str) -> dict:
    if type(dbClient) == pymongo.database.Database:
        query = { "user.userId" : user_id}
        cursor = dbClient[user_collection_name].find(query, {"_id":0})
        return  list(cursor)[0]["user"]

def userExists(dbClient, user_id:str) -> bool:
    if type(dbClient) == pymongo.database.Database:
        query = { "user.userId" : user_id}
        cursor = dbClient[user_collection_name].find(query, {"_id":0})
        cursor_list = list(cursor)
        if len(cursor_list) > 0:
            return True
    return False


def writeSample(dbClient, request: gdm_pb2.WriteSampleRequest) -> bool:
    sample = MessageToDict(request)
    if type(dbClient) == pymongo.database.Database:
        sampleCol = dbClient[samples_collection_name]
        transaction = sampleCol.insert_one(sample)
        return transaction.acknowledged 

def signUp(dbClient, request: gdm_pb2.SignUpRequest) -> bool:
    user = MessageToDict(request)
    logging.info("signUp: %s", user)
    if type(dbClient) == pymongo.database.Database:
        userCol = dbClient[user_collection_name]
        transaction = userCol.insert_one(user)
        return transaction.acknowledged 

def getSamples(dbClient, request: gdm_pb2.GetSamplesRequest) -> dict:
    if type(dbClient) == pymongo.database.Database:
        query = { "sample.userId" : request.user_id}
        cursor = dbClient[samples_collection_name].find(query,{"_id":0})
        cursor_list = [  sample["sample"] for sample in cursor]
        return  {'sample' : cursor_list}

def signIn(dbClient, request: gdm_pb2.SignInRequest) -> bool:
    if type(dbClient) == pymongo.database.Database:
        query = { "user.userId" : request.user_id, "user.passwordHash": request.password_hash}
        cursor = dbClient[user_collection_name].find(query, {"_id":0})
        cursor_list = list(cursor)
        logging.info("signIn: %s", cursor_list)
        if len(cursor_list) > 0:
            return True
        return False

def getDB(db_url:str):
    mongo_client = pymongo.MongoClient(db_url)
    return mongo_client[gdm_database_name]

def getDiagnosis(request: gdm_pb2.GetDiagnosisRequest) -> bool:
    data = pd.DataFrame({
        "Age": [request.user.age],
        "Height": [request.user.height],
        "Body Mass Index (BMI)": [request.user.bmi],
        "Obesity": [request.user.obesity],
        "OGTT1h": [request.sample.ogtt1h],
        "OGTT2h": [request.sample.ogtt2h],
        "Ethnicity_GBR": [int(request.user.ethnicity == gdm_pb2.Ethnicity.GBR)],
        "Ethnicity_IND": [int(request.user.ethnicity == gdm_pb2.Ethnicity.IND)],
        "Ethnicity_OTH": [int(request.user.ethnicity == gdm_pb2.Ethnicity.OTH)],
        "Gravida (Is this your first Pregnancy?)": [request.user.gravida]
        })
    prediction = model.predict(data)
    return bool(prediction[0])


class GdmServicer(gdm_pb2_grpc.GdmServicer):

    def __init__(self, db_url):
        self.db = getDB(db_url)

        
    def GetSamples(self, request: gdm_pb2.GetSamplesRequest, context):
        cursor_dict = getSamples(self.db, request)
        logging.info(cursor_dict)
        samples_proto = ParseDict(cursor_dict, gdm_pb2.Samples())
        return gdm_pb2.GetSamplesResponse(
            samples= samples_proto
        )
    
    def WriteSample(self, request: gdm_pb2.WriteSampleRequest, context) -> gdm_pb2.WriteSampleResponse:
        if not userExists(self.db, user_id=request.sample.user_id):
            logging.info("user_id: %s doesn't exists", request.sample.user_id)
            return gdm_pb2.WriteSampleResponse(
                success=False,
                msg="user_id: {} doesn't exists".format(request.sample.user_id)
            )

        ack = writeSample(self.db, request)
        return gdm_pb2.WriteSampleResponse(
            success=ack
        )
    
    def SignUp(self, request: gdm_pb2.SignUpRequest, context) -> gdm_pb2.SignUpResponse:
        if userExists(self.db, user_id=request.user.user_id):
            logging.info("user_id: %s already exists", request.user.user_id)
            return gdm_pb2.SignUpResponse(
                success=False,
                msg="user_id: {} already exists".format(request.user.user_id)
            )
        ack = signUp(self.db, request)
        return gdm_pb2.SignUpResponse(
            success=ack
        )

    def SignIn(self, request: gdm_pb2.SignInRequest, context) -> gdm_pb2.SignInResponse:
        ack = signIn(self.db, request)
        return gdm_pb2.SignInResponse(
            success=ack
        )
    
    def GetUser(self, request: gdm_pb2.GetUserRequest, context) -> gdm_pb2.GetUserResponse:
        user = getUser(self.db, request.user_id)
        logging.info("user: %s", user)
        user_proto = ParseDict(user, gdm_pb2.User())
        return gdm_pb2.GetUserResponse(
            user=user_proto
        )
    
    def GetDiagnosis(self, request: gdm_pb2.GetDiagnosisRequest, context) -> gdm_pb2.GetDiagnosisResponse:
        hasGDM = getDiagnosis(request)
        logging.info("hasGDM: %s", hasGDM)
        return gdm_pb2.GetDiagnosisResponse(
            hasGDM= hasGDM
        )
        

def serve(opts: Opts):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    gdm_pb2_grpc.add_GdmServicer_to_server(
        GdmServicer(opts.db_url), server)
    server.add_insecure_port('[::]:'+ str(opts.port))
    server.start()
    logging.info("Simulator started on port %s", opts.port)
    server.wait_for_termination()

3
if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        #format='%(asctime)s - %(process)d - %(levelname)s - %(message)s', 
        #datefmt='%d-%b-%y %H:%M:%S',
        format=''
    )
    args = parser.parse_args()
    opts =  Opts(
        db_url= args.mongo_url,
        port= args.port
    )
    serve(opts)