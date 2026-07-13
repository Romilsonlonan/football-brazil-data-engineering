from playwright.sync_api import sync_playwright

def inspect_heights():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://localhost:8051")
        
        trigger = page.locator("#team-selector-trigger")
        trigger.wait_for(state="visible")
        trigger.click()
        
        container = page.locator("#team-selector-options-container")
        container.wait_for(state="visible")
        
        container_box = container.bounding_box()
        print(f"Container box: {container_box}")
        
        buttons = container.locator("button")
        count = buttons.count()
        print(f"Number of buttons found: {count}")
        
        for i in range(count):
            btn = buttons.nth(i)
            btn_box = btn.bounding_box()
            print(f"Button {i}: text='{btn.inner_text()}', box={btn_box}")
            
        # Check if the last button is within the container's visible area
        last_button = buttons.nth(count - 1)
        last_btn_box = last_button.bounding_box()
        
        if container_box:
            is_visible = (
                last_btn_box['y'] < (container_box['y'] + container_box['height']) and
                last_btn_box['y'] + last_btn_box['height'] > container_box['y']
            )
            print(f"Is last button visible in container? {is_visible}")
            
        browser.close()

if __name__ == "__main__":
    inspect_heights()
