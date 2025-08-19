#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Emotion and Topic Visualization System
===============================================

Creates publication-quality visualizations for emotion and topic analysis,
replicating and extending Natalia's research visualizations.

Input: CSV files with emotion and topic data
Output: High-quality static and interactive visualizations

Author: Jonathan Uri
Date: August 2025
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
from wordcloud import WordCloud
from pathlib import Path
import warnings
from datetime import datetime
import colorcet as cc

warnings.filterwarnings("ignore")

class AdvancedEmotionVisualizer:
    """
    Advanced visualization system for emotion and topic analysis results.
    
    Input: Analyzed data with emotions and topics
    Output: Publication-ready visualizations matching academic standards
    """
    
    def __init__(self, output_folder="advanced_visualizations"):
        """
        Initialize the visualizer.
        
        Parameters:
        - output_folder (str): Folder to save all visualizations
        """
        self.output_folder = Path(output_folder)
        self.output_folder.mkdir(exist_ok=True)
        
        # Set up visualization styles
        self._setup_styles()
        
        # Define color palettes
        self.emotion_colors = {
            'joy': '#FFD700',           # Gold
            'anger': '#FF4500',         # Red Orange  
            'fear': '#8A2BE2',          # Blue Violet
            'sadness': '#4169E1',       # Royal Blue
            'surprise': '#FF69B4',      # Hot Pink
            'disgust': '#32CD32',       # Lime Green
            'others': '#708090',        # Slate Gray
            'love': '#FF1493',          # Deep Pink
            'neutral': '#A9A9A9'        # Dark Gray
        }
        
        print(f"🎨 Advanced Emotion Visualizer initialized")
        print(f"📁 Output folder: {self.output_folder}")
    
    def _setup_styles(self):
        """Setup matplotlib and seaborn styles for publication quality"""
        # Set matplotlib style
        plt.style.use('seaborn-v0_8-whitegrid')
        
        # Configure matplotlib parameters
        plt.rcParams.update({
            'figure.figsize': (12, 8),
            'figure.dpi': 300,
            'savefig.dpi': 300,
            'font.size': 12,
            'axes.titlesize': 16,
            'axes.labelsize': 14,
            'xtick.labelsize': 12,
            'ytick.labelsize': 12,
            'legend.fontsize': 11,
            'figure.titlesize': 18,
            'font.family': 'DejaVu Sans',
            'axes.grid': True,
            'grid.alpha': 0.3
        })
        
        # Set seaborn palette
        sns.set_palette("husl")
    
    def create_emotion_overview_dashboard(self, df):
        """
        Create comprehensive emotion analysis dashboard.
        
        Parameters:
        - df (pd.DataFrame): DataFrame with 'emotion' column
        
        Returns:
        - str: Path to saved visualization
        """
        print("📊 Creating emotion overview dashboard...")
        
        fig, axes = plt.subplots(2, 3, figsize=(20, 12))
        fig.suptitle('Emotion Analysis Dashboard', fontsize=20, fontweight='bold', y=0.98)
        
        # 1. Emotion Distribution (Pie Chart)
        emotion_counts = df['emotion'].value_counts()
        colors = [self.emotion_colors.get(emotion, '#808080') for emotion in emotion_counts.index]
        
        wedges, texts, autotexts = axes[0, 0].pie(
            emotion_counts.values, 
            labels=emotion_counts.index,
            autopct='%1.1f%%',
            colors=colors,
            startangle=90
        )
        axes[0, 0].set_title('Emotion Distribution', fontweight='bold')
        
        # 2. Emotion Bar Chart with counts
        emotion_counts.plot(kind='bar', ax=axes[0, 1], color=colors)
        axes[0, 1].set_title('Emotion Frequencies', fontweight='bold')
        axes[0, 1].tick_params(axis='x', rotation=45)
        axes[0, 1].set_ylabel('Count')
        
        # Add count labels on bars
        for i, v in enumerate(emotion_counts.values):
            axes[0, 1].text(i, v + max(emotion_counts.values) * 0.01, f'{v:,}', 
                           ha='center', va='bottom', fontweight='bold')
        
        # 3. Emotion Percentages (Horizontal Bar)
        emotion_pct = (emotion_counts / len(df) * 100).sort_values()
        emotion_pct.plot(kind='barh', ax=axes[0, 2], 
                        color=[self.emotion_colors.get(emotion, '#808080') for emotion in emotion_pct.index])
        axes[0, 2].set_title('Emotion Percentages', fontweight='bold')
        axes[0, 2].set_xlabel('Percentage (%)')
        
        # 4. Topic Distribution (if available)
        if 'topic' in df.columns:
            topic_counts = df['topic'].value_counts().head(10)
            topic_counts.plot(kind='bar', ax=axes[1, 0], color='lightcoral')
            axes[1, 0].set_title('Top 10 Topics', fontweight='bold')
            axes[1, 0].tick_params(axis='x', rotation=45)
            axes[1, 0].set_ylabel('Count')
        else:
            axes[1, 0].text(0.5, 0.5, 'No Topic Data Available', 
                           ha='center', va='center', transform=axes[1, 0].transAxes)
        
        # 5. Emotion-Topic Heatmap (if available)
        if 'topic' in df.columns:
            # Create emotion-topic crosstab
            emotion_topic = pd.crosstab(df['emotion'], df['topic'])
            top_topics = emotion_topic.sum().nlargest(8).index
            subset = emotion_topic[top_topics]
            
            sns.heatmap(subset, annot=True, fmt='d', cmap='YlOrRd', 
                       ax=axes[1, 1], cbar_kws={'label': 'Count'})
            axes[1, 1].set_title('Emotion-Topic Correlation', fontweight='bold')
            axes[1, 1].set_xlabel('Topic')
            axes[1, 1].set_ylabel('Emotion')
        else:
            axes[1, 1].text(0.5, 0.5, 'No Topic Data Available', 
                           ha='center', va='center', transform=axes[1, 1].transAxes)
        
        # 6. Emotion Intensity Distribution
        if 'topic_probability' in df.columns:
            # Use topic probability as proxy for confidence/intensity
            for emotion in emotion_counts.head(5).index:
                emotion_data = df[df['emotion'] == emotion]['topic_probability']
                if len(emotion_data) > 0:
                    axes[1, 2].hist(emotion_data, alpha=0.7, label=emotion, bins=20,
                                   color=self.emotion_colors.get(emotion, '#808080'))
            
            axes[1, 2].set_title('Emotion Confidence Distribution', fontweight='bold')
            axes[1, 2].set_xlabel('Confidence Score')
            axes[1, 2].set_ylabel('Frequency')
            axes[1, 2].legend()
        else:
            # Alternative: emotion frequency by text length
            if 'text' in df.columns:
                df['text_length'] = df['text'].str.len()
                emotion_length = df.groupby('emotion')['text_length'].mean().sort_values(ascending=False)
                emotion_length.plot(kind='bar', ax=axes[1, 2], 
                                   color=[self.emotion_colors.get(emotion, '#808080') for emotion in emotion_length.index])
                axes[1, 2].set_title('Average Text Length by Emotion', fontweight='bold')
                axes[1, 2].set_ylabel('Average Length (characters)')
                axes[1, 2].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        output_path = self.output_folder / "emotion_overview_dashboard.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"✅ Emotion dashboard saved: {output_path}")
        return str(output_path)
    
    def create_temporal_emotion_analysis(self, df, date_column='date'):
        """
        Create temporal analysis of emotions over time.
        
        Parameters:
        - df (pd.DataFrame): DataFrame with emotion and date data
        - date_column (str): Name of date column
        """
        if date_column not in df.columns:
            print(f"⚠️  Date column '{date_column}' not found. Skipping temporal analysis.")
            return
        
        print("📅 Creating temporal emotion analysis...")
        
        # Prepare date data
        df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
        df_clean = df.dropna(subset=[date_column])
        
        if len(df_clean) == 0:
            print("⚠️  No valid dates found. Skipping temporal analysis.")
            return
        
        # Create time-based aggregations
        df_clean['year_month'] = df_clean[date_column].dt.to_period('M')
        df_clean['year'] = df_clean[date_column].dt.year
        df_clean['month'] = df_clean[date_column].dt.month
        
        # Create multiple temporal visualizations
        fig = plt.figure(figsize=(20, 16))
        
        # 1. Monthly emotion trends (line plot)
        plt.subplot(3, 2, 1)
        emotion_monthly