from playwright.sync_api import sync_playwright

def run_cuj(page):
    page.goto("http://localhost:3200")
    page.wait_for_timeout(2000)

    page.evaluate("sessionStorage.setItem('token', 'mock_token')")

    def mock_hosts(route):
        route.fulfill(status=200, json=[])
    page.route("**/api/hosts", mock_hosts)
    page.route("**/api/hosts/", mock_hosts)

    def mock_settings(route):
        route.fulfill(status=200, json=[{"key": "notification_url", "value": ""}])
    page.route("**/api/settings", mock_settings)
    page.route("**/api/settings/", mock_settings)

    page.goto("http://localhost:3200/settings")
    page.wait_for_timeout(2000)

    save_btn = page.locator('button[type="submit"]')
    save_btn.wait_for(state="visible", timeout=10000)

    save_btn.focus()
    page.wait_for_timeout(500)

    def slow_save(route):
        import time
        time.sleep(2)
        route.fulfill(status=200, json={"status": "ok"})

    page.route("**/api/settings/notifications", slow_save)
    page.route("**/api/settings/notifications/", slow_save)

    save_btn.click()
    page.wait_for_timeout(500) # Wait just a bit to ensure it enters the loading state
    page.screenshot(path="/home/jules/verification/screenshots/saving.png")
    page.wait_for_timeout(2000)

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            record_video_dir="/home/jules/verification/videos"
        )
        page = context.new_page()
        try:
            run_cuj(page)
        finally:
            context.close()
            browser.close()
