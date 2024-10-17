import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    WebDriverException,
    TimeoutException,
    NoSuchElementException,
)
from bs4 import BeautifulSoup
import re
from datetime import datetime
from logging_config import setup_logging
from database_operations import (
    init_db,
    insert_profile_data,
    get_previous_week_data,
    generate_comparison_report,
    get_all_data_for_visualization,
)
from visualization import save_comparison_table

# Set up logging
logger = setup_logging()

CHROMEDRIVER_PATH = r"./chromedriver"
CHROME_EXECUTABLE_PATH = r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def setup_chrome_options():
    options = uc.ChromeOptions()
    options.binary_location = CHROME_EXECUTABLE_PATH
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    return options


def initialize_driver():
    logger.info("Launching Chrome...")
    try:
        return uc.Chrome(
            executable_path=CHROMEDRIVER_PATH, options=setup_chrome_options()
        )
    except Exception as e:
        logger.error(f"Failed to initialize Chrome driver: {e}")
        raise


def read_profile_urls(filename):
    try:
        with open(filename, "r") as file:
            return [line.strip() for line in file]
    except FileNotFoundError:
        logger.error(f"Profile URLs file not found: {filename}")
        raise


def scroll_and_count_interests(driver):
    def scroll_down(driver):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    previous_count = 0
    scroll_pause_time = 2
    max_attempts = 10

    for attempt in range(max_attempts):
        scroll_down(driver)
        time.sleep(scroll_pause_time)

        li_elements = driver.find_elements(
            By.CSS_SELECTOR,
            "li.pvs-list__paged-list-item.artdeco-list__item.pvs-list__item--line-separated.pvs-list__item--one-column",
        )
        current_count = len(li_elements)

        if current_count == previous_count:
            logger.info(f"No more new elements loaded after {attempt + 1} attempts.")
            break
        else:
            logger.info(f"Loaded {current_count} elements.")

        previous_count = current_count

    logger.info(f"Total number of <li> elements: {current_count}")
    return current_count


def process_profile(driver, profile_url):
    try:
        time.sleep(random.uniform(2, 5))
        driver.get(profile_url)
        wait = WebDriverWait(driver, 10)

        # Scroll to the bottom of the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(2, 5))

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        element = soup.find(string=re.compile(r"Show all \d+ skills"))

        number_of_skills = int(re.search(r"\d+", element).group()) if element else 0

        # Process interests count
        try:
            a_element = wait.until(
                EC.presence_of_element_located(
                    (By.ID, "navigation-index-see-all-companies")
                )
            )
            href_value = a_element.get_attribute("href")
            driver.get(href_value)

            interests_count = scroll_and_count_interests(driver)
            time.sleep(random.uniform(2, 5))
        except (TimeoutException, NoSuchElementException):
            logger.warning(f"Could not find interests for profile: {profile_url}")
            interests_count = 0

        status = "Success"
    except TimeoutException:
        logger.error(f"Timeout while processing profile: {profile_url}")
        interests_count, number_of_skills, status = 0, 0, "Error: Timeout"
    except NoSuchElementException:
        logger.error(f"Element not found while processing profile: {profile_url}")
        interests_count, number_of_skills, status = 0, 0, "Error: Element not found"
    except Exception as e:
        logger.error(f"Error processing profile {profile_url}: {str(e)}")
        interests_count, number_of_skills, status = 0, 0, f"Error: {str(e)}"

    return interests_count, number_of_skills, status


def run_scraper():
    logger.info("Starting LinkedIn scraper run")
    current_data = {}
    try:
        driver = initialize_driver()

        # Go to LinkedIn main page for manual login
        driver.get("https://www.linkedin.com/")
        logger.info("Opened LinkedIn main page.")

        # Wait for the "Sign in" button to be clickable and click it
        wait = WebDriverWait(driver, 10)
        sign_in_button = wait.until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    "a.nav__button-secondary[data-tracking-control-name='guest_homepage-basic_nav-header-signin']",
                )
            )
        )
        sign_in_button.click()

        logger.info("Clicked 'Sign in' button. Please log in manually.")
        input("Press Enter after you have logged in...")
        logger.info("Continuing with profile scraping...")

        profile_urls = read_profile_urls("linkedin_urls.txt")

        for profile_url in profile_urls[:10]:
            logger.info(f"Processing profile: {profile_url}")
            interests_count, number_of_skills, status = process_profile(
                driver, profile_url
            )

            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            insert_profile_data(
                current_datetime, profile_url, interests_count, number_of_skills, status
            )

            current_data[profile_url] = {
                "interests": interests_count,
                "skills": number_of_skills,
            }

            logger.info(f"Processed: {profile_url}")
            logger.info(f"Interests Count: {interests_count}")
            logger.info(f"Number of Skills: {number_of_skills}")
            logger.info(f"Status: {status}")
            logger.info("---")

            time.sleep(random.uniform(2, 5))

    except Exception as e:
        logger.error(f"An error occurred in the main function: {str(e)}")
    finally:
        if "driver" in locals():
            driver.quit()

    # Generate comparison report
    previous_data = get_previous_week_data()
    if previous_data:
        report = generate_comparison_report(current_data, previous_data)
        logger.info("Comparison Report:\n" + report)
    else:
        logger.info("No previous data available for comparison")

    logger.info("Finished LinkedIn scraper run")


def main():
    init_db()
    run_scraper()

    # Generate and save visualization
    df = get_all_data_for_visualization()
    save_comparison_table(df)


if __name__ == "__main__":
    main()

# IF there is no element for number of skills, then insert 0
# IF there is no element for interests, then insert 0
# Move processing skills to be first and then interests
