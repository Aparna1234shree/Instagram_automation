import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


# Define the driver fixture
@pytest.fixture
def driver():
    # Initialize the Chrome WebDriver
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    driver.get("https://www.instagram.com/guviofficial/")
    yield driver
    # Quit the driver after the test
    driver.quit()


def close_popup(driver, xpath):
    """Helper function to close popups if they appear."""
    try:
        popup = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        popup.click()
    except TimeoutException:
        print("Popup did not appear.")


def test_fetch_instagram_data(driver):
    """Test to handle popups, then fetch posts and followers count."""

    # Close first popup if it appears
    popup_xpath = "/html[1]/body[1]/div[6]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]"
    close_popup(driver, popup_xpath)

    # Close the second popup if it appears
    close_button_xpath = "//span[contains(@aria-label,'Close')]"
    close_popup(driver, close_button_xpath)

    # Fetch the number of posts
    try:
        posts_xpath = "/html[1]/body[1]/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/section[1]/main[1]/div[1]/header[1]/section[1]/div[2]/ul[1]/li[1]/div[1]/button[1]/span[1]/span[1]"
        posts = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, posts_xpath))).text
        print("Raw number of posts:", posts)
        assert posts is not None, "Failed to fetch posts count."
    except TimeoutException:
        pytest.fail("Failed to fetch the number of posts due to timeout.")

    # Fetch the number of followers
    try:
        followers_xpath = "/html[1]/body[1]/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/section[1]/main[1]/div[1]/header[1]/section[1]/div[2]/ul[1]/li[2]/div[1]/button[1]/span[1]/span[1]"
        followers = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, followers_xpath))).text
        print("Raw number of followers:", followers)
        assert followers is not None, "Failed to fetch followers count."
    except TimeoutException:
        pytest.fail("Failed to fetch the number of followers due to timeout.")

    # Attempt to clean and convert values
    try:
        # Remove commas and check for "k" or "M" for thousands/millions
        def convert_to_number(value):
            value = value.replace(',', '')  # Remove commas
            if 'k' in value.lower():  # Check for both 'k' and 'K'
                return int(float(value.lower().replace('k', '')) * 1000)
            elif 'm' in value.lower():  # Check for both 'm' and 'M'
                return int(float(value.lower().replace('m', '')) * 1000000)
            return int(value)  # Convert directly if no 'k' or 'M' is found

        posts_count = convert_to_number(posts)
        followers_count = convert_to_number(followers)

        # Write data to a file
        with open("instagram_data.txt", "w") as file:
            file.write(f"Number of posts: {posts_count}\n")
            file.write(f"Number of followers: {followers_count}\n")

        print("Data written to instagram_data.txt")

    except ValueError:
        pytest.fail("Failed to convert posts or followers count to an integer.")
