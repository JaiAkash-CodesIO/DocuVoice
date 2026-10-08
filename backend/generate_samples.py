from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

samples_dir = Path("samples")
samples_dir.mkdir(parents=True, exist_ok=True)

# Helper to draw clean receipt/invoice/resume
def create_sample_invoice():
    img = Image.new("RGB", (1200, 1500), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Use default bitmap font scaled or load default font
    font = ImageFont.load_default()

    lines = [
        "================================================================",
        "                       TAX INVOICE                              ",
        "================================================================",
        "",
        "Invoice Number: INV-2026-9042",
        "Invoice Date: 12-10-2026",
        "Due Date: 26-10-2026",
        "",
        "Vendor Details:",
        "Apex Cloud Technologies Inc.",
        "Email: billing@apexcloud.io",
        "Phone: +1 800-555-0199",
        "Website: https://apexcloud.io",
        "",
        "Bill To:",
        "Nexus Software Labs",
        "Contact: contact@nexuslabs.dev",
        "Phone: +1 800-555-9876",
        "",
        "----------------------------------------------------------------",
        "Item                    Qty         Unit Price        Total     ",
        "----------------------------------------------------------------",
        "Cloud Hosting Cluster     2             500.00      1000.00     ",
        "Managed Database Tier     1             350.00       350.00     ",
        "SSL Security Package      3              50.00       150.00     ",
        "Support Retainer          1             200.00       200.00     ",
        "----------------------------------------------------------------",
        "",
        "Subtotal: $1,700.00",
        "Tax Amount (10%): $170.00",
        "Total Amount Due: $1,870.00",
        "",
        "Payment Terms: Net 14 Days. Thank you for your business!",
        "================================================================",
    ]

    y = 60
    for line in lines:
        draw.text((60, y), line, fill=(0, 0, 0), font=font)
        y += 35

    # Scale up for high-res OCR readability
    img_large = img.resize((1600, 2000), Image.Resampling.NEAREST)
    img_large.save(samples_dir / "sample_invoice.png")
    print("Created sample_invoice.png")

def create_sample_receipt():
    img = Image.new("RGB", (900, 1300), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    lines = [
        "****************************************",
        "          METRO GROCERY STORE           ",
        "        104 Downtown Market Ave         ",
        "****************************************",
        "",
        "Receipt: REC-88412",
        "Date: 04-10-2026",
        "Cashier: Robert M.",
        "Payment Method: VISA Card Ending 4410",
        "",
        "----------------------------------------",
        "Item               Qty     Price   Total",
        "----------------------------------------",
        "Organic Milk         2      3.50    7.00",
        "Whole Wheat Bread    1      2.80    2.80",
        "Roasted Coffee       1     12.50   12.50",
        "Fresh Apples         4      1.25    5.00",
        "Mineral Water        6      1.00    6.00",
        "----------------------------------------",
        "",
        "Subtotal: $33.30",
        "Tax Amount: $2.66",
        "Total: $35.96",
        "",
        "Thank you for your purchase!",
        "Website: https://metrogrocery.com",
        "****************************************",
    ]

    y = 50
    for line in lines:
        draw.text((50, y), line, fill=(0, 0, 0), font=font)
        y += 35

    img_large = img.resize((1400, 1800), Image.Resampling.NEAREST)
    img_large.save(samples_dir / "sample_receipt.png")
    print("Created sample_receipt.png")

def create_sample_resume():
    img = Image.new("RGB", (1200, 1600), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    lines = [
        "ALEXANDER WRIGHT",
        "Senior Full Stack & AI Systems Engineer",
        "Email: alex.wright@workmail.com",
        "Phone: +1 555-839-2041",
        "LinkedIn: https://linkedin.com/in/alexwright-dev",
        "",
        "SUMMARY",
        "Experienced software engineer specializing in FastAPI, React, and Document AI solutions.",
        "Passionate about building scalable machine learning pipelines and intuitive user interfaces.",
        "",
        "WORK EXPERIENCE",
        "Lead Backend Engineer at CloudScale Labs (2022 - Present)",
        "- Designed microservices architecture reducing document processing latency by 45 percent.",
        "- Engineered automated OCR pipelines handling over 100,000 invoices monthly.",
        "",
        "Software Engineer at DataTech Solutions (2019 - 2022)",
        "- Developed full-stack web applications using React, Python, and PostgreSQL.",
        "- Implemented RESTful APIs and real-time streaming dashboards.",
        "",
        "SKILLS",
        "Python, FastAPI, React, Vite, OpenCV, PyMuPDF, Docker, Kubernetes, PostgreSQL, TypeScript.",
        "",
        "EDUCATION",
        "Bachelor of Science in Computer Science - University of Technology (2015 - 2019)",
        "",
        "CERTIFICATIONS",
        "AWS Certified Solutions Architect, Google Cloud Professional Data Engineer.",
    ]

    y = 60
    for line in lines:
        draw.text((60, y), line, fill=(0, 0, 0), font=font)
        y += 40

    img_large = img.resize((1600, 2100), Image.Resampling.NEAREST)
    img_large.save(samples_dir / "sample_resume.png")
    print("Created sample_resume.png")

if __name__ == "__main__":
    create_sample_invoice()
    create_sample_receipt()
    create_sample_resume()
