import requests
from bs4 import BeautifulSoup

response = requests.get("https://steamcharts.com/app/367520") # Hollow Knight
soup = BeautifulSoup(response.text, 'html.parser')
player_count = soup.find('div', class_='app-stat').find('span').text

print(player_count)
