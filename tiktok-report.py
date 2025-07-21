import requests
import json
import sys
import re
import time
import random
from datetime import datetime
BANNER = """
_______ _           _       _      _______    
 |__   __(_)Sel3a    | |9wiya| |    |__   __|   
    | |   _ _ __   __| | __ _| |_The   | |_ __  
    | |  | | '_ \ / _` |/ _` | | | | | | | '_ \ 
    | |  | | | | | (_| | (_| | | |_| |_| | | | |
    |_|  |_|_| |_|\__,_|\__,_|_|\__, (_)_|_| |_|
     Just For Fun!               __/ |          
                                |___/                                              
                    Tiktok Report Tool V1

     {}Note!: {}We don't Accept any responsibility for any illegal usage.{}
""".format('\033[91m', '\033[93m', '\033[0m')


# Updated configuration with mobile headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.tiktok.com/",
    "Origin": "https://www.tiktok.com",
}

REPORT_REASONS = {
    "1": "Illegal activities",
    "2": "Harassment or bullying",
    "3": "Hate speech",
    "4": "Violent extremism",
    "5": "Child safety",
    "6": "Impersonation",
    "7": "Spam",
    "8": "Other"
}

LOG_FILE = "tiktok_reports.log"
MAX_REPORTS = 20
DELAY_BETWEEN_REPORTS = 20  # Increased delay to avoid detection

def get_user_id(username):
    """Ultimate user ID extraction with 5 different methods"""
    methods = [
        lambda: get_user_id_mobile_api(username),
        lambda: get_user_id_web_scraping(username),
        lambda: get_user_id_alternative_api(username),
        lambda: get_user_id_ssr(username),
        lambda: get_user_id_fallback(username)
    ]
    
    for method in methods:
        user_id = method()
        if user_id:
            return user_id
    return None

def get_user_id_mobile_api(username):
    """Method 1: Mobile API"""
    try:
        url = f"https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/user/profile/?unique_id={username}"
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return response.json().get('user', {}).get('uid')
    except:
        return None

def get_user_id_web_scraping(username):
    """Method 2: Web scraping with multiple patterns"""
    try:
        url = f"https://www.tiktok.com/@{username}"
        response = requests.get(url, headers=HEADERS, timeout=10)
        patterns = [
            r'"userId":"(\d+)"',
            r'"uid":"(\d+)"',
            r'"authorId":"(\d+)"',
            r'uid=(\d+)',
            r'user\\/(\d+)\\/?',
            r'"id":"(\d+)"'
        ]
        for pattern in patterns:
            match = re.search(pattern, response.text)
            if match:
                return match.group(1)
    except:
        return None

def get_user_id_alternative_api(username):
    """Method 3: Alternative API endpoint"""
    try:
        url = f"https://m.tiktok.com/api/user/detail/?uniqueId={username}"
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return response.json().get('userInfo', {}).get('userId')
    except:
        return None

def get_user_id_ssr(username):
    """Method 4: Server-side rendered data"""
    try:
        url = f"https://www.tiktok.com/@{username}"
        response = requests.get(url, headers=HEADERS, timeout=10)
        start_marker = '"user_id":"'
        start = response.text.find(start_marker)
        if start != -1:
            start += len(start_marker)
            end = response.text.find('"', start)
            return response.text[start:end]
    except:
        return None

def get_user_id_fallback(username):
    """Method 5: Final fallback"""
    try:
        url = f"https://www.tiktok.com/node/share/user/@{username}"
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return response.json().get('userInfo', {}).get('userId')
    except:
        return None

def report_account(username, reason, details="", report_count=1):
    """Enhanced reporting function with multiple attempts"""
    user_id = get_user_id(username)
    if not user_id:
        print("\n❌ Critical Error: Failed to get user ID after multiple attempts")
        print("Possible solutions:")
        print("1. The account may not exist or be private")
        print("2. TikTok is blocking automated requests")
        print("3. Try again later or use a VPN")
        print("4. Manually verify the account exists at:")
        print(f"   https://www.tiktok.com/@{username}")
        return False

    print(f"\n✅ Success! Found user ID: {user_id}")
    print(f"🚀 Beginning mass reporting ({report_count} reports)")

    success_count = 0
    for i in range(1, report_count + 1):
        try:
            # Get fresh session for each report
            session = requests.Session()
            session.headers.update(HEADERS)
            session.get("https://www.tiktok.com/")  # Get fresh cookies
            
            payload = {
                "object_id": user_id,
                "owner_id": user_id,
                "report_type": "user",
                "reason": int(reason),
                "additional_info": details,
                "report_scene": "user_profile"
            }

            response = session.post(
                "https://www.tiktok.com/api/report/reasons_put/",
                json=payload,
                timeout=20
            )

            if response.status_code == 200:
                success_count += 1
                print(f"✅ Report {i}/{report_count} succeeded")
            else:
                print(f"⚠️ Report {i} failed (HTTP {response.status_code})")

            # Progressive delay with randomization
            delay = DELAY_BETWEEN_REPORTS + random.randint(0, 10) + (i * 2)
            if i < report_count:
                print(f"⏳ Waiting {delay} seconds (anti-detection)...")
                time.sleep(delay)

        except Exception as e:
            print(f"⚠️ Error during report {i}: {str(e)}")

    print(f"\n📊 Final results: {success_count}/{report_count} reports succeeded")
    return success_count > 0

def main():
    print(BANNER)
    if len(sys.argv) < 2:
        print("Usage: python tik-mass.py username [report_count]")
        print("Example: python tik-mass.py username 20")
        sys.exit(1)

    username = sys.argv[1].lstrip('@')
    report_count = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 1

    if report_count > MAX_REPORTS:
        print(f"⚠️ Maximum {MAX_REPORTS} reports allowed")
        report_count = MAX_REPORTS

    print(f"\nReport reasons for @{username}:")
    for num, reason in REPORT_REASONS.items():
        print(f"{num}. {reason}")

    reason = input("Select reason (1-8): ")
    while reason not in REPORT_REASONS:
        reason = input("Invalid choice. Select reason (1-8): ")

    details = input("Additional details (optional): ")

    print(f"\nStarting mass reporting for @{username}...")
    if report_account(username, reason, details, report_count):
        print("✅ Operation completed successfully")
    else:
        print("❌ Operation failed - see above for details")

if __name__ == "__main__":
    main()