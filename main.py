from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import google.generativeai as genai
import PIL.Image
import json
from typing import List, Dict
import io
import os
from pydantic import BaseModel
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Configure logging
def setup_logger():
    # Create a logger
    logger = logging.getLogger('document_comparison')
    logger.setLevel(logging.INFO)

    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - RequestID: %(request_id)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )

    # Create and configure file handler
    file_handler = RotatingFileHandler(
        f'logs/document_comparison.log',
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)

    # Create and configure console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

logger = setup_logger()

app = FastAPI()

# Configure Gemini AI
genai.configure(api_key="AIzaSyDv-v0xPb2IC4oExloK9a-CjAIMpL07TLc")
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
    "Sponsor Bank"
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

class ComparisonResponse(BaseModel):
    response1: dict
    response2: dict
    comparison_result: dict

def compare_responses(response1: Dict, response2: Dict) -> Dict:
    """
    Compare two response dictionaries and return a comparison result based on the specified conditions.
    """
    # Get common fields between the two responses
    common_fields = set(response1.keys()) & set(response2.keys())
    matching_fields = []
    mismatched_fields = {}

    # Compare each common field
    for field in common_fields:
        if response1[field] == response2[field]:
            matching_fields.append(field)
        else:
            mismatched_fields[f"{field}1, {field}2"] = f"{response1[field]}, {response2[field]}"

    # Determine the comparison status
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
    prompt = f"Extract values for the specified fields {fields} from the image in JSON format. Replace the key names as per {mapping}. For sponsor_bank and processing_bank, return only the bank name, excluding the prefix 'Authorised signatory from'. Output strictly in JSON format."
    try:
        response = model.generate_content(
            [prompt, image],
            generation_config=genai.GenerationConfig(response_mime_type="application/json")
        )
        return json.loads(response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

def validate_file_type(file: UploadFile):
    """Validate if the file type is supported."""
    allowed_types = {"image/jpeg", "image/jpg", "application/pdf"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file.content_type} not supported. Please upload JPEG, JPG, or PDF files only."
        )

@app.post("/compare-documents/", response_model=ComparisonResponse)
async def compare_documents(file1: UploadFile = File(...), file2: UploadFile = File(...)):
    """
    Endpoint to compare two documents and extract information.
    Accepts JPEG, JPG, or PDF files.
    """
    # Generate a unique request ID
    request_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    log_context = {'request_id': request_id}
    
    logger.info(f"Starting document comparison for files: {file1.filename} and {file2.filename}", extra=log_context)
    
    try:
        # Validate file types
        logger.info("Validating file types", extra=log_context)
        validate_file_type(file1)
        validate_file_type(file2)
        
        # Read and process first image
        logger.info(f"Processing first file: {file1.filename}", extra=log_context)
        image1_content = await file1.read()
        image1 = PIL.Image.open(io.BytesIO(image1_content))
        
        # Read and process second image
        logger.info(f"Processing second file: {file2.filename}", extra=log_context)
        image2_content = await file2.read()
        image2 = PIL.Image.open(io.BytesIO(image2_content))
        
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
        
    except Exception as e:
        logger.error(
            f"Error during document comparison: {str(e)}",
            exc_info=True,
            extra=log_context
        )
        raise HTTPException(status_code=500, detail=str(e))
# Optional: Add a health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}