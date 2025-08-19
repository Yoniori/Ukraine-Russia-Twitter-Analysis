#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Topic Modeling and Sentiment Analysis System
====================================================

Complete system combining BERTopic for topic modeling and pysentimiento for emotion analysis,
based on Natalia's research methodology for Russian tweet analysis.

Input: CSV files with tweet data (text column)
Output: Topics, emotions, and comprehensive visualizations

Author: Jonathan Uri
Date: August 2025
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from bertopic import BERTopic
from pysentimiento import create_analyzer
from sklearn.feature_extraction.text import CountVectorizer
from umap import UMAP
from hdbscan import HDBSCAN
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
from pathlib import Path
import os
from datetime import datetime
import logging
from tqdm import tqdm

warnings.filterwarnings("ignore")

# Configuration
INPUT_FOLDER = "/UPDATE/THIS/PATH/"  # UPDATE THIS PATH
OUTPUT_FOLDER = "topic_emotion_analysis_results"
LOG_FILE = "topic_analysis.log"

# Analysis parameters
MIN_TOPIC_SIZE = 10          # Minimum size for topics
N_NEIGHBORS = 15             # UMAP neighbors
N_COMPONENTS = 5             # UMAP dimensions
MIN_CLUSTER_SIZE = 10        # HDBSCAN minimum cluster size
RANDOM_STATE = 42           # For reproducibility

class TopicEmotionAnalyzer:
    """
    Advanced analyzer combining BERTopic and pysentimiento for comprehensive text analysis.
    
    Input: Text data from CSV files
    Output: Topic models, emotion analysis, and visualizations
    """
    
    def __init__(self, language="en", min_topic_size=MIN_TOPIC_SIZE):
        """
        Initialize the analyzer with specified parameters.
        
        Parameters:
        - language (str): Language for emotion analysis ("en", "es", "pt")
        - min_topic_size (int): Minimum size for topic clustering
        """
        self.language = language
        self.min_topic_size = min_topic_size
        self.setup_logging()
        
        # Initialize models
        self.emotion_analyzer = None
        self.topic_model = None
        self.results = {}
        
        print("🚀 Initializing Topic and Emotion Analyzer...")
        self._initialize_models()
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(LOG_FILE),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _initialize_models(self):
        """Initialize BERTopic and pysentimiento models"""
        try:
            # Initialize emotion analyzer
            print("🧠 Loading emotion analysis model...")
            self.emotion_analyzer = create_analyzer(task="emotion", lang=self.language)
            print("✅ Emotion analyzer loaded successfully")
            
            # Initialize BERTopic with optimized parameters
            print("🔍 Setting up BERTopic model...")
            
            # UMAP model for dimensionality reduction
            umap_model = UMAP(
                n_neighbors=N_NEIGHBORS,
                n_components=N_COMPONENTS,
                min_dist=0.0,
                metric='cosine',
                random_state=RANDOM_STATE
            )
            
            # HDBSCAN for clustering
            hdbscan_model = HDBSCAN(
                min_cluster_size=MIN_CLUSTER_SIZE,
                metric='euclidean',
                cluster_selection_method='eom',
                prediction_data=True
            )
            
            # Vectorizer for topic representation
            vectorizer_model = CountVectorizer(
                ngram_range=(1, 2),
                stop_words="english",
                max_features=5000,
                min_df=2,
                max_df=0.95
            )
            
            # Create BERTopic model
            self.topic_model = BERTopic(
                umap_model=umap_model,
                hdbscan_model=hdbscan_model,
                vectorizer_model=vectorizer_model,
                min_topic_size=self.min_topic_size,
                nr_topics="auto",
                calculate_probabilities=True,
                verbose=True
            )
            
            print("✅ BERTopic model initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing models: {e}")
            raise
    
    def load_data(self, file_path, text_column="text", date_column=None):
        """
        Load and prepare data for analysis.
        
        Parameters:
        - file_path (str): Path to CSV file
        - text_column (str): Name of column containing text data
        - date_column (str): Name of column containing date data (optional)
        
        Returns:
        - pd.DataFrame: Loaded and prepared data
        """
        try:
            print(f"📂 Loading data from: {file_path}")
            df = pd.read_csv(file_path)
            
            # Validate required columns
            if text_column not in df.columns:
                raise ValueError(f"Text column '{text_column}' not found in data")
            
            # Clean and prepare text data
            df[text_column] = df[text_column].fillna("").astype(str)
            df = df[df[text_column].str.strip() != ""]  # Remove empty texts
            
            # Handle date column if provided
            if date_column and date_column in df.columns:
                df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
            
            print(f"✅ Loaded {len(df):,} text entries for analysis")
            self.logger.info(f"Data loaded: {len(df)} entries from {file_path}")
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error loading data: {e}")
            raise
    
    def analyze_emotions(self, texts):
        """
        Analyze emotions in text data using pysentimiento.
        
        Parameters:
        - texts (list): List of texts to analyze
        
        Returns:
        - list: List of detected emotions
        """
        print("🎭 Analyzing emotions...")
        emotions = []
        
        for text in tqdm(texts, desc="Emotion analysis"):
            try:
                result = self.emotion_analyzer.predict(text)
                emotions.append(result.output.lower())
            except Exception as e:
                emotions.append("others")
                self.logger.warning(f"Error analyzing emotion for text: {e}")
        
        print(f"✅ Emotion analysis completed for {len(emotions)} texts")
        return emotions
    
    def perform_topic_modeling(self, texts):
        """
        Perform topic modeling using BERTopic.
        
        Parameters:
        - texts (list): List of texts for topic modeling
        
        Returns:
        - tuple: (topics, probabilities, topic_model)
        """
        print("🔍 Performing topic modeling with BERTopic...")
        
        try:
            # Fit the model and predict topics
            topics, probabilities = self.topic_model.fit_transform(texts)
            
            # Get topic information
            topic_info = self.topic_model.get_topic_info()
            
            print(f"✅ Topic modeling completed!")
            print(f"📊 Found {len(topic_info)} topics")
            print(f"🔢 Topic distribution:")
            for _, row in topic_info.head(10).iterrows():
                print(f"   Topic {row['Topic']}: {row['Count']} documents - {row['Name']}")
            
            self.logger.info(f"Topic modeling completed: {len(topic_info)} topics found")
            
            return topics, probabilities, topic_info
            
        except Exception as e:
            self.logger.error(f"Error in topic modeling: {e}")
            raise
    
    def create_topic_visualizations(self, save_folder):
        """
        Create comprehensive topic visualizations.
        
        Parameters:
        - save_folder (str): Folder to save visualizations
        """
        print("📊 Creating topic visualizations...")
        
        try:
            # Create output folder
            Path(save_folder).mkdir(parents=True, exist_ok=True)
            
            # 1. Topic hierarchy visualization
            fig_hierarchy = self.topic_model.visualize_hierarchy()
            fig_hierarchy.write_html(f"{save_folder}/topic_hierarchy.html")
            
            # 2. Intertopic distance map
            fig_topics = self.topic_model.visualize_topics()
            fig_topics.write_html(f"{save_folder}/intertopic_distance.html")
            
            # 3. Topic word scores
            fig_barchart = self.topic_model.visualize_barchart(top_k_topics=10)
            fig_barchart.write_html(f"{save_folder}/topic_words.html")
            
            # 4. Document similarity heatmap
            fig_heatmap = self.topic_model.visualize_heatmap()
            fig_heatmap.write_html(f"{save_folder}/topic_similarity.html")
            
            print("✅ Interactive topic visualizations saved")
            
        except Exception as e:
            self.logger.error(f"Error creating topic visualizations: {e}")
    
    def create_emotion_visualizations(self, df, save_folder):
        """
        Create emotion analysis visualizations.
        
        Parameters:
        - df (pd.DataFrame): DataFrame with emotion data
        - save_folder (str): Folder to save visualizations
        """
        print("🎨 Creating emotion visualizations...")
        
        # Set up matplotlib style
        plt.style.use('seaborn-v0_8')
        plt.rcParams['figure.figsize'] = (12, 8)
        
        # 1. Emotion distribution pie chart
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # Emotion distribution
        emotion_counts = df['emotion'].value_counts()
        axes[0, 0].pie(emotion_counts.values, labels=emotion_counts.index, autopct='%1.1f%%')
        axes[0, 0].set_title('Emotion Distribution', fontsize=14, fontweight='bold')
        
        # Emotion bar chart
        emotion_counts.plot(kind='bar', ax=axes[0, 1], color='skyblue')
        axes[0, 1].set_title('Emotion Counts', fontsize=14, fontweight='bold')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Topic distribution
        if 'topic' in df.columns:
            topic_counts = df['topic'].value_counts().head(10)
            topic_counts.plot(kind='bar', ax=axes[1, 0], color='lightcoral')
            axes[1, 0].set_title('Top 10 Topics Distribution', fontsize=14, fontweight='bold')
            axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Emotion-Topic heatmap
        if 'topic' in df.columns:
            emotion_topic_crosstab = pd.crosstab(df['emotion'], df['topic'])
            sns.heatmap(emotion_topic_crosstab.iloc[:, :10], annot=True, fmt='d', 
                       cmap='YlOrRd', ax=axes[1, 1])
            axes[1, 1].set_title('Emotion-Topic Correlation', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(f"{save_folder}/emotion_analysis_overview.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Time-based analysis (if date column exists)
        if 'date' in df.columns:
            self._create_temporal_analysis(df, save_folder)
        
        print("✅ Emotion visualizations created")
    
    def _create_temporal_analysis(self, df, save_folder):
        """Create time-based emotion and topic analysis"""
        try:
            # Convert date column
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df = df.dropna(subset=['date'])
            
            # Group by month
            df['month'] = df['date'].dt.to_period('M')
            
            # Emotion trends over time
            fig, axes = plt.subplots(2, 1, figsize=(15, 10))
            
            # Monthly emotion distribution
            emotion_monthly = df.groupby(['month', 'emotion']).size().unstack(fill_value=0)
            emotion_monthly.plot(kind='line', ax=axes[0], marker='o')
            axes[0].set_title('Emotion Trends Over Time', fontsize=14, fontweight='bold')
            axes[0].legend(title='Emotions', bbox_to_anchor=(1.05, 1), loc='upper left')
            
            # Monthly topic distribution
            if 'topic' in df.columns:
                topic_monthly = df.groupby(['month', 'topic']).size().unstack(fill_value=0)
                top_topics = topic_monthly.sum().nlargest(5).index
                topic_monthly[top_topics].plot(kind='line', ax=axes[1], marker='s')
                axes[1].set_title('Top 5 Topics Trends Over Time', fontsize=14, fontweight='bold')
                axes[1].legend(title='Topics', bbox_to_anchor=(1.05, 1), loc='upper left')
            
            plt.tight_layout()
            plt.savefig(f"{save_folder}/temporal_analysis.png", dpi=300, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            self.logger.warning(f"Could not create temporal analysis: {e}")
    
    def analyze_complete_dataset(self, file_path, text_column="text", date_column=None):
        """
        Perform complete analysis on dataset.
        
        Parameters:
        - file_path (str): Path to CSV file
        - text_column (str): Name of text column
        - date_column (str): Name of date column (optional)
        
        Returns:
        - pd.DataFrame: Complete analyzed dataset
        """
        print("🎯 Starting complete topic and emotion analysis...")
        
        # Load data
        df = self.load_data(file_path, text_column, date_column)
        
        # Prepare texts
        texts = df[text_column].tolist()
        
        # Analyze emotions
        emotions = self.analyze_emotions(texts)
        df['emotion'] = emotions
        
        # Perform topic modeling
        topics, probabilities, topic_info = self.perform_topic_modeling(texts)
        df['topic'] = topics
        df['topic_probability'] = [prob.max() if len(prob) > 0 else 0.0 for prob in probabilities]
        
        # Add topic names
        topic_names = {}
        for _, row in topic_info.iterrows():
            topic_names[row['Topic']] = row['Name']
        df['topic_name'] = df['topic'].map(topic_names)
        
        # Store results
        self.results = {
            'dataframe': df,
            'topic_info': topic_info,
            'model': self.topic_model
        }
        
        # Create visualizations
        output_folder = Path(OUTPUT_FOLDER)
        output_folder.mkdir(exist_ok=True)
        
        self.create_topic_visualizations(output_folder)
        self.create_emotion_visualizations(df, output_folder)
        
        # Save processed data
        output_file = output_folder / "analyzed_data_with_topics_emotions.csv"
        df.to_csv(output_file, index=False)
        
        # Save topic information
        topic_info.to_csv(output_folder / "topic_information.csv", index=False)
        
        print(f"🎉 Complete analysis finished!")
        print(f"📊 Results summary:")
        print(f"   • Total texts analyzed: {len(df):,}")
        print(f"   • Topics discovered: {len(topic_info)}")
        print(f"   • Emotions detected: {df['emotion'].nunique()}")
        print(f"   • Results saved to: {output_folder}")
        
        return df
    
    def generate_summary_report(self):
        """Generate a comprehensive summary report"""
        if not self.results:
            print("❌ No analysis results available. Run analysis first.")
            return
        
        df = self.results['dataframe']
        topic_info = self.results['topic_info']
        
        print("\n" + "="*60)
        print("📋 COMPREHENSIVE ANALYSIS REPORT")
        print("="*60)
        
        # Basic statistics
        print(f"📊 Dataset Statistics:")
        print(f"   • Total documents: {len(df):,}")
        print(f"   • Unique topics: {len(topic_info)}")
        print(f"   • Average topic probability: {df['topic_probability'].mean():.3f}")
        
        # Top emotions
        print(f"\n🎭 Emotion Distribution:")
        emotion_dist = df['emotion'].value_counts()
        for emotion, count in emotion_dist.head(7).items():
            percentage = (count / len(df)) * 100
            print(f"   • {emotion.capitalize()}: {count:,} ({percentage:.1f}%)")
        
        # Top topics
        print(f"\n🔍 Top Topics:")
        for _, row in topic_info.head(10).iterrows():
            print(f"   • Topic {row['Topic']}: {row['Count']} docs - {row['Name'][:60]}...")
        
        # Topic-Emotion correlation
        print(f"\n🔗 Topic-Emotion Insights:")
        emotion_topic_corr = pd.crosstab(df['emotion'], df['topic'])
        
        for emotion in emotion_dist.head(5).index:
            top_topic = emotion_topic_corr.loc[emotion].idxmax()
            topic_name = topic_info[topic_info['Topic'] == top_topic]['Name'].iloc[0]
            print(f"   • {emotion.capitalize()} → Topic {top_topic}: {topic_name[:50]}...")


def main():
    """
    Main execution function - demonstrates complete analysis workflow
    """
    print("🚀 Advanced Topic and Emotion Analysis System")
    print("=" * 50)
    print("Based on Natalia's research methodology")
    print("Author: Jonathan Uri")
    print("=" * 50)
    
    # Initialize analyzer
    analyzer = TopicEmotionAnalyzer(language="en", min_topic_size=MIN_TOPIC_SIZE)
    
    # Example usage - UPDATE THESE PATHS
    file_path = "/UPDATE/THIS/PATH/your_data.csv"  # UPDATE THIS
    text_column = "text"  # UPDATE IF NEEDED
    date_column = None    # UPDATE IF YOU HAVE DATES
    
    try:
        # Perform complete analysis
        results_df = analyzer.analyze_complete_dataset(
            file_path=file_path,
            text_column=text_column,
            date_column=date_column
        )
        
        # Generate summary report
        analyzer.generate_summary_report()
        
        print("\n🎉 Analysis completed successfully!")
        print(f"📁 Results saved in: {OUTPUT_FOLDER}/")
        print("📊 Check the HTML files for interactive visualizations")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        logging.error(f"Analysis failed: {e}")


if __name__ == "__main__":
    main()