# GDM 


## Description
Gestational diabetes mellitus (GDM)  is a condition in which a hormone made by the placenta prevents the body from using insulin effectively. Glucose builds up in the blood instead of being absorbed by the cells. This contians the full deployment for a platform for health tracking and predicting GDM in patients


## Requirements
* [terraform](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli)
* [kind](https://kind.sigs.k8s.io/docs/user/quick-start/)
* [kubectl](https://kubernetes.io/docs/tasks/tools/#kubectl)
* [docker](https://docs.docker.com/engine/install/)
Additionally for cloud deployment:
* [gcloud](https://cloud.google.com/sdk/docs/install-sdk)



## Usage

### Running locally

**Create infrastructure resources(includes kubernetes cluster) locally**
```
cd deployment/local/terraform/
terraform init
terraform apply
cd ../../../
```

**Build application containers**
```
docker build -t gdm/server -f docker/server/Dockerfile .
docker build -t gdm/fe -f docker/front_end/Dockerfile .
```

**Load containers unto the clusters**
```
kind load docker-image gdm/server --name gdm-local
kind load docker-image gdm/fe --name gdm-local
```

**Create application deployment**
```
kubectl apply -f deployment/local/mongo-service.yaml
kubectl apply -f deployment/local/gdm-server.yaml
kubectl apply -f deployment/local/gdm-fe.yaml
```

**forward service port to localhost**
```
kubectl port-forward service/gdm-fe 8080:8080
kubectl port-forward service/mongo-service 27018:27017
```

**Optional:** run the simulator
```
docker build -t gdm/simulator -f docker/simulator/Dockerfile .
kind load docker-image gdm/simulator --name gdm-local
kubectl apply -f deployment/local/gdm-simulator.yaml 
```

**Clean up**

```
kubectl delete -f deployment/local/mongo-service.yaml
kubectl delete -f deployment/local/gdm-server.yaml
kubectl delete -f deployment/local/gdm-fe.yaml
kubectl delete -f deployment/local/gdm-simulator.yaml 

cd deployment/local/terraform/
terraform destroy
```
### Deploying to Cloud
Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README.

**One time setup**
```
gcloud init
gcloud auth application-default login
```

Create the infrastructure
```
cd deployment/cloud/terraform/
terraform init
terraform apply
```
configure kubectl & docker 
```
cd deployment/cloud/terraform/
CLUSTER_NAME=$(terraform output -raw kubernetes_cluster_name)
REGION=$(terraform output -raw region)
PROJECT_ID=$(terraform output -raw project_id)
gcloud container clusters get-credentials $CLUSTER_NAME --region $(terraform output -raw region)
gcloud auth configure-docker $REGION-docker.pkg.dev
cd ../../../
```


Build and push containers to Artifact Registry
```
docker buildx create --use

docker buildx build --push --platform linux/amd64,linux/arm64 -t $REGION-docker.pkg.dev/$PROJECT_ID/gdm/server -f docker/server/Dockerfile .

docker buildx build --push --platform linux/amd64,linux/arm64 -t $REGION-docker.pkg.dev/$PROJECT_ID/gdm/fe -f docker/front_end/Dockerfile .

docker buildx build --push --platform linux/amd64,linux/arm64 -t $REGION-docker.pkg.dev/$PROJECT_ID/gdm/simulator -f docker/simulator/Dockerfile .
```

**create application deployment**
```
kubectl apply -f deployment/cloud/mongo-service.yaml
kubectl apply -f deployment/cloud/gdm-server.yaml
kubectl apply -f deployment/cloud/gdm-simulator.yaml
kubectl apply -f deployment/cloud/gdm-fe.yaml

```

**Clean up**
Warning: this will tear down all the live services and also delete the cluster and images
```
kubectl delete -f deployment/cloud/mongo-service.yaml
kubectl delete -f deployment/cloud/gdm-server.yaml
kubectl delete -f deployment/cloud/gdm-fe.yaml
kubectl delete -f deployment/cloud/gdm-simulator.yaml 


cd deployment/local/terraform/
terraform destroy
```


## Development flow

Before deploying the application either locally or in the cloud, you might want to test source chances directly. 

**Required**
* [python](https://www.python.org/downloads/)
* [mongo](https://www.mongodb.com/try/download/atlascli)
* [lens](https://k8slens.dev/desktop.html) - optional

**Setup**
```
# Start mongodb
mongod

# install python dependencies
pip3 install -r src/requirements.txt

# build protobufs
python -m grpc_tools.protoc -I ./src/protos/ --python_out=./src/ --pyi_out=./src/ --grpc_python_out=./src/ src/protos/gdm.proto
```

**Running the server**
```
python src/gdm_server.py
```

**Running the simulator**
```
python src/gdm_simulator.py
```

**Running the front end**
```
python src/gdm_fe.py
```
open [localhost:8080](http://localhost:8080) in your browser 