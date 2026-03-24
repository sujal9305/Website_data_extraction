import json
from app.scraper import extract_multiple_pages
from app.cleaner import clean_data
from app.processor import generate_summary


def run(url):
    # STEP 1: Multi-page scraping
    raw_data = extract_multiple_pages(url)

    if not raw_data:
        print("Failed to fetch website data.")
        return None

    # STEP 2: Cleaning (EDA)
    cleaned_data = clean_data(raw_data)

    # STEP 3: AI Processing
    ai_data = generate_summary(cleaned_data["content"])

    # STEP 4: Final structured output
    result = {
        "title": cleaned_data["title"],
        "headings": cleaned_data["headings"],
        **ai_data
    }

    return result


if __name__ == "__main__":
    url = input("Enter website URL: ").strip()

    result = run(url)

    if result:
        print("\nFinal Output:\n")
        print(json.dumps(result, indent=2))
    else:
        print("No result generated.")