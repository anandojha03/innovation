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
import asyncio  
from typing import Optional

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
genai.configure(api_key="AIzaSyCgjshow09gS-O6g0k4P6fOl9zJmR0TXkU")
# alternate
# genai.configure(api_key="AIzaSyDv-v0xPb2IC4oExloK9a-CjAIMpL07TLc")
model = genai.GenerativeModel("gemini-1.5-flash")

# Define field mappings for each image type
EXPECTED_FIELDS = {
    "user_name": "Company Name",
    "user_id": "MFID",
    "bureau_name": "Bank Bureau Name",
    "amt_limit_in_figures": "Amount Limit in Figures",
    "amt_limit_in_words": "Amount Limit in Words",
    "limit_frequency": "Limit Frequency",
    "period_ending": "Period Ending",
    "drawing_account_name": "Drawing Account Name",
    "bsb": "BSB Number",
    "account_number": "Account Number",
    "temporary_processing_limit_override": "Temporary Processing Limit Override"
}

UI_FIELDS = [
    "Company Name",
    "MFID",
    "Bank Bureau Name",
    "Amount Limit in Figures",
    "Amount Limit in Words",
    "Limit Frequency",
    "Period Ending",
    "Drawing Account Name",
    "BSB Number",
    "Account Number",
    "Temporary Processing Limit Override"
]

MAPPING_IMG1 = {
    "Company name (User name)": "user_name",
    "MFID": "user_id",
    "Lodging party (Other Bank Bureau name)": "bureau_name",
    "Maximum total value of entries per processing cycle (Non Cumulative - not including charges)": "amt_limit_in_figures",
    "Amount in words": "amt_limit_in_words",
    "Processing cycle covering maximum peak value": "limit_frequency",
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
    i = 0;

    for field, ui in common_fields.items():
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
            matching_fields[ui] = values[0]  # Keep the original non-normalized value
        else:
            mismatched_fields[ui] = values

        i = i+1

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

# form filler backend


class FormExtractionRequest(BaseModel):
    image: str  # Base64 encoded image string

class FormFields(BaseModel):
    user_name: Optional[str] = None
    user_id: Optional[str] = None
    bureau_name: Optional[str] = None
    amt_limit_in_figures: Optional[str] = None
    amt_limit_in_words: Optional[str] = None
    limit_frequency: Optional[str] = None
    period_ending: Optional[str] = None
    drawing_account_name: Optional[str] = None
    bsb: Optional[str] = None
    account_number: Optional[str] = None
    temporary_processing_limit_override: Optional[str] = None

def clean_base64(data: str) -> str:
    """Handle data URI prefix if present"""
    if data.startswith("data:image"):
        return data.split(",", 1)[1]
    return data

@app.post("/extract-form", response_model=FormFields)
async def extract_form(data: FormExtractionRequest):
    try:
        # Clean and decode base64
        cleaned_base64 = clean_base64(data.image)
        image_bytes = base64.b64decode(cleaned_base64)
        
        # Verify image validity
        image = PIL.Image.open(io.BytesIO(image_bytes))
        image.verify()  # Check if image is valid
        
        # Reopen for actual processing
        image = PIL.Image.open(io.BytesIO(image_bytes))

        # Create structured prompt
        prompt = f"""Analyze this financial document image and extract these fields:
        {json.dumps({v: f"from '{k}'" for k, v in MAPPING_IMG1.items()}, indent=4)}

        Rules:
        1. Return valid JSON ONLY
        2. Use field names: {list(MAPPING_IMG1.values())}
        3. Preserve original formatting
        4. Return null for missing fields
        5. Handle dates as strings in original format
        6. Currency values should include symbols
        7. Same exact field names might not be present but contextually they can be same

        JSON Output:"""

        # Generate response
        response = model.generate_content([prompt, image])
        
        # Extract JSON from response
        response_text = response.text.strip()
        json_str = response_text.split("{", 1)[-1].rsplit("}", 1)[0]
        json_str = "{" + json_str + "}"
        
        extracted_data = json.loads(json_str)
        return FormFields(**extracted_data)

    except (base64.binascii.Error, ValueError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid image data: {str(e)}")
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, 
                          detail=f"Failed to parse Gemini response: {str(e)}. Response was: {response_text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {"status": "healthy"}