import time
import random
import webbrowser
while True:
    sites = random.choice(['google.com', 'youtube.com', 'gmail.com'])
    visit = 'https://{}'.format(sites)
    webbrowser.open(visit) 
    time.sleep(5)
