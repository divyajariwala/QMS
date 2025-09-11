import json
from pydantic import BaseModel, Field, ValidationError
from typing import Dict

# Structured Output Format
class AEPCPrediction(BaseModel):
    narrative: str = Field(..., description="The original narrative text")
    ae_pc_prediction: Dict[str, int] = Field(
        ..., 
        description="Prediction result as a dictionary. AE and PC are represented as 1 or 0.",
        # pattern="^(AE|PC|Both|Neither)$"
    )
    reason: str = Field(..., description="Brief justification for the prediction")
    
# func: aepc_prediction
def aepc_prediction(client, narrative, model_id="azure.gpt-4o"):
    with open('aepc_detector_prompt.md', 'r') as file:
        prompt = file.read()
    model_response = client.chat.completions.create(
        model=model_id,
        messages=[
            {
                "role": "user",
                "content": prompt.replace("{narrative}", narrative)
            }
        ]
    )
    print(model_response)
    result =json.loads(model_response.choices[0].message.content.replace("```json", "").replace("```", ""))
    # check the model output format
    try:
        # Validate and control the output
        output = AEPCPrediction(
            narrative=result["narrative"],
            ae_pc_prediction=result["ae_pc_prediction"],
            reason=result["reason"]
        )
        final_response = json.dumps(output.model_dump(), indent=4) # JSON format
        print(final_response)
    except ValidationError as e:
        print("Validation Error:", e)
    return final_response


# func: priority_summarization
def priority_summarization(client, narrative, model_id="azure.gpt-4o"):
    with open('pc_summary_prompt.md', 'r') as file:
        prompt = file.read()
    model_response = client.chat.completions.create(
        model=model_id,
        messages=[
            {
                "role": "user",
                "content": prompt.replace("{narrative}", narrative)
            }
        ]
    )
    print(model_response)
    result =json.loads(model_response.choices[0].message.content.replace("```json", "").replace("```", ""))
    return result