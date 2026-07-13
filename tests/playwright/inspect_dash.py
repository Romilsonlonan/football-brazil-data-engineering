from playwright.sync_api import sync_playwright

def inspect_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://localhost:8051")
        
        # Wait for the team selector trigger
        trigger = page.locator("#team-selector-trigger")
        trigger.wait_for(state="visible")
        
        # Click the trigger
        trigger.click()
        
        # Wait for the options container
        container = page.locator("#team-selector-options-container")
        container.wait_for(state="visible")
        
        # Get all buttons inside the container
        buttons = container.locator("button")
        count = buttons.count()
        print(f"Number of buttons found: {count}")
        
        for i in range(count):
            btn = buttons.nth(i)
            print(f"Button {i}: text='{btn.inner_text()}', id='{btn.get_attribute('id')}'")
            
        browser.close()

if __name__ == "__main__":
    inspect_page()
