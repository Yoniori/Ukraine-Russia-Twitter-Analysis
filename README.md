# Ukraine-Russia-Twitter-Analysis
# Twitter (X) Data Scraper System

Advanced Python-based scraping system for extracting comprehensive data from Twitter (X) including tweets, user timelines, and social network relationships.

**Input:** Twitter URLs, hashtags, user lists in Excel files  
**Output:** CSV files with complete tweet data and user network information

**Author:** Jonathan Uri  
**Date:** December 2024

## System Overview

This scraping system provides three main data collection modes:
1. **Hashtag Tweet Scraping** - Collect tweets containing specific hashtags within date ranges
2. **User Timeline Scraping** - Extract all tweets from specified user accounts
3. **Network Relationship Scraping** - Map follower/following relationships between users

## System Architecture

### Core Components

#### 1. `main.py` - Central Control System
**Input:** Configuration parameters, Excel files with usernames  
**Output:** Orchestrated scraping operations and CSV data files

Main entry point that coordinates all scraping operations:
- Manages different scraping modes (hashtags, users, networks)
- Handles Excel file reading for bulk user processing
- Generates timestamped output files
- Provides comprehensive logging and progress tracking

#### 2. `SearchScrapper.py` - Tweet Extraction Engine
**Input:** Twitter search URLs, hashtag queries, user timeline URLs  
**Output:** Tweet objects with complete metadata

Advanced tweet scraping with features:
- Comprehensive tweet data extraction (content, author, engagement metrics)
- Media URL extraction (images, videos)
- Hashtag and mention parsing
- Robust pagination handling
- Anti-detection measures

#### 3. `SearchScrapperDetails.py` - Network Analysis Engine  
**Input:** Twitter user profile URLs (following/followers pages)  
**Output:** UserDetail objects representing network connections

Specialized for social network mapping:
- Follower/following list extraction
- Verified follower identification
- Network overlap analysis
- Bulk relationship mapping

#### 4. `WebDriverSetup.py` - Browser Configuration
**Input:** Twitter login credentials  
**Output:** Configured and authenticated WebDriver instance

Handles browser setup and authentication:
- Automatic Chrome driver management
- Optimized browser settings for scraping
- Automated Twitter login flow
- Anti-detection configurations

## Data Structures

### Tweet Object
```python
Tweet(
    ID="1234567890",                    # Unique tweet identifier
    author="username",                  # Author username (no @)
    fullName="Display Name",            # Author's display name
    content="Tweet text content...",    # Full tweet text
    timestamp="2024-12-23T10:30:00Z",  # ISO format timestamp
    retweets="42",                      # Retweet count
    likes="156",                        # Like count
    comments="23",                      # Reply count
    views="1.2K",                       # View count
    hashtags=["#hashtag1", "#hashtag2"], # Extracted hashtags
    image_url="https://...",            # Image URL if present
    video_url="https://...",            # Video URL if present
    url="https://x.com/user/status/..."  # Direct tweet URL
)
```

### UserDetail Object
```python
UserDetail(
    author="username"                   # Clean username without @
)
```

## Usage Guide

### Installation Requirements

```bash
# Install required packages
pip install selenium pandas webdriver-manager openpyxl

# Chrome browser must be installed on system
```

### Configuration Setup

1. **Update Login Credentials** in `WebDriverSetup.py`:
```python
USERNAME = 'your_twitter_username'  # Replace with your username
PASSWORD = 'your_twitter_password'  # Replace with your password
```

2. **Prepare Excel File** for user lists (for modes 1 and 3):
```excel
| all_user_name |
|---------------|
| elonmusk      |
| twitter       |
| nasa          |
```

### Scraping Modes

#### Mode 0: Hashtag Tweet Scraping
**Input:** Hashtag list, date range  
**Output:** `{start_date}_to_{end_date}_hashtag_tweets.csv`

```python
# Configure in main.py
hashtags = ['ukraine', 'climate', 'ai']
start_date = "2024-01-01"
end_date = "2024-01-31"

# Run
python main.py  # Set side=0
```

#### Mode 1: User Timeline Scraping  
**Input:** Excel file with usernames, date range  
**Output:** `{start_date}_to_{end_date}_user_tweets.csv`

```python
# Configure paths in main.py
excel_file = "/path/to/usernames.xlsx"
username_column = "all_user_name"

# Run
python main.py  # Set side=1
```

#### Mode 3: Network Relationship Scraping
**Input:** Excel file with usernames  
**Output:** `user_follows_{timestamp}.csv`

```python
# Configure paths in main.py
excel_file = "/path/to/usernames.xlsx" 
username_column = "all_user_name"

# Run  
python main.py  # Set side=3
```

## Output Data Formats

### Tweet Data CSV Columns
```csv
id,text,username,fullname,url,publication_date,photo_url,video_url,
replies,retweets,likes,hashtags,views,target
```

### Network Data CSV Columns
```csv
target_username,other_username,type
```
Where `type` can be: `following`, `followers`, `verified_followers`

## Advanced Features

### Error Handling & Resilience
- Automatic retry mechanisms for failed requests
- Graceful handling of rate limits and blocks
- Comprehensive logging of errors and progress
- Safe handling of missing data elements

### Performance Optimizations
- Dynamic scrolling with intelligent wait times
- Duplicate detection and removal
- Memory-efficient processing for large datasets
- Configurable limits to prevent infinite scraping

### Anti-Detection Measures
- Randomized scroll patterns and delays
- Human-like interaction simulation
- User agent rotation
- Smart element waiting strategies

## Technical Considerations

### Rate Limiting
- Twitter implements aggressive rate limiting
- Built-in delays between requests (1-3 seconds)
- Automatic scaling of delays based on response times
- Respect for robots.txt and ToS

### Data Privacy & Ethics
- Only scrapes publicly available data
- Respects user privacy settings
- No collection of private/protected content
- Compliance with platform terms of service

### System Requirements
- **RAM:** Minimum 4GB (8GB+ recommended for large scrapes)
- **Storage:** Varies by dataset size (estimate 1MB per 1000 tweets)
- **Network:** Stable internet connection required
- **Browser:** Chrome browser must be installed

## Troubleshooting

### Common Issues

1. **Login Failures**
   - Verify credentials in `WebDriverSetup.py`
   - Check for 2FA requirements
   - Try manual login first to clear any security checks

2. **No Data Returned**
   - Verify target users/hashtags exist and are public
   - Check date ranges are reasonable
   - Ensure network connectivity

3. **Scraping Stops Early**
   - Twitter may be rate limiting
   - Increase delays between requests
   - Check for IP blocks

4. **Element Not Found Errors**
   - Twitter frequently updates their interface
   - May need to update CSS selectors
   - Check browser compatibility

### Performance Tuning

- **For faster scraping:** Enable headless mode
- **For large datasets:** Increase max_tweets limits gradually
- **For network analysis:** Process users in smaller batches
- **For reliability:** Add more conservative delays

## Legal & Ethical Usage

⚖️ **Important:** This tool is for research and educational purposes only. Users must:
- Comply with Twitter's Terms of Service
- Respect rate limits and platform policies
- Only collect publicly available data
- Follow applicable data protection laws (GDPR, CCPA, etc.)
- Use data responsibly and ethically

## Support & Development

For issues, improvements, or questions:
- Review the code comments for detailed implementation notes
- Check Twitter's current ToS for any updates
- Test with small datasets before large-scale scraping
- Monitor for changes in Twitter's interface structure

---

**Developer:** Jonathan Uri  
**Version:** 1.0  
**Last Updated:** December 2024  
**License:** Educational/Research Use Only
