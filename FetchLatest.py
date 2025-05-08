import requests
from bs4 import BeautifulSoup


LOTTERY_CONFIG = {
    "Ultra Lotto 6/58": (1, 58), 
    "Grand Lotto 6/55": (1, 55), 
    "Superlotto 6/49": (1, 49), 
    "Megalotto 6/45": (1, 45), 
    "Lotto 6/42": (1, 42)
}

MONTH_MAP = {
    "01": "January", "02": "February", "03": "March", "04": "April",
    "05": "May", "06": "June", "07": "July", "08": "August",
    "09": "September", "10": "October", "11": "November", "12": "December"
}

LOTTERY_TYPE_MAP = {
    "All Games": "0",
    "Ultra Lotto 6/58": "18",
    "Grand Lotto 6/55": "17",
    "Super Lotto 6/49": "1",
    "Mega Lotto 6/45": "2",
    "Lotto 6/42": "13",
}

def fetch_latest_winning_numbers(lottery_type, from_date, to_date, fetch_limit):
    base_url = "https://www.pcso.gov.ph/SearchLottoResult.aspx"

    start_month, start_day, start_year = from_date.split('/')
    end_month, end_day, end_year = to_date.split('/')

    start_day = str(int(start_day))  
    start_year = str(int(start_year))  
    end_day = str(int(end_day))  
    end_year = str(int(end_year))  

    start_month_name = MONTH_MAP[start_month]
    end_month_name = MONTH_MAP[end_month]

    lottery_type_int = LOTTERY_TYPE_MAP.get(lottery_type, "0")

    session = requests.Session()
    response = session.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract hidden form fields
    viewstate = soup.find("input", {"name": "__VIEWSTATE"})["value"]
    eventvalidation = soup.find("input", {"name": "__EVENTVALIDATION"})["value"]
    viewstategenerator = soup.find("input", {"name": "__VIEWSTATEGENERATOR"})["value"]
    event_target = soup.find("input", {"name": "__EVENTTARGET"})
    event_argument = soup.find("input", {"name": "__EVENTARGUMENT"})

    # Define POST payload (data from the website)
    payload = {
        "__EVENTTARGET": event_target,
        "__EVENTARGUMENT": event_argument,
        "__VIEWSTATE": viewstate,
        "__VIEWSTATEGENERATOR": viewstategenerator,
        "__EVENTVALIDATION": eventvalidation,
        "ctl00$ctl00$cphContainer$cpContent$ddlStartMonth": start_month_name,
        "ctl00$ctl00$cphContainer$cpContent$ddlStartDate": start_day,
        "ctl00$ctl00$cphContainer$cpContent$ddlStartYear": start_year,
        "ctl00$ctl00$cphContainer$cpContent$ddlEndMonth": end_month_name,
        "ctl00$ctl00$cphContainer$cpContent$ddlEndDay": end_day,
        "ctl00$ctl00$cphContainer$cpContent$ddlEndYear": end_year,
        "ctl00$ctl00$cphContainer$cpContent$ddlSelectGame": lottery_type_int,
        "ctl00$ctl00$cphContainer$cpContent$btnSearch": "Search Lotto"
    }

    # Simulate a browser request (important for some sites)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    session.cookies.update(response.cookies)

    try:
        response = session.post(base_url, data=payload, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table")

        results = []
        if not table:
            return []

        for row in table.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) < 4:
                continue

            draw_date = cols[2].get_text(strip=True)
            game_type = cols[0].get_text(strip=True)
            if lottery_type in game_type:
                winning_numbers = [num.zfill(2) for num in cols[1].get_text(strip=True).split('-') if num.isdigit()]
                if winning_numbers:
                    results.append((draw_date, winning_numbers))

                if len(results) >= fetch_limit:
                    break

    except requests.RequestException as e:
        print(f"Error fetching results: {e}")
        return []

    return results
