import google.generativeai as genai
import PIL.Image
import json
import jsondiff
import pprint
genai.configure(api_key="AIzaSyDv-v0xPb2IC4oExloK9a-CjAIMpL07TLc")
model = genai.GenerativeModel("gemini-1.5-flash")

# generateconfig = {response_mime_type: 'application/json'}

image_path1 = "images/img1.jpg"
image_path2 = "images/img2.jpg"

image1 = PIL.Image.open(image_path1)
image2 = PIL.Image.open(image_path2)

mapping_img1 = {
    "Company name (User name)": "user_name",
    "MEID": "user_id",
    "Sponsor Bank": "sponsor_bank",
    "Processing Bank": "processing_bank",
    "Amount in Figures": "amt_in_figures",
    "Amount in words": "amt_in_words"
}

mapping_img2 = {
    "DE user name": "user_name",
    "DE user ID": "user_id",
    "Amount in Figures": "amt_in_figures",
    "Amount in words": "amt_in_words",
    "TNA prepared by": "sponsor_bank",
    "TNA approved by": "processing_bank",
}

fields1 = {
    "Company name (User name)",
    "MEID",
    "Sponsor Bank"
    "Processing Bank",
    "Amount in Figures",
    "Amount in words"
}

fields2 = {
    "DE user name",
    "DE user ID",
    "TNA prepared by",
    "TNA approved by",
    "Processing amount limit that will contain in words and number both"
}

prompt1 = f"Extract values of fields {fields1} in json from the first image and change there key name as {mapping_img1}. Return type should be json only. currently returning"
response1 = model.generate_content([prompt1, image1], generation_config=genai.GenerationConfig(response_mime_type="application/json"))

prompt2 = f"extract values of fields {fields2} in json from second image and change there key name as {mapping_img2}"
response2 = model.generate_content([prompt2, image2], generation_config=genai.GenerationConfig(response_mime_type="application/json"))


response1=json.loads(response1.text)

response2=json.loads(response2.text)

pp=pprint.PrettyPrinter(depth=4)

pp.pprint(response1)
print()
pp.pprint(response2)
print()

print(response1["amt_in_figures"] == response2["amt_in_figures"])
