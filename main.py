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
import os
import asyncio  # Added missing import

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
os.makedirs('logs', exist_ok=True)

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

# Define field mappings for each image type
EXPECTED_FIELDS = {
    "user_name",
    "user_id",
    "bureau_name",
    "amt_limit_in_figures",
    "amt_limit_in_words",
    "limit_frequency",
    "period_commencing",
    "period_ending",
    "drawing_account_name",
    "bsb",
    "account_number",
    "temporary_processing_limit_override"
}

MAPPING_IMG1 = {
    "Company name (User name)": "user_name",
    "MFID": "user_id",
    "Lodging party (Other Bank Bureau name)": "bureau_name",
    "Maximum total value of entries per processing cycle (Non Cumulative - not including charges)": "amt_limit_in_figures",
    "Amount in words": "amt_limit_in_words",
    "Processing cycle covering maximum peak value": "limit_frequency",
    "Date": "period_commencing",
    "Period ending": "period_ending",
    "Name of Account to be debited for payments": "drawing_account_name",
    "BSB no.": "bsb",
    "Account no.": "account_number",
    "Temporary processing limit override": "temporary_processing_limit_override"
}

MAPPING_IMG2 = {
    "User name": "user_name",
    "User ID number": "user_id",
    "Bureau name": "bureau_name",
    "Processing limit": "amt_limit_in_figures",
    "Processing limit under letter-container div": "amt_limit_in_words",
    "Limit frequency": "limit_frequency",
    "Date inside letter-container div": "period_commencing",
    "Period ending": "period_ending",
    "Account nominated for drawings": "drawing_account_name",
    "BSB Number": "bsb",
    "Account Number": "account_number"
}

MAPPING_IMG3 = {
    "DE User Name": "user_name",
    "DE User ID": "user_id",
    "Via Bureau": "bureau_name",
    "Processing limit amount in brackets": "amt_limit_in_figures",
    "Processing limit amount": "amt_limit_in_words",
    "Limit frequency": "limit_frequency",
    "Period commencing": "period_commencing",
    "Period ending": "period_ending",
    "Drawing account name": "drawing_account_name",
    "BSB": "bsb",
    "Account number": "account_number",
    "Temporary processing limit override": "temporary_processing_limit_override"
}

# Pydantic models
class CompareRequest(BaseModel):
    captures: List[str]  # List of base64-encoded images

class ComparisonResponse(BaseModel):
    response1: dict
    response2: dict
    response3: dict
    comparison_result: dict

def get_overall_status(matching_count: int, total_fields: int) -> str:
    """Determine the overall match status based on matching field count."""
    if matching_count == total_fields:
        return "Complete Match"
    elif matching_count > 0:
        return "Partial Match"
    return "No Match"

def normalize_value(value: str) -> str:
    """
    Normalize values by removing special characters and standardizing format.
    """
    if not isinstance(value, str):
        value = str(value)
    
    # Remove special characters, spaces, and convert to lowercase
    normalized = ''.join(char for char in value if char.isalnum()).lower()
    
    return normalized

def values_match(value1: str, value2: str) -> bool:
    """
    Compare two values after normalization.
    """
    return normalize_value(value1) == normalize_value(value2)

# Update the compare_responses function
def compare_responses(responses: List[Dict]) -> Dict:
    """
    Compare multiple response dictionaries and return a detailed comparison result.
    Uses normalized values for comparison.
    """
    common_fields = EXPECTED_FIELDS
    matching_fields = {}
    mismatched_fields = {}

    for field in common_fields:
        # Collect all available values for this field
        values = [
            response.get(field) for response in responses 
            if field in response and response.get(field) is not None
        ]
        
        if not values:
            continue

        # Check if all normalized values are identical
        normalized_values = [normalize_value(value) for value in values]
        if all(norm_val == normalized_values[0] for norm_val in normalized_values):
            matching_fields[field] = values[0]  # Keep the original non-normalized value
        else:
            mismatched_fields[field] = values

    overall_status = get_overall_status(len(matching_fields), len(common_fields))

    return {
        "status": overall_status,
        "matching_fields": matching_fields,
        "mismatched_fields": mismatched_fields,
        "normalized_matches": {
            field: {
                "original_values": values,
                "normalized_value": normalize_value(values[0])
            }
            for field, values in matching_fields.items()
        }
    }

async def process_image(image: PIL.Image.Image, image_type: int) -> dict:
    """Process a single image with Gemini AI using specific mapping."""
    mapping = {
        1: MAPPING_IMG1,
        2: MAPPING_IMG2,
        3: MAPPING_IMG3
    }[image_type]

    prompt = f"""
    Extract information from this image using the following guidelines:
    
    1. Extract values for all visible fields and map them according to these rules: {mapping}
    2. For amount fields:
       - Remove any currency symbols or commas
       - Keep only the numeric value for figures
       - Keep only the words for word amounts
    3. For dates:
       - Return in DD/MM/YYYY format
    4. For period_ending:
       - If not explicitly mentioned, return "Until further notice"
    5. For temporary_processing_limit_override:
       - If not mentioned, return "none"
    6. For limit_frequency:
       - Return only the selected/ticked option
    
    Format the output as a strict JSON object with the mapped field names as keys.
    Remove any prefixes, suffixes, or additional text from the extracted values.
    Ensure all values are strings.
    """

    try:
        response = model.generate_content(
            [prompt, image],
            generation_config=genai.GenerationConfig(
                temperature=0.1,
                response_mime_type="application/json"
            )
        )
        extracted_data = json.loads(response.text)
        
        # Apply default values for missing fields
        if 'period_ending' not in extracted_data:
            extracted_data['period_ending'] = "Until further notice"
        if 'temporary_processing_limit_override' not in extracted_data:
            extracted_data['temporary_processing_limit_override'] = "none"
            
        return extracted_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image {image_type}: {str(e)}")

def base64_to_image(base64_str: str) -> PIL.Image.Image:
    """Convert a base64-encoded string to a PIL image."""
    try:
        image_data = base64.b64decode(base64_str)
        return PIL.Image.open(io.BytesIO(image_data))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 image data: {str(e)}")

@app.post("/compare_documents/", response_model=ComparisonResponse)
async def compare_documents(request: CompareRequest):
    """
    Endpoint to compare three documents and extract information.
    Accepts three base64-encoded images.
    """
    request_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    log_context = {'request_id': request_id}

    logger.info("Starting document comparison", extra=log_context)

    try:
        if len(request.captures) != 3:
            raise HTTPException(status_code=400, detail="Exactly three images are required for comparison.")

        logger.info("Converting base64 images to PIL images", extra=log_context)
        images = [base64_to_image(capture) for capture in request.captures]

        logger.info("Processing images with Gemini", extra=log_context)
        responses = await asyncio.gather(*[
            process_image(img, idx + 1) for idx, img in enumerate(images)
        ])

        comparison_result = compare_responses(responses)
        print(f" here is the response which recived from gemini " , responses)

        logger.info(
            f"Comparison completed. Status: {comparison_result.get('status', 'Unknown')}",
            extra=log_context
        )


        return ComparisonResponse(
            response1=responses[0],
            response2=responses[1],
            response3=responses[2],
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

@app.get("/health")
async def health_check():
    return {"status": "healthy"}