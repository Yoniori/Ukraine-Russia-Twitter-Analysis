#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tweet Translation System - Stage 2
==================================

Input: cleaned_tweets_batch{1-56}.csv files
Output: Same files with translated_tweet column added

Author: [yonatan ori]
Date: July 2025
"""

import pandas as pd
import requests
import time
import os
from multiprocessing import Pool, cpu_count
from typing import List, Optional

# API settings
API_KEY = "YOUR_API_KEY_HERE"  # INSERT YOUR API KEY HERE
TRANSLATE_URL = "https://translation.googleapis.com/language/translate/v2"

# Processing settings
INPUT_FOLDER = "/UPDATE/THIS/PATH/"  # UPDATE THIS PATH
SCRIPT_FOLDER = os.path.dirname(os.path.realpath(__file__))
BATCH_SIZE = 50          # Number of texts to translate per request
REQUEST_DELAY = 0.5      # Delay between requests (seconds)
MAX_WORKERS = 4          # Maximum number of processes
FILE_RANGE = range(1, 57)  # File range to process (1-56)


def translate_batch(texts: List[str]) -> List[str]:
    """
    Translates list of texts from Russian to English
    
    Args:
        texts: List of texts to translate
        
    Returns:
        List of translated texts (same length as input)
        
    Notes:
        - Uses Google Cloud Translation API
        - Handles errors and returns empty strings on failure
        - Preserves text order
    """
    if not texts:
        return []
        
    # Build request parameters
    params = {
        'q': texts,              # Texts to translate
        'target': 'en',          # Target language: English
        'source': 'ru',          # Source language: Russian (optional)
        'format': 'text',        # Plain text format
        'key': API_KEY           # API key
    }
    
    try:
        # Execute translation request
        response = requests.post(TRANSLATE_URL, data=params, timeout=30)
        response.raise_for_status()  # Raise exception if status code not OK
        
        result = response.json()
        
        # Check response validity
        if 'data' in result and 'translations' in result['data']:
            translations = [t['translatedText'] for t in result['data']['translations']]
            return translations
        else:
            print(f"⚠️  Unexpected API response: {result}")
            return ["" for _ in texts]
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error in batch translation: {e}")
        return ["" for _ in texts]
    except Exception as e:
        print(f"❌ General error in batch translation: {e}")
        return ["" for _ in texts]


def process_file(file_index: int) -> None:
    """
    Processes single file - translates all tweets in file
    
    Args:
        file_index: File number to process
        
    Notes:
        - Loads file, translates in batches and saves in place
        - Shows progress for each file
        - Skips files that already have translation
    """
    file_path = os.path.join(INPUT_FOLDER, f"cleaned_tweets_batch{file_index}.csv")
    
    # Check file existence
    if not os.path.exists(file_path):
        print(f"⚠️  File not found: {file_path}")
        return
    
    print(f"📁 Processing file {file_index}: {os.path.basename(file_path)}")
    
    try:
        # Load the file
        df = pd.read_csv(file_path)
        
        # Check for clean tweets column existence
        if 'cleaned_tweet' not in df.columns:
            print(f"⚠️  'cleaned_tweet' column missing in file {file_index}, skipping")
            return
        
        # Create translation column if not exists
        if 'translated_tweet' not in df.columns:
            df['translated_tweet'] = ""
        
        # Prepare tweet list for translation
        tweets = df['cleaned_tweet'].fillna("").astype(str).tolist()
        total_tweets = len(tweets)
        
        if total_tweets == 0:
            print(f"⚠️  No tweets to translate in file {file_index}")
            return
        
        print(f"🔤 Starting translation of {total_tweets:,} tweets...")
        
        # Translate in batches
        all_translations = []
        for start in range(0, total_tweets, BATCH_SIZE):
            end = min(start + BATCH_SIZE, total_tweets)
            
            # Prepare batch for translation (only non-empty texts)
            batch_tweets = []
            batch_indices = []
            
            for i in range(start, end):
                tweet = tweets[i].strip()
                if tweet:  # Only if tweet is not empty
                    batch_tweets.append(tweet)
                    batch_indices.append(i)
            
            # Translate the batch
            if batch_tweets:
                translated_batch = translate_batch(batch_tweets)
                
                # Map results back to original positions
                for idx, translation in zip(batch_indices, translated_batch):
                    while len(all_translations) <= idx:
                        all_translations.append("")
                    all_translations[idx] = translation
            
            # Show progress
            progress = min(end, total_tweets)
            print(f"📝 File {file_index}: translated {progress:,}/{total_tweets:,} tweets "
                  f"({progress/total_tweets*100:.1f}%)")
            
            # Delay between requests to avoid API limits
            time.sleep(REQUEST_DELAY)
        
        # Complete translation list to required length
        while len(all_translations) < total_tweets:
            all_translations.append("")
        
        # Update DataFrame and save
        df['translated_tweet'] = all_translations[:total_tweets]
        df.to_csv(file_path, index=False, encoding='utf-8')
        
        # Statistics
        successful_translations = sum(1 for t in all_translations if t.strip())
        print(f"✅ File {file_index} completed: {successful_translations:,}/{total_tweets:,} "
              f"tweets translated successfully ({successful_translations/total_tweets*100:.1f}%)")
        
    except Exception as e:
        print(f"❌ Error processing file {file_index}: {e}")


def main():
    """
    Main function - manages parallel translation process
    """
    print("🚀 Starting tweet translation to English")
    print(f"🔧 Settings: Batch={BATCH_SIZE}, Delay={REQUEST_DELAY}s, Workers={MAX_WORKERS}")
    print(f"📊 File range: {FILE_RANGE.start}-{FILE_RANGE.stop-1}")
    
    # Check API Key validity
    if not API_KEY or API_KEY == "YOUR_API_KEY_HERE":
        print("❌ Error: Valid API_KEY required for Google Translate service")
        return
    
    # Calculate optimal number of workers
    num_workers = min(cpu_count(), MAX_WORKERS)
    print(f"⚙️  Using {num_workers} parallel processes")
    
    try:
        # Parallel processing of files
        with Pool(num_workers) as pool:
            # Process in reverse order (high to low) for debugging purposes
            file_list = list(reversed(FILE_RANGE))
            pool.map(process_file, file_list)
        
        print("🎉 Translation of all files completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⏹️  Translation stopped by user")
    except Exception as e:
        print(f"❌ General error in translation process: {e}")
        raise


if __name__ == "__main__":
    """Main entry point for the script"""
    main()
