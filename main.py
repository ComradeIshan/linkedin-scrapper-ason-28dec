from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import time
import google.generativeai as genai
import os

import random

def human_sleep(a=2, b=5):
    time.sleep(random.uniform(a, b))

EMAIL = "aliayaan1719@gmail.com"
PASSWORD = "Red#label_187"
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--user-data-dir=C:/chrome-data")


driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get("https://www.linkedin.com/login")
human_sleep(5, 8)
driver.find_element(By.ID, "username").send_keys(EMAIL)
human_sleep(2, 4)
driver.find_element(By.ID, "password").send_keys(PASSWORD)
human_sleep(2, 4)
driver.find_element(By.XPATH, "//button[@type='submit']").click()
human_sleep(8, 12)

TARGET = "ishanshahi"

profile_url = f"https://www.linkedin.com/in/{TARGET}/"
driver.get(profile_url)
time.sleep(5)

soup = BeautifulSoup(driver.page_source, "html.parser")

def get_text(sel):
    try:
        return soup.select_one(sel).get_text(strip=True)
    except:
        return "NA"

name = get_text("h1")
headline = get_text("div.text-body-medium")
location = get_text("span.text-body-small.inline.t-black--light")
about = get_text("div.full-width.t-14.t-normal.t-black.display-flex.align-items-center")


followers = "NA"
connections = "NA"
stats = soup.find_all("span", class_="t-bold")
if len(stats) >= 2:
    connections = stats[0].text
    followers = stats[1].text

# --- Recent Post Count ---
driver.get(profile_url + "recent-activity/shares/")
time.sleep(5)
post_soup = BeautifulSoup(driver.page_source, "html.parser")
posts = post_soup.find_all("div", class_="feed-shared-update-v2")
post_count = len(posts)

print("\n------ LINKEDIN SUMMARY ------\n")
print("Name:", name)
print("Headline:", headline)
print("About:", about)
print("Location:", location)
print("Followers:", followers)
print("Connections:", connections)
print("Recent Posts:", post_count)

# --- PDF Export ---
styles = getSampleStyleSheet()
doc = SimpleDocTemplate("linkedin_summary.pdf")

story = []
story.append(Paragraph(f"<b>Name:</b> {name}", styles["BodyText"]))
story.append(Spacer(1, 6))
story.append(Paragraph(f"<b>Headline:</b> {headline}", styles["BodyText"]))
story.append(Spacer(1, 6))
story.append(Paragraph(f"<b>Location:</b> {location}", styles["BodyText"]))
story.append(Spacer(1, 6))
story.append(Paragraph(f"<b>Followers:</b> {followers}", styles["BodyText"]))
story.append(Spacer(1, 6))
story.append(Paragraph(f"<b>Connections:</b> {connections}", styles["BodyText"]))
story.append(Spacer(1, 6))
story.append(Paragraph(f"<b>Recent Posts:</b> {post_count}", styles["BodyText"]))

doc.build(story)

print("\nPDF Generated → linkedin_summary.pdf")

driver.quit()



genai.configure(api_key="AIzaSyC74ZWzgB9hN3XR9RRiZlwlrJLpcVfw5hI")

model = genai.GenerativeModel("gemini-1.5-flash")

prompt = f"""
You are a LinkedIn profile reviewer.

Review the following headline and about section and give:
1. 3 headline improvement suggestions
2. 3 about section improvement suggestions
3. One rewritten headline
4. One rewritten about section

Headline:
{name} - {headline}

About:
{about}
"""

response = model.generate_content(prompt)

print("\n------ GEMINI PROFILE REVIEW ------\n")
print(response.text)
