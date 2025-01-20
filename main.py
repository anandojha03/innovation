from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import google.generativeai as genai
import PIL.Image
import json
from typing import List
import io
import os
from pydantic import BaseModel

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
    amounts_match: bool

async def process_image(image: PIL.Image.Image, fields: set, mapping: dict) -> dict:
    """Process a single image with Gemini AI."""
    prompt = f"Extract values of fields {fields} in json from the image and change their key names as {mapping}. Return type should be json only."
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
    # Validate file types
    validate_file_type(file1)
    validate_file_type(file2)
    
    try:
        # Read and process first image
        image1_content = await file1.read()
        image1 = PIL.Image.open(io.BytesIO(image1_content))
        
        # Read and process second image
        image2_content = await file2.read()
        image2 = PIL.Image.open(io.BytesIO(image2_content))
        
        # Process both images
        response1 = await process_image(image1, FIELDS1, MAPPING_IMG1)
        response2 = await process_image(image2, FIELDS2, MAPPING_IMG2)
        
        # Compare amounts
        amounts_match = response1["amt_in_figures"] == response2["amt_in_figures"]
        
        return ComparisonResponse(
            response1=response1,
            response2=response2,
            amounts_match=amounts_match
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Optional: Add a health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}