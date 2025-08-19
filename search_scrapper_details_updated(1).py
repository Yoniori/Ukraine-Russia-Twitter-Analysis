#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Twitter User Network Scraper
============================

Specialized module for scraping user networks (followers/following/verified followers) on Twitter.

Input: Twitter user profile URLs (following/followers pages)
Output: UserDetail objects with username information

Author: Jonathan Uri
Date: December 2024
"""

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, TimeoutException
from time import sleep
import random

class UserDetail:
    """
    Represents a Twitter user's basic profile information.

    Attributes:
    - author (str): Username of the user (without @ symbol)
    
    Input: Raw username data from Twitter elements
    Output: Clean, standardized username string
    """
    def __init__(self, author):
        """
        Initialize UserDetail with username.
        
        Parameters:
        - author (str): Username of the Twitter user
        """
        self.author = author.replace('@', '') if author else ""

    def __repr__(self):
        return f'UserDetail(@{self.author})'

    def __eq__(self, other):
        """Compare users by username for deduplication"""
        return isinstance(other, UserDetail) and self.author == other.author

    def __hash__(self):
        """Make UserDetail hashable for use in sets"""
        return hash(self.author)

class SearchScrapperDetails:
    """
    Advanced scraper for Twitter user network data (followers/following lists).

    Capabilities:
    - Scrape user following lists
    - Scrape user followers lists  
    - Scrape verified followers
    - Handle pagination and dynamic loading
    - Robust error handling
    
    Input: WebDriver instance and Twitter network URLs
    Output: Sets of UserDetail objects
    """
    def __init__(self, driver: webdriver.Chrome):
        """
        Initialize the network scraper with a configured WebDriver.

        Parameters:
        - driver (webdriver.Chrome): Selenium WebDriver instance
        """
        self.driver = driver

    def scrape_following_page(self, query_url: str, max_users: int):
        """
        Scrapes user details from Twitter followers/following/verified followers pages.

        Parameters:
        - query_url (str): URL of the network page to scrape
            Examples:
            - https://x.com/username/following
            - https://x.com/username/followers
            - https://x.com/username/verified_followers
        - max_users (int): Maximum number of users to scrape

        Returns:
        - set[UserDetail]: Set of UserDetail objects with scraped user data
        
        Input: Twitter network page URL (following/followers)
        Output: Set of UserDetail objects with usernames
        """
        print(f"🌐 Accessing network page: {query_url}")
        self.driver.get(query_url)
        
        # Determine page type for logging
        page_type = "unknown"
        if "/following" in query_url:
            page_type = "following"
        elif "/verified_followers" in query_url:
            page_type = "verified followers"
        elif "/followers" in query_url:
            page_type = "followers"
            
        print(f"📊 Scraping {page_type} list...")
        
        retries = 3
        user_details = set()
        processed_elements = set()

        # Check if the page shows empty state
        for attempt in range(retries):
            try:
                empty_state_element = self.driver.find_element(By.XPATH, '//div[@data-testid="emptyState"]')
                print(f"❌ No {page_type} found on this page")
                return set()
            except (NoSuchElementException, StaleElementReferenceException):
                sleep(0.5)

        # Wait for user list to load
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//button[@data-testid="UserCell"]'))
            )
            print(f"✅ {page_type.capitalize()} list loaded successfully")
        except TimeoutException:
            print(f"⏱️  Timeout: No {page_type} found after waiting")
            return set()

        print("🔄 Scraping users...")
        prev_height = self.driver.execute_script('return document.body.scrollHeight')
        no_new_content_attempts = 0
        max_no_content_attempts = 20

        while len(user_details) < max_users and no_new_content_attempts < max_no_content_attempts:
            try:
                # Find all user elements on current page
                loaded_users = self.driver.find_elements(By.XPATH, '//button[@data-testid="UserCell"]')
                
                if len(loaded_users) > 0 and len(user_details) % 50 == 0:
                    print(f"   📊 Found {len(loaded_users)} user elements, extracted {len(user_details)} unique users")

                for user_element in loaded_users:
                    if len(user_details) >= max_users:
                        break
                        
                    # Use element ID to avoid processing same element twice
                    element_id = user_element.id
                    if element_id in processed_elements:
                        continue

                    try:
                        # Extract username from user element
                        username_element = user_element.find_element(By.XPATH, './/span[contains(text(), "@")]')
                        username = username_element.text.replace("@", "")
                        
                        if username:  # Only add non-empty usernames
                            user_details.add(UserDetail(author=username))
                            processed_elements.add(element_id)
                            
                    except NoSuchElementException:
                        # Some user elements might not have visible usernames
                        continue
                    except Exception as e:
                        print(f"⚠️  Error extracting user data: {e}")
                        continue

                # Check if we've reached the target
                if len(user_details) >= max_users:
                    print(f"🎯 Reached target of {max_users} users")
                    break

                # Scroll to load more users
                scroll_distance = random.uniform(700, 1000)
                self.driver.execute_script(f'window.scrollBy(0, {scroll_distance})')
                sleep(random.uniform(1, 3))

                # Check if new content loaded
                curr_height = self.driver.execute_script('return document.body.scrollHeight')
                if curr_height == prev_height:
                    no_new_content_attempts += 1
                    if no_new_content_attempts % 5 == 0:
                        print(f"   ⏳ No new content for {no_new_content_attempts} attempts...")
                else:
                    no_new_content_attempts = 0

                prev_height = curr_height

            except StaleElementReferenceException:
                print("⚠️  Stale element detected, retrying...")
                continue
            except Exception as e:
                print(f"❌ Unexpected error during user scraping: {e}")
                break

        print(f"✅ User network scraping completed")
        print(f"📊 Total unique {page_type} collected: {len(user_details)}")
        
        if len(user_details) == 0:
            print(f"⚠️  Warning: No users were extracted from {page_type} page")
        
        return user_details

    def scrape_multiple_network_types(self, username: str, max_users_per_type: int = 100):
        """
        Scrapes all network types for a given user (following, followers, verified followers).
        
        Parameters:
        - username (str): Target username to scrape networks for
        - max_users_per_type (int): Maximum users to scrape per network type
        
        Returns:
        - dict: Dictionary with network types as keys and UserDetail sets as values
        
        Input: Username string
        Output: Dictionary with following/followers/verified_followers data
        """
        print(f"🎯 Starting comprehensive network scrape for @{username}")
        
        network_types = {
            'following': f'https://x.com/{username}/following',
            'followers': f'https://x.com/{username}/followers', 
            'verified_followers': f'https://x.com/{username}/verified_followers'
        }
        
        results = {}
        
        for network_type, url in network_types.items():
            print(f"\n🔄 Scraping {network_type} for @{username}")
            try:
                users = self.scrape_following_page(url, max_users_per_type)
                results[network_type] = users
                print(f"✅ {network_type}: {len(users)} users collected")
                
                # Brief pause between network types
                sleep(random.uniform(2, 4))
                
            except Exception as e:
                print(f"❌ Error scraping {network_type} for @{username}: {e}")
                results[network_type] = set()
        
        total_unique_users = len(set().union(*results.values()))
        print(f"\n🎉 Network scraping completed for @{username}")
        print(f"📊 Total unique users across all networks: {total_unique_users}")
        
        return results

    def get_network_statistics(self, network_data: dict):
        """
        Generates statistics from scraped network data.
        
        Parameters:
        - network_data (dict): Results from scrape_multiple_network_types
        
        Returns:
        - dict: Statistics about the network data
        """
        stats = {}
        
        for network_type, users in network_data.items():
            stats[network_type] = {
                'count': len(users),
                'usernames': [user.author for user in users]
            }
        
        # Calculate overlaps
        if 'following' in network_data and 'followers' in network_data:
            following_users = {user.author for user in network_data['following']}
            followers_users = {user.author for user in network_data['followers']}
            mutual_follows = following_users.intersection(followers_users)
            stats['mutual_follows'] = {
                'count': len(mutual_follows),
                'usernames': list(mutual_follows)
            }
        
        return stats