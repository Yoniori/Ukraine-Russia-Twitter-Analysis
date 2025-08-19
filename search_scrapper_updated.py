#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Twitter Tweet Scraping Engine
=============================

Advanced scraping module for extracting tweets using Selenium WebDriver.

Input: Twitter search URLs, hashtags, user queries
Output: Tweet objects with comprehensive metadata

Author: Jonathan Uri
Date: December 2024
"""

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, TimeoutException
from time import sleep
import random
import re

class Tweet:
    """
    Comprehensive tweet data structure containing all extractable tweet information.

    Attributes:
    - ID (str): Unique identifier for the tweet
    - author (str): Username of the tweet's author (without @)
    - fullName (str): Display name of the tweet's author
    - content (str): Text content of the tweet
    - timestamp (str): ISO formatted timestamp of the tweet
    - retweets (str): Number of retweets
    - likes (str): Number of likes
    - hashtag (str): Associated hashtag for search context
    - views (str): Number of views (if available)
    - comments (str): Number of comments/replies
    - bookmarks (str): Number of bookmarks
    - image_url (str): URL of attached image (if any)
    - video_url (str): URL of attached video (if any)
    - video_preview_image_url (str): URL of video preview/thumbnail
    - hashtags (list): List of all hashtags found in tweet content
    - url (str): Direct URL to the tweet
    """
    def __init__(self, ID, author, fullName, content, timestamp, retweets, likes, hashtag, views, comments, bookmarks, image_url, video_url=None, video_preview_image_url=None, hashtags=None, url=None):
        self.ID = ID
        self.author = author
        self.fullName = fullName
        self.content = content
        self.timestamp = timestamp
        self.retweets = retweets
        self.likes = likes
        self.hashtag = hashtag
        self.views = views
        self.comments = comments
        self.bookmarks = bookmarks
        self.image_url = image_url
        self.video_url = video_url
        self.video_preview_image_url = video_preview_image_url
        self.hashtags = hashtags if hashtags else []
        self.url = url

    def __hash__(self):
        """Make Tweet hashable for use in sets"""
        return hash(self.ID)

    def __eq__(self, other):
        """Compare tweets by ID"""
        return isinstance(other, Tweet) and self.ID == other.ID

    def __repr__(self):
        return f'Tweet(ID={self.ID}, author=@{self.author}, content="{self.content[:50]}...")'

class SearchScrapper:
    """
    Advanced Twitter search scraper with robust error handling and data extraction.

    Input: WebDriver instance
    Output: Sets of Tweet objects with complete metadata
    """
    def __init__(self, driver: webdriver.Chrome):
        """
        Initializes the SearchScrapper with a Selenium WebDriver instance.

        Parameters:
        - driver (webdriver.Chrome): Configured Selenium WebDriver instance
        """
        self.driver = driver

    def scrape_twitter_query(self, query_url: str, hashtag: str, max_tweets: int):
        """
        Scrapes tweets from Twitter search query with comprehensive error handling.

        Parameters:
        - query_url (str): Complete Twitter search URL with filters
        - hashtag (str): Associated hashtag/search term for context
        - max_tweets (int): Maximum number of tweets to scrape

        Returns:
        - set[Tweet]: Set of unique Tweet objects with extracted data
        
        Input: Twitter search URL (e.g., hashtag search, user search)
        Output: Set of Tweet objects with metadata (ID, content, author, engagement metrics)
        """
        print(f"🔍 Starting scrape for: {hashtag}")
        print(f"🌐 URL: {query_url}")
        
        self.driver.get(query_url)

        # Check for "No results" message
        no_results = False
        retries = 3
        for attempt in range(retries):
            try:
                no_results_element = self.driver.find_element(By.CSS_SELECTOR, "span.css-1jxf684")
                if "No results" in no_results_element.text:
                    print(f"❌ No results found for: {hashtag}")
                    no_results = True
                    break
            except (NoSuchElementException, StaleElementReferenceException):
                sleep(0.5)

        if no_results:
            return set()

        # Wait for tweets to load
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//article[@data-testid="tweet"]'))
            )
            print(f"✅ Tweets loaded successfully for: {hashtag}")
        except TimeoutException:
            print(f"⏱️  Timeout: No tweets found for: {hashtag}")
            return set()

        print("🔄 Scraping in progress...")
        hashtag_tweets = set()  # Store unique tweets
        processed_ids = set()   # Track processed tweet IDs
        prev_height = self.driver.execute_script('return document.body.scrollHeight')
        scroll_attempts = 0
        max_scroll_attempts = 10

        while len(hashtag_tweets) < max_tweets and scroll_attempts < max_scroll_attempts:
            try:
                loaded_tweets = self.driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
                print(f"📊 Found {len(loaded_tweets)} tweet elements on page")
                
                for tweet_element in loaded_tweets:
                    if len(hashtag_tweets) >= max_tweets:
                        break

                    try:
                        # Extract tweet data with comprehensive error handling
                        tweet_data = self._extract_tweet_data(tweet_element, hashtag, processed_ids)
                        
                        if tweet_data and tweet_data.ID not in processed_ids:
                            hashtag_tweets.add(tweet_data)
                            processed_ids.add(tweet_data.ID)
                            
                            if len(hashtag_tweets) % 10 == 0:
                                print(f"   📝 Scraped {len(hashtag_tweets)} tweets so far...")
                                
                    except Exception as e:
                        print(f"⚠️  Error processing individual tweet: {e}")
                        continue

                # Scroll to load more tweets
                self.driver.execute_script('window.scrollBy(0, 1000)')
                sleep(random.uniform(1, 3))
                curr_height = self.driver.execute_script('return document.body.scrollHeight')

                if curr_height == prev_height:
                    scroll_attempts += 1
                    print(f"🔄 No new content, attempt {scroll_attempts}/{max_scroll_attempts}")
                else:
                    scroll_attempts = 0
                    
                prev_height = curr_height

            except StaleElementReferenceException:
                print("⚠️  Stale element detected, retrying...")
                continue
            except Exception as e:
                print(f"❌ Unexpected error during scraping: {e}")
                break

        print(f"✅ Scraping completed for {hashtag}")
        print(f"📊 Total tweets collected: {len(hashtag_tweets)}")
        return hashtag_tweets

    def _extract_tweet_data(self, tweet_element, hashtag, processed_ids):
        """
        Extracts comprehensive data from a single tweet element.
        
        Parameters:
        - tweet_element: Selenium WebElement representing a tweet
        - hashtag: Context hashtag for the search
        - processed_ids: Set of already processed tweet IDs
        
        Returns:
        - Tweet: Tweet object with extracted data or None if extraction fails
        """
        try:
            # Extract tweet URL and ID first
            try:
                tweet_link_element = tweet_element.find_element(By.XPATH, './/a[contains(@href, "/status/")]')
                url = tweet_link_element.get_attribute('href')
                tweet_id = url.split('/')[-1] if url else None
            except NoSuchElementException:
                return None

            if not tweet_id or tweet_id in processed_ids:
                return None

            # Extract author username
            try:
                author = tweet_element.find_element(By.XPATH, './/span[contains(text(), "@")]').text.replace("@", "")
            except NoSuchElementException:
                author = "Unknown"

            # Extract tweet content
            try:
                content = tweet_element.find_element(By.XPATH, './/div[@data-testid="tweetText"]').text
            except NoSuchElementException:
                content = ""

            # Extract author's full name
            try:
                full_name = tweet_element.find_element(By.XPATH, './/div[@data-testid="User-Name"]//span').text
            except NoSuchElementException:
                full_name = ""

            # Extract timestamp
            try:
                timestamp_element = tweet_element.find_element(By.XPATH, './/time')
                timestamp = timestamp_element.get_attribute('datetime')
            except NoSuchElementException:
                timestamp = "No timestamp available"

            # Extract engagement metrics
            try:
                retweet_count = tweet_element.find_element(By.XPATH, './/button[@data-testid="retweet"]').text
            except NoSuchElementException:
                retweet_count = "0"

            try:
                like_count = tweet_element.find_element(By.XPATH, './/button[@data-testid="like"]').text
            except NoSuchElementException:
                like_count = "0"

            try:
                comments = tweet_element.find_element(By.XPATH, './/button[@data-testid="reply"]').text
            except NoSuchElementException:
                comments = "0"

            try:
                bookmarks = tweet_element.find_element(By.XPATH, './/button[@data-testid="bookmark"]').text
            except NoSuchElementException:
                bookmarks = "0"

            # Extract view count
            try:
                views = tweet_element.find_element(By.XPATH, "//*[@role='group']").text.split('\n')[-1]
            except NoSuchElementException:
                views = None

            # Extract media URLs
            image_url = self._extract_image_url(tweet_element)
            video_url, video_preview_url = self._extract_video_urls(tweet_element)

            # Extract hashtags from content
            hashtags = re.findall(r'#\w+', content) if content else []

            # Create and return Tweet object
            return Tweet(
                ID=tweet_id, author=author, fullName=full_name, content=content, 
                timestamp=timestamp, retweets=retweet_count, likes=like_count, 
                hashtag=hashtag, views=views, comments=comments, bookmarks=bookmarks, 
                image_url=image_url, video_url=video_url, 
                video_preview_image_url=video_preview_url, hashtags=hashtags, url=url
            )

        except Exception as e:
            print(f"⚠️  Error extracting tweet data: {e}")
            return None

    def _extract_image_url(self, tweet_element):
        """Extract image URL from tweet element"""
        try:
            tweet_photo_div = tweet_element.find_element(By.XPATH, './/div[@data-testid="tweetPhoto"]//img')
            return tweet_photo_div.get_attribute('src')
        except NoSuchElementException:
            return None

    def _extract_video_urls(self, tweet_element):
        """Extract video URL and preview image from tweet element"""
        try:
            video_elements = tweet_element.find_elements(By.XPATH, './/div[@data-testid="videoPlayer"]//video')
            if video_elements:
                video_url = video_elements[0].get_attribute('src')
                video_preview_url = video_elements[0].get_attribute('poster')
                return video_url, video_preview_url
        except NoSuchElementException:
            pass
        return None, None