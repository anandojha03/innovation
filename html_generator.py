import os
import random
from datetime import datetime, timedelta

def generate_test_pages(output_dir="test_pages"):
    """Generate 99 pairs of HTML test pages using the NAB form template"""
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(os.path.join(output_dir, "form1"))
        os.makedirs(os.path.join(output_dir, "form2"))

    # Test data variations remain the same
    company_names = [
        "XYZ Corp", "ABC Limited", "Tech Solutions", "Global Trading",
        "First Securities", "Summit Industries", "Peak Enterprises",
        "Value Chain", "Metro Group", "Stellar Systems"
    ]
    
    user_ids = [
        "123456", "234567", "345678", "456789", "567890",
        "654321", "765432", "876543", "987654", "098765"
    ]
    
    amounts = [
        ("10000000", "TEN MILLION"),
        ("5000000", "FIVE MILLION"),
        ("15000000", "FIFTEEN MILLION"),
        ("20000000", "TWENTY MILLION"),
        ("7500000", "SEVEN MILLION FIVE HUNDRED THOUSAND"),
        ("3000000", "THREE MILLION"),
        ("1000000", "ONE MILLION"),
        ("2500000", "TWO MILLION FIVE HUNDRED THOUSAND"),
        ("4000000", "FOUR MILLION"),
        ("6000000", "SIX MILLION")
    ]
    
    processing_banks = [
        "PROCESING BANK", "WESTPAC", "ANZ", "COMMONWEALTH",
        "BENDIGO", "MACQUARIE", "HSBC", "CITIBANK"
    ]

    def generate_form1(index, data):
        """Generate NAB form HTML with enhanced CSS"""
        date = (datetime.now() + timedelta(days=index)).strftime("%d / %m / %y")
        
        return f"""

                <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>NAB Form {index}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 20px auto;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }}

        .form-container {{
            background-color: white;
            padding: 20px;
            border: 1px solid #ccc;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            border-bottom: 1px solid #000;
            padding-bottom: 10px;
        }}

        .logo {{
            background-color: #000;
            padding: 10px 15px;
            display: inline-block;
        }}

        .logo span {{
            color: white;
            font-weight: bold;
            font-size: 24px;
        }}

        .logo .leaf {{
            color: #FF0000;
            margin-right: 5px;
        }}

        .title {{
            flex-grow: 1;
            text-align: right;
            font-size: 16px;
            font-weight: bold;
            line-height: 1.4;
        }}

        .instruction {{
            background-color: #000;
            color: white;
            padding: 5px 10px;
            margin: 10px 0;
            font-size: 12px;
        }}

        .date-field {{
            text-align: right;
            margin: 10px 0;
        }}

        .date-input {{
            border: 1px solid #000;
            padding: 5px;
            width: 150px;
        }}

        .section {{
            margin-bottom: 20px;
            border: 1px solid #000;
            padding: 15px;
        }}

        .section-header {{
            background-color: #000;
            color: white;
            padding: 5px 10px;
            margin: -15px -15px 15px -15px;
            font-weight: bold;
        }}

        .form-row {{
            display: flex;
            gap: 20px;
            margin-bottom: 15px;
        }}

        .form-group {{
            flex: 1;
        }}

        .form-group.half {{
            flex: 0.5;
        }}

        label {{
            display: block;
            font-size: 12px;
            margin-bottom: 5px;
        }}

        input[type="text"] {{
            width: 100%;
            padding: 5px;
            border: 1px solid #ccc;
            font-size: 14px;
        }}

        .nominated-accounts {{
            margin: 15px 0;
        }}

        .signature-section {{
            margin-top: 15px;
            border-top: 1px solid #ccc;
            padding-top: 15px;
        }}

        .processing-cycle {{
            border: 2px solid #FF0000;
            padding: 15px;
            margin: 15px 0;
        }}

        .checkbox-group {{
            display: flex;
            gap: 20px;
            margin: 10px 0;
        }}

        .checkbox-label {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}

        .bank-use {{
            background-color: #f9f9f9;
            padding: 15px;
            border: 1px solid #ccc;
            margin-top: 20px;
        }}

        .implementation-section {{
            margin-top: 15px;
            border-top: 1px solid #ccc;
            padding-top: 15px;
        }}

        .footer {{
            margin-top: 20px;
            font-size: 10px;
            color: #666;
        }}

        .signature-line {{
            border-bottom: 1px solid #000;
            margin-top: 20px;
            position: relative;
        }}

        .signature-x {{
            position: absolute;
            left: 10px;
            top: -10px;
            color: #FF0000;
            font-weight: bold;
        }}

        .email-footer {{
            margin-top: 10px;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="form-container">
        <div class="header">
            <div class="logo">
                <span class="leaf">★</span>
                <span>nab</span>
            </div>
            <div class="title">
                Other Bank Bureau - Request NAB set up<br>
                Direct Entry Transaction Negotiation Authority (TNA)
            </div>
        </div>

        <div class="instruction">
            Please use blue or black pen and write in BLOCK LETTERS
        </div>

        <div class="date-field">
            <label>Date</label>
            <input type="text" class="date-input" value="13 / 12 / 24">
        </div>

        <div class="section">
            <div class="section-header">Part A</div>
            <p>We request NAB to establish a Direct Credit Transaction Negotiation Authority, authorising the below named Bank to accept payment instructions lodged by the below named Bureau, which include direct credit entries on our behalf, and to act on items (identified by the User Identification number you assign to us) to the value of the processing limit, limit frequency and period specified.</p>
            <p>In consideration of granting this request you are hereby authorised to debit our nominated account for the value of these transactions, establishment fees and associated processing charges including charges imposed by the Bureau Bank.</p>
            <p>We acknowledge that NAB may in its discretion give priority to drawings under the authority over any cheques or other mandate or authority drawn or given now or in the future.</p>
        </div>

        <div class="section">
            <div class="section-header">Part B</div>
            <div class="form-row">
                <div class="form-group">
                    <label>Company name (User name)</label>
                    <input type="text" value="{data['company_name']}">
                </div>
                <div class="form-group">
                    <label>MFID</label>
                    <input type="text" value="{data['user_id']}">
                </div>
                <div class="form-group">
                    <label>Credit User Identification no. (NAB to allocate unless specified)</label>
                    <input type="text">
                </div>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <label>Lodging party (Other Bank Bureau name)</label>
                    <input type="text">
                </div>
                <div class="form-group">
                    <label>Contact name and details (phone and/or email)</label>
                    <input type="text">
                </div>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <label>Sponsor Bank</label>
                    <input type="text" value="{data['sponsor_bank']}">
                </div>
                <div class="form-group">
                    <label>Processing Bank</label>
                    <input type="text" value="{data['processing_bank']}">
                </div>
                <div class="form-group">
                    <label>Contact name and details (phone and/or email)</label>
                    <input type="text">
                </div>
            </div>

            <div class="nominated-accounts">
                <h4>Nominated Accounts</h4>
                <div class="form-row">
                    <div class="form-group">
                        <label>Name of Account to be debited for payments</label>
                        <input type="text">
                    </div>
                    <div class="form-group half">
                        <label>BSB no.</label>
                        <input type="text">
                    </div>
                    <div class="form-group half">
                        <label>Account no.</label>
                        <input type="text">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Name of account to be debited for charges</label>
                        <input type="text">
                    </div>
                    <div class="form-group half">
                        <label>BSB no.</label>
                        <input type="text">
                    </div>
                    <div class="form-group half">
                        <label>Account no.</label>
                        <input type="text">
                    </div>
                </div>
            </div>

            <div class="signature-section">
                <label>Authorised signature/s (Sign in terms of Notice of Authority to Transact Banking Business)</label>
                <div class="signature-line">
                    <span class="signature-x">X</span>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Name and Title</label>
                        <input type="text">
                    </div>
                    <div class="form-group">
                        <label>Contact telephone no.</label>
                        <input type="text">
                    </div>
                </div>
            </div>
        </div>

        <div class="processing-cycle">
            <div class="section-header">Part C</div>
            <label>Processing cycle covering maximum peak value (select one)</label>
            <div class="checkbox-group">
                <label class="checkbox-label"><input type="checkbox"> daily</label>
                <label class="checkbox-label"><input type="checkbox"> weekly</label>
                <label class="checkbox-label"><input type="checkbox" checked> fortnightly</label>
                <label class="checkbox-label"><input type="checkbox"> monthly</label>
                <label class="checkbox-label"><input type="checkbox"> Other (specify)</label>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <label>Maximum total value of entries per processing cycle (Non Cumulative - not including charges)</label>
                    <input type="text" value="$ {data['amount_figures']}">
                </div>
                <div class="form-group">
                    <label>Amount in words</label>
                    <input type="text" value="{data['amount_words']}">
                </div>
            </div>
        </div>

        <div class="bank-use">
            <h3>Bank Use Only</h3>
            <div class="form-row">
                <div class="form-group">
                    <label>Banker name</label>
                    <input type="text" value="XYZ">
                </div>
                <div class="form-group">
                    <label>BUID</label>
                    <input type="text" value="12345678">
                </div>
                <div class="form-group">
                    <label>Phone no.</label>
                    <input type="text">
                </div>
                <div class="form-group">
                    <label>Approved limit</label>
                    <input type="text" value="$ 10000000">
                </div>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <label>Customer Number</label>
                    <input type="text" value="12345678">
                </div>
            </div>

            <div class="implementation-section">
                <div class="checkbox-group">
                    <label class="checkbox-label"><input type="checkbox"> Credit User Application</label>
                    <label class="checkbox-label"><input type="checkbox"> LC 108 registered & formal limit LOO created</label>
                    <label class="checkbox-label"><input type="checkbox"> UDD = Bureau User Credit</label>
                    <label class="checkbox-label"><input type="checkbox"> OBB TNA Request (this document)</label>
                </div>

                <div class="signature-line">
                    <span class="signature-x">X</span>
                </div>
                <label>Request and limit approved by - Signature</label>

                <div class="form-row">
                    <div class="form-group">
                        <label>Implementation - Specialised Products</label>
                        <div class="checkbox-group">
                            <label class="checkbox-label"><input type="checkbox"> TNA completed</label>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Bank Stamp</label>
                        <div style="border: 1px solid #ccc; height: 100px;"></div>
                    </div>
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label>Input by - Initial</label>
                        <input type="text">
                    </div>
                    <div class="form-group">
                        <label>Date</label>
                        <input type="text">
                    </div>
                    <div class="form-group">
                        <label>Checked by - Initial</label>
                        <input type="text">
                    </div>
                    <div class="form-group">
                        <label>Date</label>
                        <input type="text">
                    </div>
                </div>
            </div>
        </div>

        <div class="email-footer">
            Email copies to: Specialised.Products@nab.com.au
        </div>

        <div class="footer">
            ©2013 National Australia Bank Limited ABN 12 004 044 937 AFSL and Australian Credit License 230686 A102952-0613
        </div>
    </div>
</body>
</html>
        """

    def generate_form2(index, data):
        """Generate TNA form HTML"""
        date = (datetime.now() + timedelta(days=index)).strftime("%d/%m/%Y")
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 20px auto;
                    padding: 20px;
                    line-height: 1.6;
                }}

                .container {{
                    border: 1px solid #000;
                    padding: 20px;
                }}

                .header {{
                    text-align: center;
                    margin-bottom: 20px;
                    border-bottom: 1px solid #ccc;
                    padding-bottom: 10px;
                }}

                .header h1 {{
                    font-size: 18px;
                    margin: 0;
                }}

                .header p {{
                    font-size: 12px;
                    margin: 5px 0;
                    color: #333;
                }}

                .main-content {{
                    margin-bottom: 20px;
                }}

                .details-section {{
                    margin-top: 20px;
                }}

                .details-section h2 {{
                    font-size: 16px;
                    margin-bottom: 10px;
                }}

                .details-grid {{
                    display: grid;
                    grid-template-columns: auto 1fr;
                    gap: 5px;
                    font-size: 14px;
                }}

                .details-grid dt {{
                    font-weight: normal;
                }}

                .details-grid dd {{
                    margin-left: 10px;
                }}

                .footer {{
                    font-size: 12px;
                    color: #666;
                    margin-top: 20px;
                    border-top: 1px solid #eee;
                    padding-top: 10px;
                }}

                ol {{
                    margin-left: 20px;
                    padding-left: 0;
                }}

                ol li {{
                    margin-bottom: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Transaction Negotiation Authority (TNA)</h1>
                    <p>Issued by National Australia Bank Limited in compliance with<br>BECS Procedures<br>Appendix A8</p>
                </div>

                <div class="main-content">
                    <p>National Australia Bank Limited ACN/ABN/ARBN 12 004 044 937<br>authorises<br>{data['processing_bank']} in accordance with the TNA details below:</p>

                    <ol>
                        <li>to accept files which include credit items from the nominated DE User or its nominated Bureau; and</li>
                        <li>to act on those items for the amount, the period, and the frequency specified below; or for such other processing amount as National Australia Bank Limited may from time to time advise; and</li>
                        <li>to draw on the account nominated for the total value of those items plus any charges applied by {data['processing_bank']}</li>
                    </ol>

                    <p>In consideration of {data['processing_bank']} Limited accepting files and acting on items, National Australia Bank Limited agrees to accept all drawings initiated by Bendigo and Adelaide Bank Limited under this authority</p>

                    <p>National Australia Bank Limited may terminate this authority by notice to {data['processing_bank']} Limited, without prejudice to liabilities incurred or arising prior to termination. Termination does not take effect before receipt of the notice is acknowledged by {data['processing_bank']}</p>
                </div>

                <div class="details-section">
                    <h2>TNA Details</h2>
                    <dl class="details-grid">
                        <dt>DE User Name:</dt>
                        <dd>{data['company_name']}</dd>
                        <dt>DE User ID:</dt>
                        <dd>{data['user_id']}</dd>
                        <dt>Via Bureau:</dt>
                        <dd>{data['processing_bank']}</dd>
                        <dt>Processing limit amount:</dt>
                        <dd>{data['amount_words']} (${data['amount_figures']})</dd>
                        <dt>Limit frequency:</dt>
                        <dd>Fortnightly</dd>
                        <dt>Period commencing:</dt>
                        <dd>{date}</dd>
                        <dt>Period ending:</dt>
                        <dd>until further notice</dd>
                        <dt>Drawing account name:</dt>
                        <dd>{data['company_name']}</dd>
                        <dt>BSB:</dt>
                        <dd>123456</dd>
                        <dt>Account number:</dt>
                        <dd>12345678</dd>
                        <dt>Temporary processing limit override:</dt>
                        <dd>None</dd>
                    </dl>
                </div>

                <div class="details-section">
                    <h2>User FI approval</h2>
                    <dl class="details-grid">
                        <dt>TNA prepared by:</dt>
                        <dd>Authorised signatory from {data['sponsor_bank']}</dd>
                        <dt>TNA approved by:</dt>
                        <dd>Authorised signatory from {data['processing_bank']}</dd>
                    </dl>
                </div>

                <div class="details-section">
                    <h2>Lodgement FI approval</h2>
                    <dl class="details-grid">
                        <dt>TNA approved by:</dt>
                        <dd>Authorised signatory from {data['processing_bank']}</dd>
                    </dl>
                </div>

                <div class="footer">
                    <p>This form was generated on the AusPayNet BUDS & TNA system on {date} 4:19pm</p>
                    <p>All times refer to the time in Sydney NSW</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    # Generate test pages
    # Generate 33 complete matches
    for i in range(33):
        data = {
            'company_name': random.choice(company_names),
            'user_id': random.choice(user_ids),
            'sponsor_bank': "NAB",
            'processing_bank': random.choice(processing_banks),
            'amount_figures': "10000000",
            'amount_words': "TEN MILLION"
        }
        
        with open(f"{output_dir}/form1/complete_match_{i+1}.html", "w", encoding='utf-8') as f:
            f.write(generate_form1(i, data))
        with open(f"{output_dir}/form2/complete_match_{i+1}.html", "w", encoding='utf-8') as f:
            f.write(generate_form2(i, data))

    # Generate 33 partial matches
    for i in range(33):
        base_data = {
            'company_name': random.choice(company_names),
            'user_id': random.choice(user_ids),
            'sponsor_bank': "NAB",
            'processing_bank': random.choice(processing_banks),
            'amount_figures': random.choice(amounts)[0],
            'amount_words': random.choice(amounts)[1]
        }
        
        modified_data = base_data.copy()
        fields_to_modify = random.sample(['company_name', 'user_id', 'amount_figures'], random.randint(1, 2))
        
        for field in fields_to_modify:
            if field == 'company_name':
                modified_data['company_name'] = random.choice([n for n in company_names if n != base_data['company_name']])
            elif field == 'user_id':
                modified_data['user_id'] = random.choice([id for id in user_ids if id != base_data['user_id']])
            else:
                new_amount = random.choice([a for a in amounts if a[0] != base_data['amount_figures']])
                modified_data['amount_figures'] = new_amount[0]
                modified_data['amount_words'] = new_amount[1]
        
        with open(f"{output_dir}/form1/partial_match_{i+1}.html", "w", encoding='utf-8') as f:
            f.write(generate_form1(i+33, base_data))
        with open(f"{output_dir}/form2/partial_match_{i+1}.html", "w", encoding='utf-8') as f:
            f.write(generate_form2(i+33, modified_data))

    # Generate 33 non-matches
    for i in range(33):
        data1 = {
            'company_name': random.choice(company_names),
            'user_id': random.choice(user_ids),
            'sponsor_bank': random.choice(processing_banks),
            'processing_bank': random.choice(processing_banks),
            'amount_figures': random.choice(amounts)[0],
            'amount_words': random.choice(amounts)[1]
        }
        
        data2 = {
            'company_name': random.choice([n for n in company_names if n != data1['company_name']]),
            'user_id': random.choice([id for id in user_ids if id != data1['user_id']]),
            'sponsor_bank': "NAB",
            'processing_bank': random.choice([b for b in processing_banks if b != data1['processing_bank']]),
            'amount_figures': random.choice([a[0] for a in amounts if a[0] != data1['amount_figures']]),
            'amount_words': random.choice([a[1] for a in amounts if a[1] != data1['amount_words']])
        }
        
        with open(f"{output_dir}/form1/no_match_{i+1}.html", "w", encoding='utf-8') as f:
            f.write(generate_form1(i+66, data1))
        with open(f"{output_dir}/form2/no_match_{i+1}.html", "w", encoding='utf-8') as f:
            f.write(generate_form2(i+66, data2))

    return "Generated 99 pairs of test pages in the 'test_pages' directory"

# Execute the generator
if __name__ == "__main__":
    result = generate_test_pages()
    print(result)