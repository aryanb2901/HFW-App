import requests
from bs4 import BeautifulSoup

link = "https://fbref.com/en/matches/a071faa8/Liverpool-Bournemouth-August-15-2025-Premier-League"

headers_list = [
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0 Safari/537.36"},
    {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Firefox/120.0"},
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0"},
]

for i, headers in enumerate(headers_list, 1):
    print(f"\n--- Attempt {i} ---")
    try:
        r = requests.get(link, headers=headers, timeout=15)
        print("Status:", r.status_code)
        if r.status_code != 200:
            print("⚠️ Non-200 response. First 300 chars of body:")
            print(r.text[:300])
            continue

        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.title.string if soup.title else "(no title)"
        print("✅ Page title:", title)
        print("Contains 'table' tags:", len(soup.find_all('table')))
        print("Contains HTML comments:", len(soup.find_all(string=lambda x: isinstance(x, type(soup.comment)))))

    except Exception as e:
        print("❌ Error:", e)
