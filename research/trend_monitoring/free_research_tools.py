"""
Free Research and Trend Monitoring Tools for Freyja
No paid APIs required - uses free sources and scraping
"""

import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json
import logging
from dataclasses import dataclass
import random
import time

logger = logging.getLogger(__name__)

@dataclass
class FreeTrendData:
    """Free trend data structure"""
    keyword: str
    score: float
    source: str
    timestamp: datetime
    category: Optional[str] = None
    url: Optional[str] = None

class FreeResearchTools:
    """Free research tools using public APIs and scraping"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    async def get_reddit_trends(self, subreddits: List[str] = None) -> List[FreeTrendData]:
        """Get trending topics from Reddit (free JSON API)"""
        if not subreddits:
            subreddits = ['technology', 'artificial', 'productivity', 'entrepreneur']
        
        trends = []
        
        for subreddit in subreddits:
            try:
                # Reddit's JSON API is free
                url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=10"
                
                response = self.session.get(url)
                if response.status_code == 200:
                    data = response.json()
                    
                    for post in data['data']['children']:
                        post_data = post['data']
                        
                        trend = FreeTrendData(
                            keyword=post_data['title'][:50],  # Truncate title
                            score=float(post_data['score']),
                            source=f"reddit_r_{subreddit}",
                            timestamp=datetime.now(),
                            category='reddit',
                            url=f"https://reddit.com{post_data['permalink']}"
                        )
                        trends.append(trend)
                
                # Be respectful to Reddit's servers
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error fetching Reddit trends from r/{subreddit}: {e}")
        
        return trends
    
    async def get_github_trending(self, language: str = "python") -> List[FreeTrendData]:
        """Get trending repositories from GitHub"""
        trends = []
        
        try:
            url = f"https://api.github.com/search/repositories?q=language:{language}&sort=stars&order=desc&per_page=10"
            
            response = self.session.get(url)
            if response.status_code == 200:
                data = response.json()
                
                for repo in data['items']:
                    trend = FreeTrendData(
                        keyword=repo['name'],
                        score=float(repo['stargazers_count']),
                        source="github_trending",
                        timestamp=datetime.now(),
                        category='github',
                        url=repo['html_url']
                    )
                    trends.append(trend)
            
        except Exception as e:
            logger.error(f"Error fetching GitHub trends: {e}")
        
        return trends
    
    async def get_hackernews_trends(self) -> List[FreeTrendData]:
        """Get trending stories from Hacker News"""
        trends = []
        
        try:
            # Get top stories IDs
            top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
            response = self.session.get(top_stories_url)
            
            if response.status_code == 200:
                story_ids = response.json()[:10]  # Top 10 stories
                
                for story_id in story_ids:
                    story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                    story_response = self.session.get(story_url)
                    
                    if story_response.status_code == 200:
                        story = story_response.json()
                        
                        if story and 'title' in story:
                            trend = FreeTrendData(
                                keyword=story['title'][:50],
                                score=float(story.get('score', 0)),
                                source="hackernews",
                                timestamp=datetime.now(),
                                category='tech_news',
                                url=story.get('url', f"https://news.ycombinator.com/item?id={story_id}")
                            )
                            trends.append(trend)
                    
                    time.sleep(0.1)  # Rate limiting
            
        except Exception as e:
            logger.error(f"Error fetching Hacker News trends: {e}")
        
        return trends
    
    async def get_producthunt_trends(self) -> List[FreeTrendData]:
        """Get trending products from Product Hunt"""
        trends = []
        
        try:
            # Product Hunt doesn't require API key for basic data
            url = "https://www.producthunt.com/"
            response = self.session.get(url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find product names (this is simplified - real implementation would need more robust scraping)
                products = soup.find_all('h3', limit=10)
                
                for i, product in enumerate(products):
                    if product.text.strip():
                        trend = FreeTrendData(
                            keyword=product.text.strip()[:30],
                            score=float(100 - i),  # Simple scoring
                            source="producthunt",
                            timestamp=datetime.now(),
                            category='products'
                        )
                        trends.append(trend)
            
        except Exception as e:
            logger.error(f"Error fetching Product Hunt trends: {e}")
        
        return trends
    
    async def get_google_trends_free(self) -> List[FreeTrendData]:
        """Get Google trends using pytrends (free)"""
        trends = []
        
        try:
            from pytrends.request import TrendReq
            
            pytrends = TrendReq(hl='en-US', tz=360)
            
            # Get trending searches
            trending_searches = pytrends.trending_searches(pn='united_states')
            
            for i, keyword in enumerate(trending_searches[0][:10]):
                trend = FreeTrendData(
                    keyword=keyword,
                    score=float(100 - i),
                    source="google_trends_free",
                    timestamp=datetime.now(),
                    category='general'
                )
                trends.append(trend)
            
        except Exception as e:
            logger.error(f"Error fetching Google Trends: {e}")
        
        return trends
    
    async def get_all_free_trends(self) -> List[FreeTrendData]:
        """Get trends from all free sources"""
        all_trends = []
        
        print("🔍 Gathering trends from free sources...")
        
        # Gather from all sources
        sources = [
            self.get_reddit_trends(),
            self.get_github_trending(),
            self.get_hackernews_trends(),
            self.get_google_trends_free(),
            # Skip Product Hunt for now (requires more robust scraping)
        ]
        
        for source_coro in sources:
            try:
                trends = await source_coro
                all_trends.extend(trends)
                print(f"✅ Retrieved {len(trends)} trends from {trends[0].source if trends else 'source'}")
            except Exception as e:
                print(f"⚠️  Failed to get trends from source: {e}")
        
        # Sort by score
        all_trends.sort(key=lambda x: x.score, reverse=True)
        
        return all_trends
    
    def filter_trends_by_relevance(self, trends: List[FreeTrendData], 
                                 relevant_keywords: List[str] = None) -> List[FreeTrendData]:
        """Filter trends by relevance to your brand"""
        if not relevant_keywords:
            from config import get_settings
            settings = get_settings()
            relevant_keywords = settings.brand.preferred_topics
        
        filtered_trends = []
        
        for trend in trends:
            keyword_lower = trend.keyword.lower()
            
            # Check if trend matches any relevant keywords
            is_relevant = any(
                keyword.lower() in keyword_lower 
                for keyword in relevant_keywords
            )
            
            if is_relevant:
                trend.score += 50  # Boost relevant trends
                filtered_trends.append(trend)
            elif random.random() < 0.3:  # Include 30% of other trends for diversity
                filtered_trends.append(trend)
        
        return filtered_trends
    
    def save_trends(self, trends: List[FreeTrendData], filename: str = None):
        """Save trends to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"free_trends_{timestamp}.json"
        
        from pathlib import Path
        filepath = Path("data/raw") / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        trends_data = []
        for trend in trends:
            trends_data.append({
                'keyword': trend.keyword,
                'score': trend.score,
                'source': trend.source,
                'timestamp': trend.timestamp.isoformat(),
                'category': trend.category,
                'url': trend.url
            })
        
        with open(filepath, 'w') as f:
            json.dump(trends_data, f, indent=2)
        
        print(f"💾 Saved {len(trends)} trends to {filepath}")

# Utility functions
async def monitor_free_trends():
    """Main function to monitor trends using free sources"""
    research = FreeResearchTools()
    
    print("🚀 Starting Free Trend Monitoring...")
    
    # Get all trends
    trends = await research.get_all_free_trends()
    
    # Filter by relevance
    filtered_trends = research.filter_trends_by_relevance(trends)
    
    # Save results
    research.save_trends(filtered_trends)
    
    print(f"\n📊 Summary:")
    print(f"Total trends found: {len(trends)}")
    print(f"Relevant trends: {len(filtered_trends)}")
    
    print(f"\n🔥 Top 5 Trends:")
    for i, trend in enumerate(filtered_trends[:5], 1):
        print(f"{i}. {trend.keyword[:40]} (Score: {trend.score:.1f}) - {trend.source}")
    
    return filtered_trends

# Test function
async def test_free_research():
    """Test the free research tools"""
    try:
        print("🧪 Testing Free Research Tools...")
        
        research = FreeResearchTools()
        
        # Test Reddit trends
        reddit_trends = await research.get_reddit_trends(['technology'])
        print(f"✅ Reddit trends: {len(reddit_trends)}")
        
        # Test GitHub trends  
        github_trends = await research.get_github_trending()
        print(f"✅ GitHub trends: {len(github_trends)}")
        
        # Test Hacker News
        hn_trends = await research.get_hackernews_trends()
        print(f"✅ Hacker News trends: {len(hn_trends)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Free research test failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(monitor_free_trends())