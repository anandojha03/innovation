import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
import time

def convert_html_to_jpg(input_dir, output_dir):
    """
    Convert HTML files to JPG images
    
    Args:
        input_dir (str): Directory containing HTML files in form1 and form2 subdirectories
        output_dir (str): Directory to save JPG files
    """
    # Create output directories if they don't exist
    os.makedirs(os.path.join(output_dir, "form1"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "form2"), exist_ok=True)
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=900,1200")  # Set window size
    
    # Initialize the driver
    driver = webdriver.Chrome(options=chrome_options)
    
    # Process both form directories
    for form_dir in ["form1", "form2"]:
        html_dir = os.path.join(input_dir, form_dir)
        jpg_dir = os.path.join(output_dir, form_dir)
        
        # Get all HTML files in the directory
        html_files = [f for f in os.listdir(html_dir) if f.endswith('.html')]
        
        for html_file in html_files:
            # Construct file paths
            html_path = os.path.join(html_dir, html_file)
            jpg_path = os.path.join(jpg_dir, html_file.replace('.html', '.jpg'))
            
            try:
                # Load the HTML file
                file_url = f"file:///{os.path.abspath(html_path)}"
                driver.get(file_url)
                
                # Wait for page to load
                time.sleep(1)
                
                # Get page dimensions
                height = driver.execute_script("return Math.max(document.body.scrollHeight, document.body.offsetHeight);")
                width = driver.execute_script("return Math.max(document.body.scrollWidth, document.body.offsetWidth);")
                
                # Set window size to match content
                driver.set_window_size(width + 100, height + 100)
                
                # Take screenshot
                driver.save_screenshot(jpg_path)
                
                # Optimize the image
                with Image.open(jpg_path) as img:
                    img = img.convert('RGB')
                    img.save(jpg_path, 'JPEG', quality=95, optimize=True)
                
                print(f"Converted {html_file} to JPG")
                
            except Exception as e:
                print(f"Error converting {html_file}: {str(e)}")
    
    # Close the driver
    driver.quit()
    print("Conversion completed!")

# Example usage:
if __name__ == "__main__":
    input_directory = "test_pages"  # Directory containing HTML files
    output_directory = "test_pages_jpg"  # Directory to save JPG files
    convert_html_to_jpg(input_directory, output_directory)