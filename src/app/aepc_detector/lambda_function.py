import json
import os

import boto3

bedrock_client = boto3.client("bedrock-runtime")

MODEL_ID = os.environ.get("model_id",
                          "arn:aws:bedrock:us-east-1:120569648189:inference-profile"
                          "/us.anthropic.claude-sonnet-4-20250514-v1:0")


def load_prompt():
    """Load the prompt from local file."""
    prompt_file = os.path.join(os.path.dirname(__file__), "aepc_detector_prompt.md")
    with open(prompt_file, "r", encoding="utf-8") as f:
        return f.read()


def list_profiles():
    """Helper to list inference profiles from Bedrock"""
    client = boto3.client("bedrock")
    resp = client.list_inference_profiles()
    for profile in resp["inferenceProfileSummaries"]:
        print(profile["inferenceProfileId"], profile["inferenceProfileArn"])
    return resp


def lambda_handler(event, _context):

    client = boto3.client("bedrock")

    list_profiles()

    try:
        if "body" in event:
            body = json.loads(event["body"])
        else:
            body = event

        narrative = body.get("narrative", "")
        if not narrative:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing 'narrative' in request"})
            }

        base_prompt = load_prompt()

        messages = [
            {
                "role": "user",
                "content": f"{base_prompt}\n\nNarrative:\n{narrative}"
            }
        ]

        response = bedrock_client.invoke_model(
            modelId=MODEL_ID,
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1024,
                "temperature": 0.0,
                "messages": messages
            })
        )

        response_body = json.loads(response["body"].read())
        output_text = response_body["content"][0]["text"]

        return {
            "statusCode": 200,
            "body": json.dumps({"result": output_text})
        }

    except Exception as e:  # pylint: disable=broad-exception-caught
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
