#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Selenium WebDriver Setup and Configuration
==========================================

Configures and initializes Selenium WebDriver for Twitter scraping with automated login.

Input: None (uses hardcoded credentials - UPDATE THESE)
Output: Configured and logged-in WebDriver instance

Author: Jonathan Uri
Date: December 2024
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager as CM
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def setup_web_driver():
    """
    Sets up and initializes a Selenium WebDriver instance for Chrome with Twitter login.
    
    Features:
    - Automatic Chrome driver installation
    - Optimized Chrome options for scraping
    - Automated Twitter login flow
    - Error handling for login issues
    
    Returns:
    - webdriver.Chrome: Configured and logged-in WebDriver instance
    
    Input: None (uses environment/hardcoded credentials)
    Output: Ready-to-use WebDriver instance logged into Twitter
    """
    print("🚀 Setting up Chrome WebDriver...")
    
    # Configure Chrome options for optimal scraping
    chrome_options = Options()
    
    # Add useful Chrome options
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Optional: Run in headless mode (uncomment next line)
    # chrome_options.add_argument("--headless")
    
    # Disable images for faster loading (optional)
    # chrome_options.add_argument("--disable-images")
    
    # User agent to avoid detection
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    try:
        # Use WebDriverManager to handle driver installation automatically
        service = Service(executable_path=CM().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✅ Chrome WebDriver initialized successfully")
        
    except Exception as e:
        print(f"❌ Error initializing WebDriver: {e}")
        raise

    # Navigate to Twitter login page via search (helps avoid detection)
    login_url = 'https://x.com/search?q=%28%23Cake%29+until%3A2019-11-21+since%3A2006-12-17&src=typed_query&f=live'
    print(f"🌐 Navigating to Twitter login page...")
    driver.get(login_url)

    # Automated login flow
    success = perform_twitter_login(driver)
    
    if not success:
        print("⚠️  Login may have failed, but continuing with scraping...")
        # Don't quit driver - some scraping might still work
    
    return driver

def perform_twitter_login(driver):
    """
    Performs automated Twitter login with error handling.
    
    Parameters:
    - driver: WebDriver instance
    
    Returns:
    - bool: True if login appears successful, False otherwise
    
    Input: WebDriver instance on Twitter login page
    Output: Boolean indicating login success
    
    NOTE: UPDATE THE CREDENTIALS BELOW WITH YOUR ACTUAL TWITTER LOGIN INFO
    """
    print("🔑 Starting Twitter login process...")
    
    # LOGIN CREDENTIALS - UPDATE THESE WITH YOUR ACTUAL CREDENTIALS
    USERNAME = 'YOUR_USERNAME_HERE'  # UPDATE THIS
    PASSWORD = 'YOUR_PASSWORD_HERE'  # UPDATE THIS
    
    if USERNAME == 'YOUR_USERNAME_HERE' or PASSWORD == 'YOUR_PASSWORD_HERE':
        print("⚠️  WARNING: Default credentials detected!")
        print("📝 Please update USERNAME and PASSWORD in WebDriverSetup.py")
        print("🔄 Continuing without login - some features may not work")
        return False

    try:
        # Step 1: Wait for and enter username
        print("📝 Entering username...")
        username_input = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@autocomplete="username"]'))
        )
        username_input.clear()
        username_input.send_keys(USERNAME)
        time.sleep(2)

        # Step 2: Click 'Next' button
        print("▶️  Clicking Next button...")
        next_button = driver.find_element(By.XPATH, '//span[text()="Next"]/ancestor::button')
        next_button.click()
        time.sleep(3)

        # Step 3: Wait for password field and enter password
        print("🔒 Entering password...")
        password_input = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@autocomplete="current-password"]'))
        )
        password_input.clear()
        password_input.send_keys(PASSWORD)
        time.sleep(2)

        # Step 4: Click 'Log in' button
        print("🚪 Clicking Log in button...")
        login_button = driver.find_element(By.XPATH, '//span[text()="Log in"]/ancestor::button')
        login_button.click()
        
        # Step 5: Wait for login to complete
        print("⏳ Waiting for login to complete...")
        time.sleep(8)

        # Verify login success by checking for home timeline or search results
        try:
            # Check if we're successfully logged in (look for common post-login elements)
            WebDriverWait(driver, 10).until(
                EC.any_of(
                    EC.presence_of_element_located((By.XPATH, '//article[@data-testid="tweet"]')),
                    EC.presence_of_element_located((By.XPATH, '//nav[@role="navigation"]')),
                    EC.presence_of_element_located((By.XPATH, '//div[@data-testid="primaryColumn"]'))
                )
            )
            print("✅ Twitter login successful!")
            return True
            
        except TimeoutException:
            print("⚠️  Could not verify login success")
            return False

    except TimeoutException as e:
        print(f"⏱️  Login timeout: {e}")
        print("💡 This might be due to Twitter's anti-bot measures")
        return False
        
    except NoSuchElementException as e:
        print(f"❌ Login element not found: {e}")
        print("💡 Twitter's login page structure may have changed")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected login error: {e}")
        return False

def setup_web_driver_with_custom_options(headless=False, disable_images=False):
    """
    Alternative setup function with customizable options.
    
    Parameters:
    - headless (bool): Run browser in headless mode
    - disable_images (bool): Disable image loading for faster scraping
    
    Returns:
    - webdriver.Chrome: Configured WebDriver instance
    """
    print("🛠️  Setting up WebDriver with custom options...")
    
    chrome_options = Options()
    
    if headless:
        chrome_options.add_argument("--headless")
        print("👻 Running in headless mode")
    
    if disable_images:
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        print("🚫 Images disabled for faster loading")
    
    # Standard options
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    service = Service(executable_path=CM().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver

if __name__ == "__main__":
    """
    Test the WebDriver setup independently.
    """
    print("🧪 Testing WebDriver setup...")
    
    try:
        driver = setup_web_driver()
        print("✅ WebDriver test successful!")
        
        # Brief test navigation
        driver.get("https://x.com")
        time.sleep(5)
        
        driver.quit()
        print("🎉 Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise