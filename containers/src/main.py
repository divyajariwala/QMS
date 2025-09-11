import utils
import json
import boto3
from fastapi import FastAPI, Request
from openai import OpenAI
# initialize LLM model
# client = boto3.client(service_name="bedrock-runtime")
client = OpenAI(
    api_key="sk-z64AsJhaUSPWF8ns_KCZWg",
    base_url="https://genai-sharedservice-americas.pwc.com", 
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
        model = "internal-pwc-mounjaro-12-categorization-model-v1"
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