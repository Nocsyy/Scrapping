import os
import re
import time
import requests
import csv
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

API_KEY = os.getenv('API_KEY')
CSE_ID = os.getenv('CSE_ID')

MAX_WORKERS = 10
RETRY_ATTEMPTS = 3
TIMEOUT = 20

def get_selenium_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    service = Service('/path/to/chromedriver')  # Remplacez par le chemin vers votre chromedriver
    return webdriver.Chrome(service=service, options=chrome_options)

def google_search(query, api_key, cse_id, num=10):
    service = build("customsearch", "v1", developerKey=api_key)
    results = []
    start_index = 1
    max_results = 1000

    while start_index <= num and start_index <= max_results:
        try:
            res = service.cse().list(q=query, cx=cse_id, start=start_index).execute()
            results.extend(res.get('items', []))
            start_index += 10
            time.sleep(1)

            if 'nextPage' not in res.get('queries', {}):
                break
        except HttpError as e:
            print(f"HTTP error: {e.resp.status} - {e._get_reason()}")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            break

    return results

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def fetch_url_with_retries(url, retries=RETRY_ATTEMPTS):
    if not is_valid_url(url):
        print(f"URL invalide : {url}")
        return None
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    attempt = 0
    while attempt < retries:
        try:
            response = requests.get(url, headers=headers, timeout=TIMEOUT)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt+1} failed for {url}: {e}")
            attempt += 1
            time.sleep(2)
    return None

def extract_emails_from_page(url, visited_pages, max_pages_per_site):
    all_emails = set()
    total_pages_scraped = 0
    total_sites_scraped = 0

    if len(visited_pages) >= max_pages_per_site:
        return all_emails, total_pages_scraped, total_sites_scraped

    page_content = fetch_url_with_retries(url)
    if page_content is None:
        return all_emails, total_pages_scraped, total_sites_scraped

    soup = BeautifulSoup(page_content, 'html.parser')

    # Recherche d'emails dans le texte de la page
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = set(re.findall(email_pattern, soup.get_text()))

    # Recherche d'emails dans les attributs href
    emails.update({link['href'].split('mailto:')[1] for link in soup.find_all('a', href=True) if 'mailto:' in link['href']})

    if emails:
        all_emails.update(emails)

    total_pages_scraped += 1
    visited_pages.add(url)

    for link in soup.find_all('a', href=True):
        next_url = urljoin(url, link['href'])
        if next_url not in visited_pages and urlparse(next_url).netloc == urlparse(url).netloc:
            sub_emails, sub_pages, sub_sites = extract_emails_from_page(next_url, visited_pages, max_pages_per_site)
            all_emails.update(sub_emails)
            total_pages_scraped += sub_pages
            total_sites_scraped += sub_sites

    total_sites_scraped += 1
    return all_emails, total_pages_scraped, total_sites_scraped

def extract_emails_with_selenium(url):
    driver = get_selenium_driver()
    driver.get(url)
    time.sleep(5)  # Attendez que la page se charge
    page_content = driver.page_source
    driver.quit()
    soup = BeautifulSoup(page_content, 'html.parser')

    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = set(re.findall(email_pattern, soup.get_text()))
    emails.update({link['href'].split('mailto:')[1] for link in soup.find_all('a', href=True) if 'mailto:' in link['href']})

    return emails

def fetch_emails_from_urls(urls, max_sites, max_pages_per_site):
    all_emails = {}
    total_pages_scraped = 0
    total_sites_scraped = 0

    def process_url(url):
        nonlocal total_pages_scraped, total_sites_scraped
        visited_pages = set()
        site_emails, pages_scraped, sites_scraped = extract_emails_from_page(url, visited_pages, max_pages_per_site)
        if site_emails:
            all_emails.update({email: url for email in site_emails})
        total_pages_scraped += pages_scraped
        total_sites_scraped += sites_scraped

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []
        for url in urls:
            if total_sites_scraped >= max_sites:
                break
            futures.append(executor.submit(process_url, url))
        for future in futures:
            future.result()

    return all_emails, total_pages_scraped, total_sites_scraped

def save_to_csv(filename, data):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Email', 'Site'])
        for email, site in data.items():
            writer.writerow([email, site])