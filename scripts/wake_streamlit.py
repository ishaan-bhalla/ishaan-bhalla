"""Open each Streamlit app in a headless browser so it doesn't go to sleep.

Streamlit Community Cloud puts apps to sleep after a period with no visitors,
and a plain HTTP ping doesn't count as a visit. This loads each app like a
browser would and, if it is already asleep, clicks the wake-up button.
Exits with an error if an app doesn't come up, so a failed run is visible.
"""
import sys
import time

from playwright.sync_api import sync_playwright

APPS = {
    "Image-to-Text": "https://ishaan-bhalla-neural-network-to-describe-simple-pict-app-u8tfxe.streamlit.app/",
    "Insaaf Insight": "https://insaaf-insight.streamlit.app/",
}
WAKE_BUTTON = "Yes, get this app back up!"


def app_is_up(page) -> bool:
    """The app is up once any frame shows a Streamlit app body with content."""
    for frame in page.frames:
        try:
            if frame.locator("[data-testid='stApp'], [data-testid='stAppViewContainer']").count():
                return True
        except Exception:
            continue
    return False


def wake(page, name: str, url: str) -> bool:
    page.goto(url, timeout=120_000)
    woke = False
    for _ in range(60):  # up to ~5 minutes
        button = page.get_by_role("button", name=WAKE_BUTTON)
        if button.count():
            button.first.click()
            woke = True
        if app_is_up(page):
            print(f"{name}: up{' (was asleep, woken)' if woke else ''}")
            return True
        time.sleep(5)
    print(f"{name}: did not come up within 5 minutes")
    return False


def main() -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        results = [wake(browser.new_page(), name, url) for name, url in APPS.items()]
        browser.close()
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
