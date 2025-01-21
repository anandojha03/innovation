import os
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime

def test_document_comparison():
    # Configuration
    BASE_URL = "http://127.0.0.1:8000"  # Adjust as needed
    ENDPOINT = "/compare-documents/"
    TOTAL_TESTS = 5
    
    # Setup directories
    form1_dir = Path("test_pages_jpg/form1")
    form2_dir = Path("test_pages_jpg/form2")
    
    # Initialize results storage
    successful_matches = []
    total_passed = 0
    
    # Process each pair of files
    for i in range(1, TOTAL_TESTS + 1):
        filename = f"complete_match_{i}.jpg"
        file1_path = form1_dir / filename
        file2_path = form2_dir / filename
        
        # Skip if either file doesn't exist
        if not file1_path.exists() or not file2_path.exists():
            print(f"Skipping test {i}: One or both files missing")
            continue
        
        # Prepare files for upload
        files = {
            'file1': ('file1.jpg', open(file1_path, 'rb'), 'image/jpeg'),
            'file2': ('file2.jpg', open(file2_path, 'rb'), 'image/jpeg')
        }
        
        try:
            # Make API request
            print(f"Trying to hit fastAPI with {file1_path} and {file2_path}")
            response = requests.post(f"{BASE_URL}{ENDPOINT}", files=files)
            response.raise_for_status()
            print(f"Got some response")
            # Process response
            result = response.json()
            
            if result['comparison_result']['Status'] == "Complete Match":
                successful_matches.append({
                    'Test Number': i,
                    'File1': str(file1_path),
                    'File2': str(file2_path),
                    'Full Response': str(result)
                })
                total_passed += 1
                
            print(f"Processed test {i}: {'Success' if result['comparison_result']['Status'] == 'Complete Match' else 'Failed'}")
            
        except Exception as e:
            print(f"Error processing test {i}: {str(e)}")
            
        finally:
            # Close file handles
            for f in files.values():
                f[1].close()
    
    # Create Excel report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"comparison_results_{timestamp}.xlsx"
    
    # Create DataFrame for successful matches
    df_matches = pd.DataFrame(successful_matches)
    
    # Create Excel writer object
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Write successful matches
        if successful_matches:
            df_matches.to_excel(writer, sheet_name='Successful Matches', index=False)
        
        # Write summary
        summary_data = {
            'Metric': ['Total Tests', 'Successful Matches', 'Success Rate'],
            'Value': [
                TOTAL_TESTS,
                total_passed,
                f"{(total_passed/TOTAL_TESTS)*100:.2f}%"
            ]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
    
    print(f"\nTest Summary:")
    print(f"Total tests: {TOTAL_TESTS}")
    print(f"Successful matches: {total_passed}")
    print(f"Success rate: {(total_passed/TOTAL_TESTS)*100:.2f}%")
    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    test_document_comparison()