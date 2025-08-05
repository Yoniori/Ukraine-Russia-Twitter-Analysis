#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tweet Emotion Analysis System - Stage 3
=======================================

Input: cleaned_tweets_batch{1-56}.csv files with FEATURE_VALUE column
Output: Same files with emotion column added

Author: [yonatan ori]
Date: July 2025
"""

import pandas as pd
import os
from pysentimiento import create_analyzer
from tqdm import tqdm
import warnings
from typing import List, Optional

# Suppress unimportant warnings
warnings.filterwarnings("ignore")

# Configuration settings
INPUT_FOLDER = "/UPDATE/THIS/PATH/"  # UPDATE THIS PATH
TEXT_COLUMN = "FEATURE_VALUE"       # Text column name for analysis
EMOTION_COLUMN = "emotion"          # Emotion column name to be added
FILE_INDICES = list(range(1, 57))  # Files from 1 to 56

# Supported emotions list
SUPPORTED_EMOTIONS = [
    'joy',      # happiness
    'anger',    # anger
    'fear',     # fear
    'sadness',  # sadness
    'surprise', # surprise
    'disgust',  # disgust
    'others'    # other
]


def initialize_emotion_analyzer():
    """
    Initializes pysentimiento emotion analyzer
    
    Returns:
        Ready-to-use emotion analyzer
        
    Notes:
        - Uses English-trained model
        - Handles possible initialization issues
    """
    try:
        print("🧠 Initializing pysentimiento emotion analyzer...")
        analyzer = create_analyzer(task="emotion", lang="en")
        print("✅ Emotion analyzer ready successfully")
        return analyzer
    except Exception as e:
        print(f"❌ Error initializing emotion analyzer: {e}")
        print("💡 Ensure model is installed: pip install pysentimiento")
        raise


def analyze_text_emotion(analyzer, text: str) -> str:
    """
    Analyzes emotion of single text
    
    Args:
        analyzer: The emotion analyzer
        text: Text for analysis
        
    Returns:
        Detected emotion (string) or 'error' on failure
    """
    try:
        # Basic text cleaning
        clean_text = str(text).strip()
        
        # Handle empty texts
        if not clean_text:
            return "others"
        
        # Analyze emotion
        result = analyzer.predict(clean_text)
        emotion = result.output.lower()
        
        # Validate detected emotion
        if emotion in SUPPORTED_EMOTIONS:
            return emotion
        else:
            return "others"
            
    except Exception as e:
        print(f"⚠️  Error analyzing text: {e}")
        return "error"


def analyze_file_emotions(file_index: int) -> None:
    """
    Analyzes emotions in single file
    
    Args:
        file_index: File number to process
        
    Notes:
        - Loads file, analyzes emotions and saves in place
        - Shows progress bar for each file
        - Skips files that already have emotion analysis
    """
    file_path = os.path.join(INPUT_FOLDER, f"cleaned_tweets_batch{file_index}.csv")
    
    # Check file existence
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    print(f"📄 Processing file {file_index}: {os.path.basename(file_path)}")
    
    try:
        # Load the file
        df = pd.read_csv(file_path)
        
        # Check for text column for analysis existence
        if TEXT_COLUMN not in df.columns:
            print(f"⚠️  Column '{TEXT_COLUMN}' missing in file {file_index}, skipping")
            return
        
        # Check if emotion analysis already exists
        if EMOTION_COLUMN in df.columns and not df[EMOTION_COLUMN].isna().all():
            print(f"ℹ️  File {file_index} already analyzed, skipping")
            return
        
        # Prepare text list for analysis
        texts = df[TEXT_COLUMN].fillna("").astype(str).tolist()
        total_texts = len(texts)
        
        if total_texts == 0:
            print(f"⚠️  No texts for analysis in file {file_index}")
            return
        
        print(f"🎭 Analyzing emotions in {total_texts:,} texts...")
        
        # Initialize emotion analyzer
        analyzer = initialize_emotion_analyzer()
        
        # Emotion analysis with progress bar
        emotions = []
        for text in tqdm(texts, desc=f"🔍 Analyzing emotions batch {file_index}"):
            emotion = analyze_text_emotion(analyzer, text)
            emotions.append(emotion)
        
        # Update DataFrame and save
        df[EMOTION_COLUMN] = emotions
        df.to_csv(file_path, index=False, encoding='utf-8')
        
        # Show statistics
        emotion_counts = pd.Series(emotions).value_counts()
        print(f"✅ File {file_index} completed!")
        print("📊 Emotion distribution:")
        for emotion, count in emotion_counts.items():
            percentage = (count / total_texts) * 100
            print(f"   {emotion}: {count:,} ({percentage:.1f}%)")
        
    except Exception as e:
        print(f"❌ Error processing file {file_index}: {e}")


def analyze_all_files():
    """
    Analyzes emotions in all files
    """
    print("🚀 Starting emotion analysis in texts")
    print(f"📁 Working folder: {INPUT_FOLDER}")
    print(f"📊 Number of files: {len(FILE_INDICES)}")
    print(f"🎭 Supported emotions: {', '.join(SUPPORTED_EMOTIONS)}")
    
    try:
        # Process all files
        for i, file_index in enumerate(FILE_INDICES, 1):
            print(f"\n--- Processing file {i}/{len(FILE_INDICES)} ---")
            analyze_file_emotions(file_index)
        
        print("\n🎉 Emotion analysis completed successfully!")
        
        # Show general summary
        print_emotion_summary()
        
    except KeyboardInterrupt:
        print("\n⏹️  Analysis stopped by user")
    except Exception as e:
        print(f"\n❌ General error in emotion analysis: {e}")
        raise


def print_emotion_summary():
    """
    Shows general summary of emotions across all files
    """
    print("\n📈 General emotion summary:")
    
    total_emotions = {emotion: 0 for emotion in SUPPORTED_EMOTIONS}
    total_texts = 0
    processed_files = 0
    
    # Collect data from all files
    for file_index in FILE_INDICES:
        file_path = os.path.join(INPUT_FOLDER, f"cleaned_tweets_batch{file_index}.csv")
        
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path)
                if EMOTION_COLUMN in df.columns:
                    emotion_counts = df[EMOTION_COLUMN].value_counts()
                    for emotion, count in emotion_counts.items():
                        if emotion in total_emotions:
                            total_emotions[emotion] += count
                    total_texts += len(df)
                    processed_files += 1
            except Exception as e:
                print(f"⚠️  Error reading file {file_index}: {e}")
    
    # Show results
    if total_texts > 0:
        print(f"📁 Processed files: {processed_files}/{len(FILE_INDICES)}")
        print(f"📊 Total texts: {total_texts:,}")
        print("\n🎭 General emotion distribution:")
        
        for emotion in SUPPORTED_EMOTIONS:
            count = total_emotions[emotion]
            percentage = (count / total_texts) * 100 if total_texts > 0 else 0
            print(f"   {emotion.capitalize()}: {count:,} ({percentage:.1f}%)")
    else:
        print("❌ No emotion data found for summary")


if __name__ == "__main__":
    """Main entry point for the script"""
    analyze_all_files()
