import sys
import os
import csv
import re
import asyncio
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSystemTrayIcon,
    QFrame,
    QSpacerItem,
    QSizePolicy
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
basedir = os.path.dirname(__file__)

try:
    from ctypes import windll  # Only exists on Windows.
    myappid = 'mycompany.myproduct.subproduct.version'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass
from playwright.async_api import async_playwright


class SmallBoxSelector(QWidget):
    def __init__(self, options, icons):
        super().__init__()
        layout = QHBoxLayout()
        self.buttons = []

        for option, icon_path in zip(options, icons):
            button = QPushButton(option)
            button.setIcon(QIcon(icon_path))
            button.setIconSize(QPixmap(icon_path).size())  # Adjust icon size as needed
            button.setCheckable(True)
            button.clicked.connect(self.on_button_clicked)
            layout.addWidget(button)
            self.buttons.append(button)

        self.setLayout(layout)
        self.selected_button = None

    def on_button_clicked(self):
        sender = self.sender()
        if sender.isChecked():
            if self.selected_button:
                self.selected_button.setStyleSheet("")  # Remove background color from previously selected button
            self.selected_button = sender
            self.selected_option = sender.text()
            sender.setStyleSheet("background-color: #FFCCCB;")  # Light red color for selected button
        else:
            self.selected_option = None


class SocialMediaScraperApp_WOUT(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Social Media Scraper")
        self.setGeometry(100, 100, 800, 600)  # Adjusted size for better layout

        # Set window icon
        self.setWindowIcon(QIcon('logo.png'))

        main_layout = QVBoxLayout()

        # Header layout for welcome message and logo
        header_layout = QVBoxLayout()

        # Welcome message
        self.welcome_label = QLabel("Welcome to social media AI companion")
        self.welcome_label.setAlignment(Qt.AlignCenter)
        self.welcome_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50;")
        header_layout.addWidget(self.welcome_label)

        # Logo
        self.logo_label = QLabel()
        pixmap = QPixmap('logo.png')
        self.logo_label.setPixmap(pixmap)
        self.logo_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(self.logo_label)

        main_layout.addLayout(header_layout)

        # Divider line
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(divider)

        # Platform selection
        platform_options = ["Twitter", "LinkedIn (Coming soon!)"]
        platform_icons = ["twitter_icon.png", "linkedin_icon.png"]
        self.platform_selector = SmallBoxSelector(platform_options, platform_icons)
        main_layout.addWidget(self.platform_selector)

        # Inputs
        inputs_layout = QVBoxLayout()

        self.total_run_time_input = QLineEdit()
        self.total_run_time_input.setPlaceholderText("Total run time (seconds)")
        inputs_layout.addWidget(self.total_run_time_input)

        self.scroll_interval_input = QLineEdit()
        self.scroll_interval_input.setPlaceholderText("Scroll interval (seconds)")
        inputs_layout.addWidget(self.scroll_interval_input)

        # URL input for Twitter
        self.twitter_url_input = QLineEdit()
        self.twitter_url_input.setPlaceholderText("Twitter URL (optional)")
        inputs_layout.addWidget(self.twitter_url_input)

        # Spacer item to push inputs to the bottom
        spacer_item = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        inputs_layout.addSpacerItem(spacer_item)

        main_layout.addLayout(inputs_layout)

        # Button
        self.start_button = QPushButton("Start Scraper")
        self.start_button.clicked.connect(self.start_scraper)
        main_layout.addWidget(self.start_button)

        # Status label
        self.status_label = QLabel()
        main_layout.addWidget(self.status_label)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #e0f7fa;
            }
            QLabel {
                font-size: 16px;
            }
            QLineEdit, QPushButton {
                font-size: 14px;
                padding: 8px;
                border-radius: 5px;
                border: 1px solid #ccc;
                margin: 5px 0;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                box-shadow: 3px 3px 5px #888888;
            }
            QPushButton:hover {
                background-color: #45a049;
                box-shadow: 5px 5px 7px #666666;
            }
            QPushButton:pressed {
                background-color: #3e8e41;
                box-shadow: inset 3px 3px 5px #444444;
            }
        """)

        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(QIcon('logo.png'), self)
        self.tray_icon.setToolTip("Social Media Scraper")
        self.tray_icon.activated.connect(self.tray_icon_clicked)
        self.tray_icon.show()

    def tray_icon_clicked(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.showNormal()
            self.activateWindow()

    async def extract_tweets(self, page):
        await page.wait_for_selector('article div[lang]')
        tweets = await page.query_selector_all('article div[lang]')
        tweet_texts = [await tweet.inner_text() for tweet in tweets]
        return tweet_texts

    async def save_tweets_to_csv(self, tweets):
        with open('tweets.txt', 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            for tweet in tweets:
                writer.writerow([tweet])

    async def scrape_linkedin(self):
        self.status_label.setText("Scraping LinkedIn posts...")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()

            await page.goto('https://www.linkedin.com')

            # Wait for the posts to load
            await page.wait_for_selector('.feed-shared-update-v2', timeout=60000)

            # Extract post content
            posts_data = []
            total_run_time = int(self.total_run_time_input.text())
            scroll_interval = int(self.scroll_interval_input.text())
            start_time = asyncio.get_event_loop().time()

            while asyncio.get_event_loop().time() - start_time < total_run_time:
                # Scroll the page
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await asyncio.sleep(scroll_interval)

                # Extract post content after scrolling
                post_elements = await page.query_selector_all('.feed-shared-update-v2')
                for post_element in post_elements:
                    post_content = await post_element.inner_html()
                    # Clean HTML content if needed
                    cleaned_content = re.sub('<[^<]+?>', '', post_content)
                    posts_data.append(cleaned_content)

            # Save data to a file
            # Example: Save data to a CSV file
            with open('linkedin_posts.txt', 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Post Content'])
                for post in posts_data:
                    writer.writerow([post])

            await browser.close()

        self.status_label.setText("LinkedIn posts scraped successfully!")

    async def main(self):
        total_run_time = int(self.total_run_time_input.text())
        scroll_interval = int(self.scroll_interval_input.text())

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()

            # Check if LinkedIn is selected
            selected_platform = self.platform_selector.selected_option
            if selected_platform == "LinkedIn (Coming soon!)":
                await self.scrape_linkedin()
            else:
                twitter_url = self.twitter_url_input.text().strip()
                await self.scrape_twitter(page, total_run_time, scroll_interval, twitter_url)

            await browser.close()

    async def scrape_twitter(self, page, total_run_time, scroll_interval, twitter_url='https://twitter.com/'):
        if not twitter_url:
            twitter_url = 'https://twitter.com'
        await page.goto(twitter_url, timeout=60000)
        saved_tweets = await self.extract_tweets(page)
        start_time = asyncio.get_event_loop().time()

        async def check_for_new_tweets():
            nonlocal saved_tweets
            while asyncio.get_event_loop().time() - start_time < total_run_time:
                await asyncio.sleep(scroll_interval)
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                new_tweets = await self.extract_tweets(page)
                if new_tweets[0] != saved_tweets[0]:
                    self.status_label.setText("First tweet has changed. Saving tweets to CSV...")
                    await self.save_tweets_to_csv(saved_tweets)
                    saved_tweets = new_tweets

        asyncio.create_task(check_for_new_tweets())
        await asyncio.sleep(total_run_time)

    def start_scraper(self):
        selected_platform = self.platform_selector.selected_option
        if selected_platform == "LinkedIn (Coming soon!)":
            asyncio.run(self.scrape_linkedin())
        else:
            asyncio.run(self.main())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SocialMediaScraperApp()
    window.show()
    sys.exit(app.exec_())
