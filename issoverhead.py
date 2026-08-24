import requests
from datetime import datetime
import os
import smtplib
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

MY_LAT = 41.878113 # Your latitude
MY_LONG = -87.629799 # Your longitude

MY_EMAIL = os.environ.get("MY_EMAIL")
PASSWORD = os.environ.get("MY_PASSWORD")
PERSONAL = os.environ.get("REGULAR_EMAIL")

def get_session_with_retries():
    """Create a requests session with automatic retry logic"""
    session = requests.Session()
    retry_strategy = Retry(
        total=3,  # Maximum number of retries
        backoff_factor=1,  # Wait 1, 2, 4 seconds between retries
        status_forcelist=[429, 500, 502, 503, 504],  # Retry on these HTTP status codes
        allowed_methods=["GET"]  # Only retry on GET requests
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

try:
    session = get_session_with_retries()
    response = session.get(url="http://api.open-notify.org/iss-now.json", timeout=10)
    response.raise_for_status()
    data = response.json()
    
    iss_latitude = float(data["iss_position"]["latitude"])
    iss_longitude = float(data["iss_position"]["longitude"])
except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
    print(f"Error: Could not connect to ISS API after retries: {e}")
    exit(0)  # Exit gracefully without failing the workflow
except requests.exceptions.RequestException as e:
    print(f"Error: Failed to fetch ISS data: {e}")
    exit(0)

#Your position is within +5 or -5 degrees of the ISS position.
def iss_is_close():
    close_lat = MY_LAT - 5 <= iss_latitude <= MY_LAT + 5
    close_long = MY_LONG - 5 <= iss_longitude <= MY_LONG + 5
    return close_lat and close_long


parameters = {
    "lat": MY_LAT,
    "lng": MY_LONG,
    "formatted": 0,
}

try:
    session = get_session_with_retries()
    response = session.get("https://api.sunrise-sunset.org/json", params=parameters, timeout=10)
    response.raise_for_status()
    data = response.json()
    sunrise = int(data["results"]["sunrise"].split("T")[1].split(":")[0])
    sunset = int(data["results"]["sunset"].split("T")[1].split(":")[0])
except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
    print(f"Error: Could not connect to Sunrise-Sunset API after retries: {e}")
    exit(0)  # Exit gracefully without failing the workflow
except requests.exceptions.RequestException as e:
    print(f"Error: Failed to fetch sunrise-sunset data: {e}")
    exit(0)

time_now = datetime.now()

def is_dark():
    if time_now.hour >= sunset or time_now.hour <= sunrise:
        return True
    else:
        return False

#If the ISS is close to my current position
# and it is currently dark
# Then send me an email to tell me to look up.
# BONUS: run the code every 60 seconds.

if iss_is_close() and is_dark():
    try:
        with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
            connection.starttls()
            connection.login(user=MY_EMAIL, password=PASSWORD)
            connection.sendmail(from_addr=MY_EMAIL,
                                to_addrs=PERSONAL,
                                msg=f"Subject:ISS IS OVERHEAD\n\nISS is overhead! See if you can spot it!"
            )
        print("Email sent successfully!")
    except smtplib.SMTPException as e:
        print(f"Error: Failed to send email: {e}")
        exit(1)
else:
    print("ISS is not close or it's not dark yet.")
