import fitz  # PyMuPDF
from PIL import Image
import io
import json
import base64
import boto3
from botocore.exceptions import ClientError

def pdf_to_images(pdf_path):
    """Convert PDF pages to PIL Images and return as list"""
    doc = fitz.open(pdf_path)
    images = []
    
    for page_num in range(doc.page_count):
        page = doc[page_num]
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
        images.append(img)
    
    doc.close()
    return images

def images_to_base64(images):
    """Convert PIL Images to base64 strings"""
    base64_images = []
    for img in images:
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf8')
        base64_images.append(img_base64)
    return base64_images

def run_multi_modal_prompt(bedrock_runtime, model_id, messages, max_tokens):
    """Invokes a model with a multimodal prompt"""
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "messages": messages
    })
    
    response = bedrock_runtime.invoke_model(body=body, modelId=model_id)
    response_body = json.loads(response.get('body').read())
    return response_body

if __name__ == "__main__":
    pdf_file = input("Enter PDF file path: ")
    page_images = pdf_to_images(pdf_file)
    print(f"Converted {len(page_images)} pages to images")
    
    # Convert images to base64
    base64_images = images_to_base64(page_images)
    
    # Setup Bedrock client
    bedrock_runtime = boto3.client(service_name='bedrock-runtime')
    model_id = 'anthropic.claude-3-7-sonnet-20250219-v1:0'
    max_tokens = 1000
    
    # Create message content with all images
    content = []
    for img_base64 in base64_images:
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": img_base64
            }
        })
    
    # Add placeholder prompt
    content.append({
        "type": "text",
        "text": "Analyze these document pages and provide a summary of the content."
    })
    
    message = {"role": "user", "content": content}
    messages = [message]
    
    try:
        response = run_multi_modal_prompt(bedrock_runtime, model_id, messages, max_tokens)
        print(json.dumps(response, indent=4))
    except ClientError as err:
        print(f"Error: {err.response['Error']['Message']}")

