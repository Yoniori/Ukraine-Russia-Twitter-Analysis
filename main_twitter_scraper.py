#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Twitter (X) Data Scraper - Main Script
======================================

Complete scraping system for Twitter data including tweets, user timelines, and follower networks.

Input: Excel files with usernames, hashtags, date ranges
Output: CSV files with scraped Twitter data

Author: Jonathan Uri
Date: December 2024
"""

import time
import pandas as pd
from WebDriverSetup import setup_web_driver
from SearchScrapper import SearchScrapper
from SearchScrapperDetails import SearchScrapperDetails

def read_users_from_excel(file_path, column_name):
    """
    Reads target usernames from specified column in Excel file.

    Parameters:
    - file_path (str): Path to the Excel file
    - column_name (str): Name of the column containing usernames

    Returns:
    - list: List of usernames extracted from Excel file
    
    Input: Excel file with username column
    Output: List of clean usernames (without @ symbols)
    """
    try:
        # Read Excel file
        df = pd.read_excel(file_path)

        # Check if column exists
        if column_name not in df.columns:
            raise ValueError(f"Column '{column_name}' not found in the Excel file")

        # Get unique usernames, remove any NaN values and convert to list
        users = df[column_name].dropna().unique().tolist()

        # Remove any leading/trailing whitespace and @ symbols
        users = [str(user).strip().replace('@', '') for user in users]

        print(f"Successfully loaded {len(users)} unique usernames from {file_path}")
        return users

    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return []

def main(side, excel_file_path=None, username_column=None):
    """
    Main entry point for Twitter scraping operations.

    Parameters:
    - side (int): Scraping mode selector
        - 0: Scrape tweets using hashtags for specific dates
        - 1: Scrape tweets from user timelines  
        - 3: Scrape following/followers/verified followers of users
    - excel_file_path (str): Path to Excel file containing usernames (for side=3)
    - username_column (str): Name of column containing usernames in Excel file (for side=3)
    
    Input: Configuration parameters and Excel files
    Output: CSV files with scraped Twitter data
    """
    start_time = time.time()
    driver = setup_web_driver()

    if side == 0:
        # Hashtag-based tweet scraping
        # Input: Hashtag list, date range
        # Output: CSV file with tweets containing specified hashtags
        
        hashtags = ['hamas']  # Replace or extend this list with relevant hashtags
        start_date = "2023-11-25"
        end_date = "2023-12-02"
        all_tweets = []

        print(f"🔍 Scraping tweets for hashtags: {hashtags}")
        print(f"📅 Date range: {start_date} to {end_date}")

        for hashtag in hashtags:
            search_query = f'https://x.com/search?q=%28%23{hashtag}%29+until%3A{end_date}+since%3A{start_date}&src=typed_query&f=live'
            scraped_tweets = SearchScrapper(driver).scrape_twitter_query(search_query, hashtag, max_tweets=50)

            # Process and format tweet data
            tweets_data = [
                (
                    tweet.ID, tweet.content, tweet.author, tweet.fullName, tweet.url, tweet.timestamp,
                    tweet.image_url, None, None, tweet.video_url, tweet.video_preview_image_url,
                    None, None, None, None, tweet.comments, tweet.retweets, None, tweet.likes,
                    tweet.hashtags, tweet.views, hashtag
                )
                for tweet in scraped_tweets
            ]
            all_tweets.extend(tweets_data)

        # Save hashtag scraping results
        columns = [
            'id', 'text', 'username', 'fullname', 'url', 'publication_date', 'photo_url',
            'photo_preview_image_url', 'photo_alt_text', 'video_url', 'video_preview_image_url',
            'video_alt_text', 'animated_gif_url', 'animated_gif_preview_image_url', 'animated_gif_alt_text',
            'replies', 'retweets', 'quotes', 'likes', 'hashtags', 'views', 'target'
        ]
        df = pd.DataFrame(all_tweets, columns=columns)
        output_file = f"{start_date}_to_{end_date}_hashtag_tweets.csv"
        df.to_csv(output_file, index=False)
        print(f"✅ Hashtag data saved to {output_file}")
        print(f"📊 Total tweets scraped: {len(all_tweets)}")

    elif side == 1:
        # User timeline scraping
        # Input: List of usernames, date range
        # Output: CSV file with tweets from specified user accounts
        
        users = read_users_from_excel(excel_file_path, username_column)
        start_date = "2023-09-25"
        end_date = "2025-01-01"
        all_tweets = []

        print(f"👤 Scraping tweets from {len(users)} users")
        print(f"📅 Date range: {start_date} to {end_date}")

        for user in users:
            print(f"🔄 Processing user: @{user}")
            search_query = f'https://x.com/search?q=%28from%3A{user}%29+until%3A{end_date}+since%3A{start_date}&src=typed_query&f=live'
            scraped_tweets = SearchScrapper(driver).scrape_twitter_query(search_query, user, max_tweets=100)

            tweets_data = [
                (
                    tweet.ID, tweet.content, tweet.author, tweet.fullName, tweet.url, tweet.timestamp,
                    tweet.image_url, None, None, tweet.video_url, tweet.video_preview_image_url,
                    None, None, None, None, tweet.comments, tweet.retweets, None, tweet.likes,
                    tweet.hashtags, tweet.views, user
                )
                for tweet in scraped_tweets
            ]
            all_tweets.extend(tweets_data)
            print(f"   📝 Found {len(tweets_data)} tweets for @{user}")

        # Save user timeline results
        columns = [
            'id', 'text', 'username', 'fullname', 'url', 'publication_date', 'photo_url',
            'photo_preview_image_url', 'photo_alt_text', 'video_url', 'video_preview_image_url',
            'video_alt_text', 'animated_gif_url', 'animated_gif_preview_image_url', 'animated_gif_alt_text',
            'replies', 'retweets', 'quotes', 'likes', 'hashtags', 'views', 'target'
        ]
        df = pd.DataFrame(all_tweets, columns=columns)
        output_file = f"{start_date}_to_{end_date}_user_tweets.csv"
        df.to_csv(output_file, index=False)
        print(f"✅ User timeline data saved to {output_file}")
        print(f"📊 Total tweets scraped: {len(all_tweets)}")

    elif side == 3:
        # User network scraping (followers/following)
        # Input: Excel file with usernames
        # Output: CSV file with follower/following relationships
        
        # Validate Excel parameters
        if not excel_file_path or not username_column:
            raise ValueError("Excel file path and username column name are required for side=3")

        # Read users from Excel file
        users_follows = read_users_from_excel(excel_file_path, username_column)

        if not users_follows:
            print("❌ No users found in Excel file. Exiting...")
            return

        print(f"🌐 Scraping network data for {len(users_follows)} users")
        
        all_follows = []
        follow_types = [
            ("following", "https://x.com/{}/following"),
            ("followers", "https://x.com/{}/followers"),
            ("verified_followers", "https://x.com/{}/verified_followers")
        ]

        for target in users_follows:
            print(f"🔄 Processing user network: @{target}")
            for follow_type, url_template in follow_types:
                print(f"   📊 Scraping {follow_type}...")
                url = url_template.format(target)
                scraped_users = SearchScrapperDetails(driver).scrape_following_page(url, max_users=100)

                follows_data = [
                    (target, user.author, follow_type)
                    for user in scraped_users
                ]
                all_follows.extend(follows_data)
                print(f"   ✅ Found {len(scraped_users)} {follow_type}")

        # Save network data results
        columns = ['target_username', 'other_username', 'type']
        df = pd.DataFrame(all_follows, columns=columns)

        # Add timestamp to output filename
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_file = f"user_follows_{timestamp}.csv"
        df.to_csv(output_file, index=False)
        print(f"✅ Network data saved to {output_file}")
        print(f"📊 Total relationships scraped: {len(all_follows)}")

    else:
        print("❌ Invalid side argument. Use 0 for hashtags, 1 for user timelines, or 3 for user follows.")
        return

    # Cleanup
    driver.quit()
    
    # Execution summary
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"\n🎉 Scraping completed successfully!")
    print(f"⏱️  Total execution time: {elapsed_time:.2f} seconds")

if __name__ == '__main__':
    """
    Main execution block - Configure your scraping parameters here
    
    Input Configuration:
    - excel_file: Path to Excel file containing usernames
    - username_column: Column name in Excel file with usernames
    - side: Scraping mode (0=hashtags, 1=users, 3=networks)
    
    Output: CSV files with scraped Twitter data
    """
    
    # Configuration - UPDATE THESE PATHS FOR YOUR SETUP
    excel_file = "/home/lebanon-israel-war-user/Desktop/Tweets/all user name.xlsx"  # UPDATE THIS PATH
    username_column = "all_user_name"  # UPDATE THIS COLUMN NAME
    
    print("🚀 Twitter Scraper by Jonathan Uri")
    print("=" * 50)
    
    # Run user timeline scraping
    main(side=1, excel_file_path=excel_file, username_column=username_column)