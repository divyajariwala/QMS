import utils
import json
import boto3
import os
from fastapi import FastAPI, Request
from openai import OpenAI

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")
SAGEMAKER_ENDPOINT_NAME = os.getenv("SAGEMAKER_ENDPOINT_NAME")

client = OpenAI(
    api_key = API_KEY,
    base_url = BASE_URL, 
)

# initialize runtime for sagemaker endpoint
runtime= boto3.client('runtime.sagemaker')

# initialize the FastAPI
app = FastAPI()

@app.post("/ae_pc_detector")
async def ae_pc_detector(request: Request):
    data = await request.json()
    narrative = data["narrative"]
    result = utils.aepc_prediction(client, narrative)
    return result

@app.post("/pc_csc_prediction")
async def pc_csc_prediction(request: Request):
    data = await request.json()
    narrative = data["narrative"]
    if "model" in data.keys():
        model = data["model"]
    else:
        model = SAGEMAKER_ENDPOINT_NAME
    input_data = [
        {
            "modelInput": {
                "Complaint": narrative
            }
        },
    ]
    payload=json.dumps(input_data)
    response = runtime.invoke_endpoint(
        EndpointName = model, 
        ContentType='application/json',
        Body=payload
    )
    result = json.loads(response['Body'].read().decode())
    return result

@app.post("/pc_lvl_prediction")
async def pc_lvl_prediction(request: Request):
    ### NEED TO BE DONE
    return

@app.post("/priority_summarization")
async def pc_priority_summarization(request: Request):
    data = await request.json()
    narrative = data["narrative"]
    result = utils.priority_summarization(client, narrative)
    return result