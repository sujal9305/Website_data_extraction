import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time


# -----------------------------------
# 1. FETCH HTML (SMART HYBRID)
# -----------------------------------

def fetch_html_requests(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except:
        return None


def fetch_html_selenium(url):
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )

        driver.get(url)
        time.sleep(3)

        html = driver.page_source
        driver.quit()

        return html

    except Exception as e:
        print("Selenium Error:", e)
        return None


def fetch_html(url):
    html = fetch_html_requests(url)

    if not html or len(html) < 5000:
        print("Switching to Selenium...")
        html = fetch_html_selenium(url)

    return html


# -----------------------------------
# 2. EXTRACT DATA FROM ONE PAGE
# -----------------------------------

def extract_data(html):
    soup = BeautifulSoup(html, "html.parser")

    # remove unwanted tags
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        tag.decompose()

    title = soup.title.string.strip() if soup.title else ""

    headings = []
    for tag in soup.find_all(["h1", "h2"]):
        text = tag.get_text(strip=True)
        if text and len(text) > 5 and text not in headings:
            headings.append(text)

    main_section = soup.find("main") or soup.find("article") or soup.body
    paragraphs = main_section.find_all("p") if main_section else []

    content_list = []
    for p in paragraphs:
        text = p.get_text(strip=True)

        if len(text) > 50:
            content_list.append(text)

    content = " ".join(content_list)

    return {
        "title": title,
        "headings": headings,
        "content": content
    }


# -----------------------------------
# 3. GET ALL INTERNAL LINKS (DYNAMIC)
# -----------------------------------

def get_internal_links(base_url, soup):
    links = set()
    base_domain = urlparse(base_url).netloc

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"].strip()

        if not href or href.startswith("#"):
            continue

        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)

        # only internal links
        if parsed.netloc != base_domain:
            continue

        # skip junk pages
        if any(skip in full_url.lower() for skip in [
            "login", "signup", "cart", "privacy",
            "terms", "policy", "cookie", "account"
        ]):
            continue

        # skip file types
        if full_url.endswith((".jpg", ".png", ".pdf", ".svg", ".zip")):
            continue

        links.add(full_url)

    return list(links)


# -----------------------------------
# 4. PRIORITIZE IMPORTANT PAGES
# -----------------------------------

def prioritize_links(links):
    priority_keywords = [
        "about", "service", "solution", "product",
        "company", "team", "contact", "work", "case"
    ]

    def score(link):
        return sum(1 for k in priority_keywords if k in link.lower())

    return sorted(links, key=score, reverse=True)


# -----------------------------------
# 5. MULTI-PAGE EXTRACTION (SMART)
# -----------------------------------

def extract_multiple_pages(base_url):
    visited = set()
    all_content = []
    all_headings = []
    pages_data = []

    html = fetch_html(base_url)
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")

    # main page
    main_data = extract_data(html)
    title = main_data["title"]

    pages_data.append({
        "url": base_url,
        **main_data
    })

    all_content.append(main_data["content"])
    all_headings.extend(main_data["headings"])
    visited.add(base_url)

    # get links
    links = get_internal_links(base_url, soup)
    links = prioritize_links(links)

    print("Top links:", links[:5])

    # crawl top pages
    for link in links[:5]:  # limit pages
        if link in visited:
            continue

        try:
            sub_html = fetch_html(link)
            if not sub_html:
                continue

            sub_data = extract_data(sub_html)

            pages_data.append({
                "url": link,
                **sub_data
            })

            all_content.append(sub_data["content"])
            all_headings.extend(sub_data["headings"])
            visited.add(link)

        except Exception as e:
            print("Error:", link, e)

    # merge
    final_content = " ".join(all_content)
    final_headings = list(set(all_headings))

    return {
        "title": title,
        "headings": final_headings,
        "content": final_content,
        "pages": pages_data   # NEW (structured per page)
    }