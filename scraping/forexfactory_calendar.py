import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd

def forexfactory_calendar(month):
    # Create a cloudscraper instance
    scraper = cloudscraper.create_scraper()  # returns a requests.Session object

    # Load the page
    url = f'https://www.forexfactory.com/calendar?month={month}'
    response = scraper.get(url)

    if response.status_code != 200:
        print(f"Error: Could not retrieve data for month {month}, status code: {response.status_code}")
        return []

    # Use BeautifulSoup to parse the page source
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', {'class': 'calendar__table'})

    # DEBUG: Print the response content if the table is not found
    if not table:
        print(f"Could not find the calendar table for month {month}.")
        return []

    # Extract the data from the table
    data = []
    current_date = None

    for row in table.find_all('tr', recursive=False):
        # Check if the row represents a date change
        date_cell = row.find('td', {'class': 'calendar__date'})
        if date_cell and date_cell.text.strip():
            current_date = date_cell.text.strip()

        # Skip rows that don't contain event information
        if not row.has_attr('data-event-id'):
            continue

        # Process each event row
        time_cell = row.find('td', {'class': 'calendar__time'})
        currency_cell = row.find('td', {'class': 'calendar__currency'})
        event_cell = row.find('td', {'class': 'calendar__event'})
        actual_cell = row.find('td', {'class': 'calendar__actual'})
        forecast_cell = row.find('td', {'class': 'calendar__forecast'})
        previous_cell = row.find('td', {'class': 'calendar__previous'})

        # Extract the event title from the nested span tag
        event_title = event_cell.find('span', {'class': 'calendar__event-title'}).text.strip() if event_cell else ''

        data.append({
            'Date': current_date,
            'Time': time_cell.text.strip() if time_cell else '',
            'Currency': currency_cell.text.strip() if currency_cell else '',
            'Event': event_title,
            'Actual': actual_cell.text.strip() if actual_cell else '',
            'Forecast': forecast_cell.text.strip() if forecast_cell else '',
            'Previous': previous_cell.text.strip() if previous_cell else ''
        })

    return data

def get_monthly_data(month):
    print(f"Fetching data for: {month}")
    month_data = forexfactory_calendar(month)

    # Convert the data into a DataFrame
    df = pd.DataFrame(month_data)
    return df

