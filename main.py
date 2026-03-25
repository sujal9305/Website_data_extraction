import json
from app.scraper import extract_multiple_pages
from app.cleaner import clean_data
from app.processor import generate_summary


def run(url):
 
    raw_data = extract_multiple_pages(url)

    if not raw_data:
        print("Failed to fetch website data.")
        return None

    cleaned_data = clean_data(raw_data)

    ai_data = generate_summary(cleaned_data["content"])

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