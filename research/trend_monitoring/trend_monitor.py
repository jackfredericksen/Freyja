"""
Freyja - AI-Powered Social Media Assistant - Trend Monitoring System
Monitors trending topics, hashtags, and conversations for content inspiration
"""

from pytrends.request import TrendReq
import requests
from bs4 import BeautifulSoup
import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from dataclasses import dataclass
from config import get_settings

settings = get_settings()

@dataclass
class TrendData:
    """Data structure for trend information"""
    keyword: str
    score: float
    source: str
    timestamp: datetime
    category: Optional[str] = None
    related_topics: List[str] = None

class TrendMonitor:
    """Main trend monitoring class"""
    
    def __init__(self):
        self.pytrends = TrendReq(hl='en-US', tz=360)
        self.logger = logging.getLogger(__name__)
        
    async def get_google_trends(self, timeframe: str = 'today 1-d') -> List[TrendData]:
        """
        Get trending topics from Google Trends
        
        Args:
            timeframe: Time period for trends (default: today 1-d)
            
        Returns:
            List of TrendData objects
        """
        try:
            # Get trending searches
            trending_searches = self.pytrends.trending_searches(pn='united_states')
            
            trends = []
            for i, keyword in enumerate(trending_searches[0][:settings.research.max_trends_per_check]):
                trend = TrendData(
                    keyword=keyword,
                    score=float(100 - i),  # Higher score for higher ranking
                    source='google_trends',
                    timestamp=datetime.now(),
                    category='general'
                )
                trends.append(trend)
                
            self.logger.info(f"Retrieved {len(trends)} trends from Google Trends")
            return trends
            
        except Exception as e:
            self.logger.error(f"Error fetching Google Trends: {e}")
            return []
    
    async def get_tech_trends(self) -> List[TrendData]:
        """Get technology-specific trending topics"""
        try:
            # Tech-focused keywords for trend analysis
            tech_keywords = [
                'artificial intelligence', 'machine learning', 'blockchain',
                'cryptocurrency', 'web3', 'metaverse', 'cloud computing',
                'cybersecurity', 'data science', 'automation'
            ]
            
            trends = []
            
            for keyword in tech_keywords:
                self.pytrends.build_payload([keyword], timeframe='today 1-d', geo='US')
                interest_over_time = self.pytrends.interest_over_time()
                
                if not interest_over_time.empty:
                    # Get latest score
                    latest_score = interest_over_time[keyword].iloc[-1]
                    
                    trend = TrendData(
                        keyword=keyword,
                        score=float(latest_score),
                        source='google_trends_tech',
                        timestamp=datetime.now(),
                        category='technology'
                    )
                    trends.append(trend)
                    
                # Add delay to respect rate limits
                await asyncio.sleep(1)
            
            self.logger.info(f"Retrieved {len(trends)} tech trends")
            return trends
            
        except Exception as e:
            self.logger.error(f"Error fetching tech trends: {e}")
            return []
    
    async def get_social_media_trends(self) -> List[TrendData]:
        """
        Get trending hashtags and topics from social media research
        Note: This uses public data sources, not direct X API access
        """
        try:
            trends = []
            
            # Simulate trending hashtags (in real implementation, 
            # you'd scrape from trend tracking websites)
            simulated_trends = [
                '#AI', '#MachineLearning', '#TechNews', '#Innovation',
                '#Productivity', '#RemoteWork', '#DigitalTransformation',
                '#Automation', '#DataScience', '#CloudComputing'
            ]
            
            for i, hashtag in enumerate(simulated_trends):
                trend = TrendData(
                    keyword=hashtag,
                    score=float(100 - i * 5),
                    source='social_media_research',
                    timestamp=datetime.now(),
                    category='hashtag'
                )
                trends.append(trend)
            
            self.logger.info(f"Retrieved {len(trends)} social media trends")
            return trends
            
        except Exception as e:
            self.logger.error(f"Error fetching social media trends: {e}")
            return []
    
    async def get_news_trends(self) -> List[TrendData]:
        """Get trending topics from news sources"""
        try:
            trends = []
            
            if not settings.research.news_api_key:
                self.logger.warning("News API key not configured")
                return trends
            
            # Use News API to get trending tech news
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                'apiKey': settings.research.news_api_key,
                'category': 'technology',
                'country': 'us',
                'pageSize': 20
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                news_data = response.json()
                
                for i, article in enumerate(news_data.get('articles', [])):
                    # Extract keywords from title
                    title_words = article['title'].split()
                    for word in title_words:
                        if len(word) > 4 and word.isalpha():  # Filter meaningful words
                            trend = TrendData(
                                keyword=word.lower(),
                                score=float(100 - i),
                                source='news_api',
                                timestamp=datetime.now(),
                                category='news'
                            )
                            trends.append(trend)
                            break  # One keyword per article for simplicity
            
            self.logger.info(f"Retrieved {len(trends)} news trends")
            return trends
            
        except Exception as e:
            self.logger.error(f"Error fetching news trends: {e}")
            return []
    
    async def get_all_trends(self) -> List[TrendData]:
        """Get trends from all sources"""
        all_trends = []
        
        # Gather trends from all sources concurrently
        trend_tasks = [
            self.get_google_trends(),
            self.get_tech_trends(),
            self.get_social_media_trends(),
            self.get_news_trends()
        ]
        
        trend_results = await asyncio.gather(*trend_tasks, return_exceptions=True)
        
        for result in trend_results:
            if isinstance(result, list):
                all_trends.extend(result)
            else:
                self.logger.error(f"Error in trend gathering: {result}")
        
        # Sort by score (highest first)
        all_trends.sort(key=lambda x: x.score, reverse=True)
        
        self.logger.info(f"Total trends collected: {len(all_trends)}")
        return all_trends
    
    def filter_trends_by_brand(self, trends: List[TrendData]) -> List[TrendData]:
        """Filter trends based on brand preferences"""
        filtered_trends = []
        
        for trend in trends:
            # Check if trend keyword matches preferred topics
            keyword_lower = trend.keyword.lower()
            
            # Skip if in avoid topics
            if any(avoid.lower() in keyword_lower for avoid in settings.brand.avoid_topics):
                continue
            
            # Prioritize if in preferred topics
            if any(pref.lower() in keyword_lower for pref in settings.brand.preferred_topics):
                trend.score += 20  # Boost score for preferred topics
            
            filtered_trends.append(trend)
        
        return filtered_trends
    
    def save_trends_to_file(self, trends: List[TrendData], filename: str = None):
        """Save trends to JSON file for later use"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"trends_{timestamp}.json"
        
        filepath = settings.data_dir / "raw" / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        trends_dict = []
        for trend in trends:
            trend_dict = {
                'keyword': trend.keyword,
                'score': trend.score,
                'source': trend.source,
                'timestamp': trend.timestamp.isoformat(),
                'category': trend.category,
                'related_topics': trend.related_topics
            }
            trends_dict.append(trend_dict)
        
        with open(filepath, 'w') as f:
            json.dump(trends_dict, f, indent=2)
        
        self.logger.info(f"Saved {len(trends)} trends to {filepath}")

# Usage example and main monitoring function
async def monitor_trends():
    """Main monitoring function"""
    monitor = TrendMonitor()
    
    # Get all trends
    trends = await monitor.get_all_trends()
    
    # Filter by brand preferences
    filtered_trends = monitor.filter_trends_by_brand(trends)
    
    # Save to file
    monitor.save_trends_to_file(filtered_trends)
    
    # Return top 10 trends for immediate use
    return filtered_trends[:10]

if __name__ == "__main__":
    # Run trend monitoring
    asyncio.run(monitor_trends())