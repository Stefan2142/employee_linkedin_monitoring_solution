# LinkedIn Profile Scraper

This project is a LinkedIn profile scraper that collects information about interests and skills from LinkedIn profiles. It uses Selenium with undetected_chromedriver for web scraping, stores data in a SQLite database, and provides visualization of the collected data.

## Features

- Scrapes LinkedIn profiles for interests and skills counts
- Stores data in a SQLite database
- Compares current data with previous scrapes
- Generates a visual comparison report
- Handles manual login to avoid LinkedIn's anti-automation measures

## Prerequisites

- Python 3.7+
- Chrome browser
- ChromeDriver (compatible with your Chrome version)

## Installation

1. Clone this repository:

   ```
   git clone https://github.com/stefan2142/linkedin-profile-scraper.git
   cd linkedin-profile-scraper
   ```

2. Install the required packages:

   ```
   pip install -r requirements.txt
   ```

3. Ensure you have the correct ChromeDriver version installed and its path is set correctly in the `CHROMEDRIVER_PATH` variable in `linkedin_login_uc_version.py`.

## Usage

1. Create a file named `linkedin_profiles.txt` in the project directory and add the LinkedIn profile URLs you want to scrape, one per line.

2. Run the scraper:

   ```
   python linkedin_login_uc_version.py
   ```

3. When prompted, manually log in to your LinkedIn account.

4. The scraper will process each profile and store the data in the SQLite database.

5. After scraping, a comparison report will be generated and saved as an HTML file.

## Files Description

- `linkedin_login_uc_version.py`: Main script for the LinkedIn scraper
- `database_operations.py`: Functions for database operations
- `visualization.py`: Functions for creating visual reports
- `logging_config.py`: Logging configuration (not included in the repository)

## Notes

- This scraper is for educational purposes only. Be sure to comply with LinkedIn's terms of service and robots.txt when using this tool.
- The scraper includes delays between requests to avoid overloading LinkedIn's servers. Adjust these as needed.
- Always use this tool responsibly and ethically.

## Contributing

Contributions, issues, and feature requests are welcome. Feel free to check [issues page](https://github.com/stefan2142/linkedin-profile-scraper/issues) if you want to contribute.

## License

[MIT](https://choosealicense.com/licenses/mit/)
