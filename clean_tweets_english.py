#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Russian Tweet Cleaning System - Stage 1
=======================================

Input: russian_lang_tweets_part{1-609}.csv files
Output: cleaned_tweets_batch{1-n}.csv files with cleaned text

Author: [Yonatan ori]
Date: July 2025
"""

import pandas as pd
import re
import os
from pathlib import Path

# Configuration settings
SCRIPT_FOLDER = os.path.dirname(os.path.realpath(__file__))
INPUT_FOLDER = '/path/to/your/data/'  # UPDATE THIS PATH
CHUNK_SIZE = 50000  # Optimal batch size for processing
NUM_INPUT_FILES = 609  # Total input files


def clean_tweet(text):
    """
    Cleans tweet text from irrelevant content
    
    Args:
        text (str): Original tweet text
        
    Returns:
        str: Clean text or empty string if input invalid
        
    Cleaning process:
    1. Remove URLs (http/https links)
    2. Remove hashtags (but keep the words)
    3. Remove mentions (@username)
    4. Preserve emojis and punctuation
    5. Normalize whitespace
    """
    # Input validation
    if not isinstance(text, str):
        return ""

    # Remove URLs (http/https links)
    text = re.sub(r"http\S+", "", text)
    
    # Remove hashtags (but not the words themselves) 
    text = re.sub(r"#\w+", "", text)
    
    # Remove mentions (@username)
    text = re.sub(r"@\w+", "", text)
    
    # Note: emojis and punctuation marks are preserved naturally
    
    # Normalize whitespace - replace multiple spaces with single space
    text = re.sub(r"\s+", " ", text).strip()
    
    return text


def process_tweet_files():
    """
    Processes all Russian tweet files and organizes into clean batch files
    
    Process:
    1. Iterate through all input files (1-609)
    2. Clean the tweets
    3. Filter empty tweets
    4. Organize into batch files of 50K tweets
    """
    file_index = 1      # Output file counter
    buffer = []         # Buffer for storing tweets before saving
    row_counter = 0     # Row counter in current buffer
    
    print("🚀 Starting Russian tweet files processing")
    print(f"📁 Input folder: {INPUT_FOLDER}")
    print(f"💾 Output folder: {SCRIPT_FOLDER}")
    print(f"📊 Batch size: {CHUNK_SIZE:,} tweets")
    
    # Process all input files
    for i in range(1, NUM_INPUT_FILES + 1):
        file_path = os.path.join(INPUT_FOLDER, f"russian_lang_tweets_part{i}.csv")
        
        # Check file existence
        if not os.path.exists(file_path):
            print(f"⚠️  File not found: {file_path}")
            continue
        
        print(f"🔄 Processing file {i}/{NUM_INPUT_FILES}: {os.path.basename(file_path)}")
        
        try:
            # Load the file
            df = pd.read_csv(file_path)
            
            # Check for TWEET column existence
            if 'TWEET' not in df.columns:
                print(f"⚠️  No 'TWEET' column found in {file_path}, skipping")
                continue
            
            # Clean the tweets
            df['cleaned_tweet'] = df['TWEET'].astype(str).apply(clean_tweet)
            
            # Filter empty tweets after cleaning
            df = df[df['cleaned_tweet'].str.strip() != ""]
            
            print(f"✅ Cleaned {len(df):,} tweets from file {i}")
            
            # Add to buffer
            for _, row in df.iterrows():
                if not row['cleaned_tweet']:  # Additional check for empty tweets
                    continue
                    
                buffer.append(row)
                row_counter += 1
                
                # Check if we reached full batch size
                if row_counter >= CHUNK_SIZE:
                    _save_batch(buffer, file_index)
                    buffer = []
                    row_counter = 0
                    file_index += 1
                    
        except Exception as e:
            print(f"❌ Error processing file {file_path}: {e}")
            continue
    
    # Save remaining tweets in buffer
    if buffer:
        _save_batch(buffer, file_index)
    
    print(f"🎉 Processing completed! Created {file_index} batch files")


def _save_batch(buffer, file_index):
    """
    Saves batch of tweets to CSV file
    
    Args:
        buffer (list): List of rows to save
        file_index (int): Output file number
    """
    out_df = pd.DataFrame(buffer)
    out_file = os.path.join(SCRIPT_FOLDER, f"cleaned_tweets_batch{file_index}.csv")
    out_df.to_csv(out_file, index=False, encoding='utf-8')
    print(f"💾 Saved {len(out_df):,} tweets to file: {os.path.basename(out_file)}")


if __name__ == "__main__":
    """Main entry point for the script"""
    try:
        process_tweet_files()
    except KeyboardInterrupt:
        print("\n⏹️  Processing stopped by user")
    except Exception as e:
        print(f"❌ General error: {e}")
        raise
