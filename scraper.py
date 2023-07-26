import jsonlines
import random
from playwright.sync_api import sync_playwright
from playwright._impl._api_types import TimeoutError
from bs4 import BeautifulSoup

class Scraper:
    """
    A class used to scrape web pages.
    
    ...

    Attributes
    ----------
    input_url : str
        The URL of the web page to scrape.
    output_file : str
        The path of the file where the scraped data will be saved.
    proxy_url : str, optional
        The URL of the proxy server to use when scraping (default is None).
    server : str
        The proxy server's domain or IP address.
    port : str
        The proxy server's port.
    username : str
        The username to authenticate with the proxy server.
    password : str
        The password to authenticate with the proxy server.
    browser : Browser
        The Playwright browser object.
    page : Page
        The Playwright page object.

    Methods
    -------
    start():
        Starts the Playwright context.
    stop(p: Playwright):
        Stops the Playwright context and closes the browser.
    process_proxy():
        Splits the proxy_url into server, port, username, and password.
    process_page():
        Extracts the data from the page and writes it to the output file.
    wait_for_quotes(timeout=100000):
        Waits for the quotes to load on the page.
    scrape():
        The main method that handles the page navigation and data extraction.
    """
    
    def __init__(self, input_url, output_file, proxy_url=None):
        self.input_url = input_url
        self.output_file = output_file
        self.proxy_url = proxy_url
        self.server = None
        self.port = None
        self.username = None
        self.password = None
        self.browser = None
        self.context = None
        self.page = None
        self.USER_AGENTS = [
                            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
                            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
                            'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
        ]

    def start_playwright(self):
        """Starts the Playwright context and initializes the browser."""
        self.playwright = sync_playwright().__enter__()
        
        browser_args = {
            #"headless": False, 
            "proxy": {
                "server": f"{self.server}:{self.port}",
                "username": self.username,
                "password": self.password
            }
        } if self.proxy_url else {}

        self.browser = self.playwright.chromium.launch(**browser_args)
        self.context = self.browser.new_context(user_agent=random.choice(self.USER_AGENTS))
        self.page = self.context.new_page()
        self.handle_captcha()
        self.handle_cookies()

    def stop_playwright(self):
        """Stops the Playwright context and closes the browser."""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def process_proxy(self):
        """Splits the proxy_url into server, port, username, and password."""
        username_password, server_port = self.proxy_url.split('@')
        self.username, self.password = username_password.split(':')
        self.server, self.port = server_port.split(':')

    def process_page(self):
        """
        Extracts the data from the page and writes it to the output file.
        The data includes the quote, its author, and its associated tags.
        """
        page_content = self.page.content()
        soup = BeautifulSoup(page_content, 'html.parser')

        quotes = soup.find_all('div', class_='quote')

        with jsonlines.open(self.output_file, mode='a') as writer:
            for quote in quotes:
                text = quote.find('span', class_='text').text[1:-1]
                author = quote.find('small', class_='author').text
                tags = [tag.text for tag in quote.find('div', class_='tags').find_all('a', class_='tag')]
                writer.write({"text": text, "by": author, "tags": tags})

    def wait_for_quotes(self, timeout=100000):
        """
        Waits for the quotes to load on the page.
        
        Parameters
        ----------
        timeout : int, optional
            The maximum time to wait in milliseconds (default is 100000).
        """
        self.page.wait_for_selector('div.quote', timeout=timeout)
    
    def handle_captcha(self):
        """Handle captcha if present."""
        pass

    def handle_cookies(self):
        """Handle cookies if necessary."""
        pass 

    def scrape(self):
        """
        The main method that handles the page navigation and data extraction.
        It navigates to the input_url, waits for the quotes to load, processes the page, 
        and tries to find the 'next' button to navigate to the next page.
        If there is no 'next' button, it stops the scraping process.
        """
        if self.proxy_url:
            self.process_proxy()  # Process the proxy URL into its components

        self.start_playwright()

        while True:
            # Navigate to the page
            self.page.goto(self.input_url)
            print('Scraping: ', self.input_url)

            # Wait for the quotes to load
            self.wait_for_quotes()

            # Process the page
            self.process_page()

            # Try to find the 'next' button and click it
            try:
                next_button = self.page.wait_for_selector('li.next a', timeout=1000)
            except TimeoutError:
                # If there is no 'next' button, we're probably on the last page
                break
            else:
                next_button.click()
                self.input_url = self.page.url

        self.stop_playwright()
