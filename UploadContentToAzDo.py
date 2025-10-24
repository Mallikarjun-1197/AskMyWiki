from logger import get_logger
log = get_logger("UploadContentToAzDo")

import requests
import os
from dotenv import load_dotenv

load_dotenv()

organization = os.getenv("ORGANIZATION")
project = os.getenv("PROJECT")
wiki_id = os.getenv("WIKI_ID")
pat = os.getenv("PAT")


# 📄 Pages to upload
pages = {
    "/Expense-Policy": """
# Company Expense Reimbursement Policy

Employees may submit expenses for reimbursement related to travel, meals, and client entertainment.

## Guidelines
- Travel must be pre-approved by a manager
- Meal expenses capped at ₹2,000 per day
- Receipts must be uploaded within 7 days of the expense
- Use the Expense Portal to submit claims

## Exceptions
- Emergency travel may be reimbursed post-approval
- International travel requires VP-level approval
""",
    "/Leave-Policy": """
# Employee Leave Policy

The company offers various types of leave to support employee well-being.

## Types of Leave
- Casual Leave: 12 days/year
- Sick Leave: 10 days/year
- Earned Leave: 15 days/year
- Maternity/Paternity Leave: As per statutory guidelines

## Process
- Apply via HRMS portal
- Manager approval required
- Leave balance visible in dashboard
""",
    "/Performance-Review-Process": """
# Performance Review Process

Performance reviews are conducted twice a year to assess employee growth and contribution.

## Timeline
- Mid-Year Review: June
- Annual Review: December

## Evaluation Criteria
- Goal achievement
- Collaboration and communication
- Innovation and ownership

## Outcome
- Feedback shared via HRMS
- Ratings influence bonuses and promotions
""",
    "/IT-Support-Guide": """
# IT Support Guide

The IT Helpdesk assists with hardware, software, and access issues.

## Common Requests
- Laptop provisioning
- Password resets
- VPN setup
- Email access

## How to Raise a Ticket
- Visit the IT Helpdesk Portal
- Select issue category
- Provide detailed description
- Track status via ticket ID
""",
    "/Office-Facilities": """
# Office Facilities and Amenities

Our offices are equipped to support productivity and comfort.

## Amenities
- Cafeteria with subsidized meals
- Conference rooms with AV setup
- Wellness room and quiet zones
- Parking for employees and visitors

## Booking
- Use the Facilities Portal to reserve meeting rooms
- Access control via employee badge
"""
}

# 🔗 Base URL
base_url = f"https://dev.azure.com/{organization}/{project}/_apis/wiki/wikis/{wiki_id}/pages"

# 🧾 Headers and auth
headers = {"Content-Type": "application/json"}
auth = requests.auth.HTTPBasicAuth("", pat)

# 🚀 Upload each page
for path, content in pages.items():
    url = f"{base_url}?path={path}&api-version=7.0"
    payload = {"content": content}
    response = requests.put(url, headers=headers, auth=auth, json=payload)

    if response.status_code == 200:
        print(f"✅ Created: {path}")
    else:
        print(f"❌ Failed: {path}")
        print(f"Status Code: {response.status_code}")
        print("Reason:", response.reason)
        print("Response Text:", response.text)
