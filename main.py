from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List
import google.generativeai as genai
import PIL.Image
import io
import base64
import json
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from fastapi.middleware.cors import CORSMiddleware
import os  # Import the os module

# Initialize FastAPI app
app = FastAPI()

# Configure CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)  # This line requires the os module

# Configure logging
def setup_logger():
    logger = logging.getLogger('document_comparison')
    logger.setLevel(logging.INFO)

    file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - RequestID: %(request_id)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )

    file_handler = RotatingFileHandler(
        f'logs/document_comparison.log',
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

logger = setup_logger()

# Configure Gemini AI
genai.configure(api_key="AIzaSyATtiKUD9zPa_lFgoRiazgh-lFcuDGucJ8")
model = genai.GenerativeModel("gemini-1.5-flash")

# Define mappings and fields as constants
MAPPING_IMG1 = {
    "Company name (User name)": "user_name",
    "MEID": "user_id",
    "Sponsor Bank": "sponsor_bank",
    "Processing Bank": "processing_bank",
    "Amount in Figures": "amt_in_figures",
    "Amount in words": "amt_in_words"
}

MAPPING_IMG2 = {
    "DE user name": "user_name",
    "DE user ID": "user_id",
    "Amount in Figures": "amt_in_figures",
    "Amount in words": "amt_in_words",
    "TNA prepared by": "sponsor_bank",
    "TNA approved by": "processing_bank",
}

FIELDS1 = {
    "Company name (User name)",
    "MEID",
    "Sponsor Bank",
    "Processing Bank",
    "Amount in Figures",
    "Amount in words"
}

FIELDS2 = {
    "DE user name",
    "DE user ID",
    "TNA prepared by",
    "TNA approved by",
    "Processing amount limit that will contain in words and number both"
}

# Pydantic models for request and response
class CompareRequest(BaseModel):
    captures: List[str]  # List of base64-encoded images

class ComparisonResponse(BaseModel):
    response1: dict
    response2: dict
    comparison_result: dict

# Helper functions
def compare_responses(response1: Dict, response2: Dict) -> Dict:
    """
    Compare two response dictionaries and return a comparison result based on the specified conditions.
    """
    common_fields = set(response1.keys()) & set(response2.keys())
    matching_fields = []
    mismatched_fields = {}

    for field in common_fields:
        if response1[field] == response2[field]:
            matching_fields.append(field)
        else:
            mismatched_fields[f"{field}1, {field}2"] = f"{response1[field]}, {response2[field]}"

    if len(matching_fields) == len(common_fields):
        return {"Status": "Complete Match"}
    elif len(matching_fields) > 0:
        return {
            "Status": "Partial Match",
            **mismatched_fields
        }
    else:
        return {"Status": "Nothing Match"}

async def process_image(image: PIL.Image.Image, fields: set, mapping: dict) -> dict:
    """Process a single image with Gemini AI."""
    prompt = (
        f"Extract values for the specified fields {fields} from the image in JSON format. "
        f"Replace the key names as per {mapping}. "
        "For sponsor_bank and processing_bank, return only the bank name, excluding the prefix 'Authorised signatory from'. "
        "For amt_in_words, return only the amount in words (e.g., 'TEN MILLION') without any additional text or symbols. "
        "Output strictly in JSON format."
    )
    try:
        response = model.generate_content(
            [prompt, image],
            generation_config=genai.GenerationConfig(response_mime_type="application/json")
        )
        return json.loads(response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

def base64_to_image(base64_str: str) -> PIL.Image.Image:
    """Convert a base64-encoded string to a PIL image."""
    try:
        image_data = base64.b64decode(base64_str)
        return PIL.Image.open(io.BytesIO(image_data))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 image data: {str(e)}")

# Endpoint to compare documents
@app.post("/compare_documents/", response_model=ComparisonResponse)
async def compare_documents(request: CompareRequest):
    """
    Endpoint to compare two documents and extract information.
    Accepts base64-encoded image data.
    """
    # Generate a unique request ID
    request_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    log_context = {'request_id': request_id}

    logger.info("Starting document comparison", extra=log_context)

    try:
        # Ensure exactly two images are provided
        if len(request.captures) != 2:
            raise HTTPException(status_code=400, detail="Exactly two images are required for comparison.")

        # Convert base64 strings to PIL images
        logger.info("Converting base64 images to PIL images", extra=log_context)
        image1 = base64_to_image(request.captures[0])
        image2 = base64_to_image(request.captures[1])

        # Process both images
        logger.info("Processing images with Gemini", extra=log_context)
        response1 = await process_image(image1, FIELDS1, MAPPING_IMG1)
        response2 = await process_image(image2, FIELDS2, MAPPING_IMG2)

        # Compare responses
        logger.info("Comparing processed results", extra=log_context)
        comparison_result = compare_responses(response1, response2)

        logger.info(
            f"Comparison completed. Status: {comparison_result.get('Status', 'Unknown')}",
            extra=log_context
        )

        return ComparisonResponse(
            response1=response1,
            response2=response2,
            comparison_result=comparison_result
        )

    except HTTPException as e:
        logger.error(
            f"HTTP error during document comparison: {str(e.detail)}",
            exc_info=True,
            extra=log_context
        )
        raise e
    except Exception as e:
        logger.error(
            f"Error during document comparison: {str(e)}",
            exc_info=True,
            extra=log_context
        )
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}