import sys
import re
from playwright.sync_api import sync_playwright

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def extract_quanta_video(caseno):
    url = f"https://www.quantatw.com/Quanta/chinese/investment/meeting_open.aspx?CASENO={caseno}&link=1"
    print(f"Opening: {url}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=UA)
        page = context.new_page()
        
        captured_urls = []
        def on_response(response):
            # print(f"Response: {response.url}")
            if ".mp4" in response.url or ".m3u8" in response.url:
                captured_urls.append(response.url)
                print(f"Captured: {response.url}")
        
        page.on("response", on_response)
        
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            print("Page loaded, content:")
            print(page.content()[:2000])
            page.wait_for_timeout(10000)
            
            # Also check DOM for any video/source tags
            for attr in ["video", "source", "iframe", "embed"]:
                els = page.query_selector_all(attr)
                for el in els:
                    src = el.get_attribute("src")
                    if src:
                        print(f"DOM {attr} src: {src}")
                        captured_urls.append(src)
        except Exception as e:
            print(f"Error: {e}")
            
        browser.close()
    
    return captured_urls

if __name__ == "__main__":
    caseno = "NEWS003653"
    if len(sys.argv) > 1:
        caseno = sys.argv[1]
    urls = extract_quanta_video(caseno)
    print("\nSummary of captured URLs:")
    for u in urls:
        print(u)
