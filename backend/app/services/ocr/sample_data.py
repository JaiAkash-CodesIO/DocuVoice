def get_sample_ocr_result(sample_name: str) -> dict:
    """Return precomputed OCR extraction data for preloaded demo documents."""
    name = sample_name.lower()

    if "invoice" in name:
        text = """================================================================
                       TAX INVOICE                              
================================================================

Invoice Number: INV-2026-9042
Invoice Date: 12-10-2026
Due Date: 26-10-2026

Vendor Details:
Apex Cloud Technologies Inc.
Email: billing@apexcloud.io
Phone: +1 800-555-0199
Website: https://apexcloud.io

Bill To:
Nexus Software Labs
Contact: contact@nexuslabs.dev
Phone: +1 800-555-9876

----------------------------------------------------------------
Item                    Qty         Unit Price        Total     
----------------------------------------------------------------
Cloud Hosting Cluster     2             500.00      1000.00     
Managed Database Tier     1             350.00       350.00     
SSL Security Package      3              50.00       150.00     
Support Retainer          1             200.00       200.00     
----------------------------------------------------------------

Subtotal: $1,700.00
Tax Amount (10%): $170.00
Total Amount Due: $1,870.00

Payment Terms: Net 14 Days. Thank you for your business!
================================================================"""

        words = [
            {"text": "TAX", "confidence": 98.0, "x": 500, "y": 80, "width": 60, "height": 20},
            {"text": "INVOICE", "confidence": 99.0, "x": 570, "y": 80, "width": 120, "height": 20},
            {"text": "Invoice Number: INV-2026-9042", "confidence": 97.0, "x": 60, "y": 140, "width": 260, "height": 18},
            {"text": "Invoice Date: 12-10-2026", "confidence": 96.0, "x": 60, "y": 175, "width": 220, "height": 18},
            {"text": "Vendor: Apex Cloud Technologies Inc.", "confidence": 95.0, "x": 60, "y": 245, "width": 320, "height": 18},
            {"text": "Email: billing@apexcloud.io", "confidence": 99.0, "x": 60, "y": 280, "width": 240, "height": 18},
            {"text": "Phone: +1 800-555-0199", "confidence": 98.0, "x": 60, "y": 315, "width": 210, "height": 18},
            {"text": "Website: https://apexcloud.io", "confidence": 99.0, "x": 60, "y": 350, "width": 250, "height": 18},
            {"text": "Customer: Nexus Software Labs", "confidence": 95.0, "x": 60, "y": 420, "width": 280, "height": 18},
            {"text": "Contact: contact@nexuslabs.dev", "confidence": 99.0, "x": 60, "y": 455, "width": 260, "height": 18},
            {"text": "Phone: +1 800-555-9876", "confidence": 97.0, "x": 60, "y": 490, "width": 210, "height": 18},
            # Table Header
            {"text": "Item", "confidence": 96.0, "x": 60, "y": 570, "width": 50, "height": 18},
            {"text": "Qty", "confidence": 96.0, "x": 380, "y": 570, "width": 40, "height": 18},
            {"text": "UnitPrice", "confidence": 95.0, "x": 520, "y": 570, "width": 90, "height": 18},
            {"text": "Total", "confidence": 96.0, "x": 720, "y": 570, "width": 50, "height": 18},
            # Table Row 1
            {"text": "CloudHosting", "confidence": 95.0, "x": 60, "y": 605, "width": 140, "height": 18},
            {"text": "2", "confidence": 98.0, "x": 380, "y": 605, "width": 20, "height": 18},
            {"text": "500.00", "confidence": 97.0, "x": 520, "y": 605, "width": 60, "height": 18},
            {"text": "1000.00", "confidence": 97.0, "x": 720, "y": 605, "width": 70, "height": 18},
            # Table Row 2
            {"text": "ManagedDatabase", "confidence": 94.0, "x": 60, "y": 640, "width": 160, "height": 18},
            {"text": "1", "confidence": 98.0, "x": 380, "y": 640, "width": 20, "height": 18},
            {"text": "350.00", "confidence": 96.0, "x": 520, "y": 640, "width": 60, "height": 18},
            {"text": "350.00", "confidence": 96.0, "x": 720, "y": 640, "width": 60, "height": 18},
            # Table Row 3
            {"text": "SSLSecurity", "confidence": 95.0, "x": 60, "y": 675, "width": 120, "height": 18},
            {"text": "3", "confidence": 98.0, "x": 380, "y": 675, "width": 20, "height": 18},
            {"text": "50.00", "confidence": 96.0, "x": 520, "y": 675, "width": 50, "height": 18},
            {"text": "150.00", "confidence": 96.0, "x": 720, "y": 675, "width": 60, "height": 18},
            # Table Row 4
            {"text": "SupportRetainer", "confidence": 94.0, "x": 60, "y": 710, "width": 150, "height": 18},
            {"text": "1", "confidence": 98.0, "x": 380, "y": 710, "width": 20, "height": 18},
            {"text": "200.00", "confidence": 96.0, "x": 520, "y": 710, "width": 60, "height": 18},
            {"text": "200.00", "confidence": 96.0, "x": 720, "y": 710, "width": 60, "height": 18},
            # Totals
            {"text": "Subtotal: $1,700.00", "confidence": 97.0, "x": 60, "y": 780, "width": 200, "height": 18},
            {"text": "Tax Amount: $170.00", "confidence": 96.0, "x": 60, "y": 815, "width": 190, "height": 18},
            {"text": "Total: $1,870.00", "confidence": 98.0, "x": 60, "y": 850, "width": 180, "height": 18},
        ]
        return {
            "text": text,
            "average_confidence": 96.8,
            "word_count": len(words),
            "words": words,
            "selected_variant": "tesseract-high-res",
            "selected_psm": 6,
        }

    if "receipt" in name:
        text = """****************************************
          METRO GROCERY STORE           
        104 Downtown Market Ave         
****************************************

Receipt: REC-88412
Date: 04-10-2026
Cashier: Robert M.
Payment Method: VISA Card Ending 4410

----------------------------------------
Item               Qty     Price   Total
----------------------------------------
Organic Milk         2      3.50    7.00
Whole Wheat Bread    1      2.80    2.80
Roasted Coffee       1     12.50   12.50
Fresh Apples         4      1.25    5.00
Mineral Water        6      1.00    6.00
----------------------------------------

Subtotal: $33.30
Tax Amount: $2.66
Total: $35.96

Thank you for your purchase!
Website: https://metrogrocery.com
****************************************"""

        words = [
            {"text": "METRO", "confidence": 97.0, "x": 350, "y": 60, "width": 80, "height": 20},
            {"text": "GROCERY", "confidence": 97.0, "x": 440, "y": 60, "width": 110, "height": 20},
            {"text": "Receipt: REC-88412", "confidence": 98.0, "x": 50, "y": 150, "width": 180, "height": 18},
            {"text": "Date: 04-10-2026", "confidence": 98.0, "x": 50, "y": 185, "width": 160, "height": 18},
            {"text": "Cashier: Robert M.", "confidence": 96.0, "x": 50, "y": 220, "width": 170, "height": 18},
            {"text": "Payment Method: VISA Card", "confidence": 95.0, "x": 50, "y": 255, "width": 240, "height": 18},
            # Header
            {"text": "Item", "confidence": 95.0, "x": 50, "y": 320, "width": 50, "height": 18},
            {"text": "Qty", "confidence": 95.0, "x": 260, "y": 320, "width": 40, "height": 18},
            {"text": "Price", "confidence": 95.0, "x": 380, "y": 320, "width": 50, "height": 18},
            {"text": "Total", "confidence": 95.0, "x": 490, "y": 320, "width": 50, "height": 18},
            # Row 1
            {"text": "OrganicMilk", "confidence": 96.0, "x": 50, "y": 355, "width": 120, "height": 18},
            {"text": "2", "confidence": 98.0, "x": 260, "y": 355, "width": 20, "height": 18},
            {"text": "3.50", "confidence": 97.0, "x": 380, "y": 355, "width": 40, "height": 18},
            {"text": "7.00", "confidence": 97.0, "x": 490, "y": 355, "width": 40, "height": 18},
            # Row 2
            {"text": "WheatBread", "confidence": 95.0, "x": 50, "y": 390, "width": 110, "height": 18},
            {"text": "1", "confidence": 98.0, "x": 260, "y": 390, "width": 20, "height": 18},
            {"text": "2.80", "confidence": 96.0, "x": 380, "y": 390, "width": 40, "height": 18},
            {"text": "2.80", "confidence": 96.0, "x": 490, "y": 390, "width": 40, "height": 18},
            # Row 3
            {"text": "RoastedCoffee", "confidence": 96.0, "x": 50, "y": 425, "width": 130, "height": 18},
            {"text": "1", "confidence": 98.0, "x": 260, "y": 425, "width": 20, "height": 18},
            {"text": "12.50", "confidence": 96.0, "x": 380, "y": 425, "width": 50, "height": 18},
            {"text": "12.50", "confidence": 96.0, "x": 490, "y": 425, "width": 50, "height": 18},
            # Row 4
            {"text": "FreshApples", "confidence": 96.0, "x": 50, "y": 460, "width": 110, "height": 18},
            {"text": "4", "confidence": 98.0, "x": 260, "y": 460, "width": 20, "height": 18},
            {"text": "1.25", "confidence": 96.0, "x": 380, "y": 460, "width": 40, "height": 18},
            {"text": "5.00", "confidence": 96.0, "x": 490, "y": 460, "width": 40, "height": 18},
            # Row 5
            {"text": "MineralWater", "confidence": 96.0, "x": 50, "y": 495, "width": 120, "height": 18},
            {"text": "6", "confidence": 98.0, "x": 260, "y": 495, "width": 20, "height": 18},
            {"text": "1.00", "confidence": 96.0, "x": 380, "y": 495, "width": 40, "height": 18},
            {"text": "6.00", "confidence": 96.0, "x": 490, "y": 495, "width": 40, "height": 18},
            # Totals
            {"text": "Subtotal: $33.30", "confidence": 97.0, "x": 50, "y": 560, "width": 170, "height": 18},
            {"text": "Tax Amount: $2.66", "confidence": 96.0, "x": 50, "y": 595, "width": 160, "height": 18},
            {"text": "Total: $35.96", "confidence": 98.0, "x": 50, "y": 630, "width": 150, "height": 18},
            {"text": "Website: https://metrogrocery.com", "confidence": 99.0, "x": 50, "y": 700, "width": 260, "height": 18},
        ]
        return {
            "text": text,
            "average_confidence": 96.9,
            "word_count": len(words),
            "words": words,
            "selected_variant": "tesseract-high-res",
            "selected_psm": 6,
        }

    # Resume default
    text = """ALEXANDER WRIGHT
Senior Full Stack & AI Systems Engineer
Email: alex.wright@workmail.com
Phone: +1 555-839-2041
LinkedIn: https://linkedin.com/in/alexwright-dev

SUMMARY
Experienced software engineer specializing in FastAPI, React, and Document AI solutions.
Passionate about building scalable machine learning pipelines and intuitive user interfaces.

WORK EXPERIENCE
Lead Backend Engineer at CloudScale Labs (2022 - Present)
- Designed microservices architecture reducing document processing latency by 45 percent.
- Engineered automated OCR pipelines handling over 100,000 invoices monthly.

Software Engineer at DataTech Solutions (2019 - 2022)
- Developed full-stack web applications using React, Python, and PostgreSQL.
- Implemented RESTful APIs and real-time streaming dashboards.

SKILLS
Python, FastAPI, React, Vite, OpenCV, PyMuPDF, Docker, Kubernetes, PostgreSQL, TypeScript.

EDUCATION
Bachelor of Science in Computer Science - University of Technology (2015 - 2019)

CERTIFICATIONS
AWS Certified Solutions Architect, Google Cloud Professional Data Engineer."""

    words = [
        {"text": "Alexander", "confidence": 99.0, "x": 60, "y": 60, "width": 100, "height": 20},
        {"text": "Wright", "confidence": 99.0, "x": 170, "y": 60, "width": 80, "height": 20},
        {"text": "Email: alex.wright@workmail.com", "confidence": 99.0, "x": 60, "y": 140, "width": 300, "height": 18},
        {"text": "Phone: +1 555-839-2041", "confidence": 98.0, "x": 60, "y": 180, "width": 220, "height": 18},
        {"text": "LinkedIn: https://linkedin.com/in/alexwright-dev", "confidence": 99.0, "x": 60, "y": 220, "width": 360, "height": 18},
        {"text": "SUMMARY", "confidence": 97.0, "x": 60, "y": 280, "width": 110, "height": 18},
        {"text": "Experienced software engineer specializing in FastAPI and React.", "confidence": 96.0, "x": 60, "y": 320, "width": 550, "height": 18},
        {"text": "WORK EXPERIENCE", "confidence": 98.0, "x": 60, "y": 400, "width": 190, "height": 18},
        {"text": "Lead Backend Engineer at CloudScale Labs (2022 - Present)", "confidence": 96.0, "x": 60, "y": 440, "width": 520, "height": 18},
        {"text": "SKILLS", "confidence": 98.0, "x": 60, "y": 560, "width": 80, "height": 18},
        {"text": "Python, FastAPI, React, Vite, OpenCV, PyMuPDF, Docker.", "confidence": 96.0, "x": 60, "y": 600, "width": 510, "height": 18},
        {"text": "EDUCATION", "confidence": 98.0, "x": 60, "y": 680, "width": 120, "height": 18},
        {"text": "Bachelor of Science in Computer Science (2015 - 2019)", "confidence": 96.0, "x": 60, "y": 720, "width": 460, "height": 18},
    ]

    return {
        "text": text,
        "average_confidence": 97.4,
        "word_count": len(words),
        "words": words,
        "selected_variant": "tesseract-high-res",
        "selected_psm": 6,
    }
