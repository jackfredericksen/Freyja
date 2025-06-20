"""
Freyja - Content Templates System
Provides reusable templates for different types of social media content
"""

from jinja2 import Template, Environment, BaseLoader
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import json
import random
from pathlib import Path
from config import get_settings

settings = get_settings()

@dataclass
class ContentTemplate:
    """Structure for content templates"""
    id: str
    name: str
    category: str
    content_type: str  # tweet, thread, reply, quote_tweet
    template: str
    variables: List[str]
    tags: List[str] = field(default_factory=list)
    description: str = ""
    example: str = ""
    min_engagement_score: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)

class TemplateEngine:
    """Main template engine for content generation"""
    
    def __init__(self):
        self.templates: Dict[str, ContentTemplate] = {}
        self.jinja_env = Environment(loader=BaseLoader())
        self.load_default_templates()
    
    def load_default_templates(self):
        """Load default content templates"""
        
        # Tweet Templates
        self.add_template(ContentTemplate(
            id="tech_insight",
            name="Tech Insight",
            category="educational",
            content_type="tweet",
            template="🧠 {{ insight_topic }}: {{ main_point }}\n\n{{ elaboration }}\n\n{{ call_to_action }} {{ hashtags }}",
            variables=["insight_topic", "main_point", "elaboration", "call_to_action", "hashtags"],
            tags=["tech", "educational", "insight"],
            description="Share technical insights and knowledge",
            example="🧠 AI Development: Machine learning models learn patterns from data, not rules.\n\nThis means they can discover connections humans might miss, but they can also perpetuate biases present in training data.\n\nWhat's your experience with AI bias? #MachineLearning #AI #TechEthics"
        ))
        
        self.add_template(ContentTemplate(
            id="quick_tip",
            name="Quick Tip",
            category="educational",
            content_type="tweet",
            template="💡 Quick {{ tool_name }} tip:\n\n{{ tip_content }}\n\n{{ additional_context }}\n\n{{ hashtags }}",
            variables=["tool_name", "tip_content", "additional_context", "hashtags"],
            tags=["tips", "productivity", "tools"],
            description="Share quick tips and tricks",
            example="💡 Quick VS Code tip:\n\nUse Ctrl+Shift+P to open the command palette and access any feature instantly.\n\nThis single shortcut can replace dozens of menu clicks and boost your coding speed.\n\n#VSCode #ProductivityTips #CodingTips"
        ))
        
        self.add_template(ContentTemplate(
            id="question_engagement",
            name="Question for Engagement",
            category="engagement",
            content_type="tweet",
            template="{{ question }} 🤔\n\n{{ context }}\n\n{{ engagement_prompt }}\n\n{{ hashtags }}",
            variables=["question", "context", "engagement_prompt", "hashtags"],
            tags=["engagement", "question", "community"],
            description="Ask questions to drive engagement",
            example="What's the biggest productivity myth you've encountered? 🤔\n\nI've seen people obsess over the 'perfect' productivity system while ignoring the basics like sleep and focused work time.\n\nDrop your thoughts below! What productivity advice do you think is overrated?\n\n#Productivity #WorkLife #Efficiency"
        ))
        
        self.add_template(ContentTemplate(
            id="personal_story",
            name="Personal Story",
            category="personal",
            content_type="tweet",
            template="{{ story_opening }}\n\n{{ story_body }}\n\n{{ lesson_learned }}\n\n{{ hashtags }}",
            variables=["story_opening", "story_body", "lesson_learned", "hashtags"],
            tags=["personal", "story", "lessons"],
            description="Share personal experiences and lessons",
            example="Three months ago, I made a costly mistake in a client project.\n\nI assumed the client understood the technical limitations without explaining them clearly. The project scope crept, deadlines slipped, and stress levels skyrocketed.\n\nLesson: Over-communicate technical constraints upfront. It saves everyone time and stress.\n\n#LessonsLearned #ProjectManagement #Communication"
        ))
        
        # Thread Templates
        self.add_template(ContentTemplate(
            id="how_to_thread",
            name="How-To Thread",
            category="educational",
            content_type="thread",
            template="🧵 How to {{ main_topic }} ({{ step_count }} steps):\n\n1/ {{ introduction }}\n\n{% for step in steps %}{{ loop.index + 1 }}/ {{ step }}\n\n{% endfor %}{{ conclusion }}\n\n{{ hashtags }}",
            variables=["main_topic", "step_count", "introduction", "steps", "conclusion", "hashtags"],
            tags=["tutorial", "how-to", "thread", "educational"],
            description="Create step-by-step tutorial threads",
            example="🧵 How to set up a productive home office (5 steps):\n\n1/ First, choose a dedicated space. Even a corner of a room works better than working from your bed or couch.\n\n2/ Invest in proper lighting. Natural light is best, but a good desk lamp prevents eye strain during long work sessions.\n\n3/ Get an ergonomic chair and desk setup. Your back will thank you after 8-hour work days.\n\n4/ Minimize distractions. Keep your phone in another room and use website blockers during focused work time.\n\n5/ Add personal touches that motivate you. Plants, inspiring quotes, or photos can boost your mood and productivity.\n\nYour workspace impacts your mindset. Take time to create an environment that energizes and focuses you.\n\n#ProductivityTips #HomeOffice #WorkFromHome"
        ))
        
        self.add_template(ContentTemplate(
            id="list_thread",
            name="List Thread",
            category="educational",
            content_type="thread",
            template="🧵 {{ list_title }} ({{ item_count }} {{ item_type }}):\n\n{% for item in items %}{{ loop.index }}/ {{ item.title }}\n{{ item.description }}\n\n{% endfor %}{{ conclusion }}\n\n{{ hashtags }}",
            variables=["list_title", "item_count", "item_type", "items", "conclusion", "hashtags"],
            tags=["list", "resources", "thread", "curation"],
            description="Create curated list threads",
            example="🧵 Essential productivity tools for developers (5 tools):\n\n1/ Notion\nAll-in-one workspace for notes, tasks, and project management. Perfect for organizing your learning and side projects.\n\n2/ VS Code\nLightweight but powerful code editor with extensions for every language and workflow imaginable.\n\n3/ GitHub Copilot\nAI pair programmer that suggests code as you type. Speeds up development and helps you learn new patterns.\n\n4/ Toggl Track\nTime tracking app that shows where your hours actually go. Eye-opening for optimizing your schedule.\n\n5/ Alfred (Mac) / PowerToys (Windows)\nKeyboard shortcuts and automation tools that eliminate repetitive tasks.\n\nThe right tools won't make you productive overnight, but they can remove friction from your daily workflow.\n\n#ProductivityTools #DeveloperTools #CodingLife"
        ))
        
        # Reply Templates
        self.add_template(ContentTemplate(
            id="supportive_reply",
            name="Supportive Reply",
            category="engagement",
            content_type="reply",
            template="{{ supportive_opening }} {{ specific_acknowledgment }}\n\n{{ additional_insight }}\n\n{{ encouragement }}",
            variables=["supportive_opening", "specific_acknowledgment", "additional_insight", "encouragement"],
            tags=["support", "reply", "community"],
            description="Provide supportive replies to others' posts",
            example="This resonates so much! The struggle with impostor syndrome in tech is real, especially when you're constantly learning new technologies.\n\nI've found that keeping a 'wins journal' helps - writing down daily accomplishments, no matter how small, builds evidence against that inner critic.\n\nYou're doing better than you think. Keep pushing forward! 💪"
        ))
        
        self.add_template(ContentTemplate(
            id="helpful_reply",
            name="Helpful Reply",
            category="helpful",
            content_type="reply",
            template="{{ helpful_opening }}\n\n{{ main_advice }}\n\n{{ additional_resource }}",
            variables=["helpful_opening", "main_advice", "additional_resource"],
            tags=["helpful", "advice", "reply"],
            description="Provide helpful advice in replies",
            example="Great question! I've dealt with this exact issue.\n\nTry using environment variables for your API keys and a .env file for local development. Never commit secrets to your repo - use GitHub Secrets for CI/CD instead.\n\nHere's a helpful guide I bookmarked: [link]. The security section covers best practices for API key management."
        ))
        
        # Quote Tweet Templates
        self.add_template(ContentTemplate(
            id="agree_and_expand",
            name="Agree and Expand",
            category="engagement",
            content_type="quote_tweet",
            template="{{ agreement_statement }}\n\n{{ personal_experience }}\n\n{{ additional_insight }}\n\n{{ hashtags }}",
            variables=["agreement_statement", "personal_experience", "additional_insight", "hashtags"],
            tags=["quote", "agreement", "insight"],
            description="Quote tweet to agree and add your perspective",
            example="Absolutely this! 👆\n\nI learned this the hard way when I spent 3 months building a 'perfect' task management system instead of just... doing the tasks.\n\nSometimes the best productivity hack is just starting with pen and paper.\n\n#ProductivityTrap #KeepItSimple"
        ))
    
    def add_template(self, template: ContentTemplate):
        """Add a template to the engine"""
        self.templates[template.id] = template
    
    def get_template(self, template_id: str) -> Optional[ContentTemplate]:
        """Get a template by ID"""
        return self.templates.get(template_id)
    
    def get_templates_by_category(self, category: str) -> List[ContentTemplate]:
        """Get all templates in a category"""
        return [t for t in self.templates.values() if t.category == category]
    
    def get_templates_by_type(self, content_type: str) -> List[ContentTemplate]:
        """Get all templates of a specific content type"""
        return [t for t in self.templates.values() if t.content_type == content_type]
    
    def search_templates(self, query: str) -> List[ContentTemplate]:
        """Search templates by name, description, or tags"""
        query_lower = query.lower()
        results = []
        
        for template in self.templates.values():
            if (query_lower in template.name.lower() or 
                query_lower in template.description.lower() or 
                any(query_lower in tag.lower() for tag in template.tags)):
                results.append(template)
        
        return results
    
    def generate_content(self, template_id: str, variables: Dict[str, Any]) -> str:
        """Generate content using a template"""
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        # Validate required variables
        missing_vars = [var for var in template.variables if var not in variables]
        if missing_vars:
            raise ValueError(f"Missing required variables: {missing_vars}")
        
        # Render template
        jinja_template = self.jinja_env.from_string(template.template)
        return jinja_template.render(**variables)
    
    def suggest_template(self, content_type: str, category: str = None, tags: List[str] = None) -> ContentTemplate:
        """Suggest a template based on criteria"""
        candidates = self.get_templates_by_type(content_type)
        
        if category:
            candidates = [t for t in candidates if t.category == category]
        
        if tags:
            candidates = [t for t in candidates if any(tag in t.tags for tag in tags)]
        
        if not candidates:
            # Fallback to any template of the content type
            candidates = self.get_templates_by_type(content_type)
        
        return random.choice(candidates) if candidates else None
    
    def get_template_variables(self, template_id: str) -> List[str]:
        """Get required variables for a template"""
        template = self.get_template(template_id)
        return template.variables if template else []
    
    def preview_template(self, template_id: str) -> str:
        """Get template example or generate preview with placeholder data"""
        template = self.get_template(template_id)
        if not template:
            return "Template not found"
        
        if template.example:
            return template.example
        
        # Generate preview with placeholder data
        placeholder_vars = {var: f"[{var.upper()}]" for var in template.variables}
        try:
            return self.generate_content(template_id, placeholder_vars)
        except:
            return template.template
    
    def save_custom_template(self, template: ContentTemplate, filepath: str = None):
        """Save a custom template to file"""
        if filepath is None:
            filepath = settings.data_dir / "templates" / f"{template.id}.json"
        
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        template_dict = {
            "id": template.id,
            "name": template.name,
            "category": template.category,
            "content_type": template.content_type,
            "template": template.template,
            "variables": template.variables,
            "tags": template.tags,
            "description": template.description,
            "example": template.example,
            "min_engagement_score": template.min_engagement_score,
            "created_at": template.created_at.isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(template_dict, f, indent=2)
    
    def load_custom_templates(self, templates_dir: str = None):
        """Load custom templates from directory"""
        if templates_dir is None:
            templates_dir = settings.data_dir / "templates"
        
        templates_dir = Path(templates_dir)
        if not templates_dir.exists():
            return
        
        for template_file in templates_dir.glob("*.json"):
            try:
                with open(template_file, 'r') as f:
                    template_dict = json.load(f)
                
                template = ContentTemplate(
                    id=template_dict["id"],
                    name=template_dict["name"],
                    category=template_dict["category"],
                    content_type=template_dict["content_type"],
                    template=template_dict["template"],
                    variables=template_dict["variables"],
                    tags=template_dict.get("tags", []),
                    description=template_dict.get("description", ""),
                    example=template_dict.get("example", ""),
                    min_engagement_score=template_dict.get("min_engagement_score", 0.0),
                    created_at=datetime.fromisoformat(template_dict.get("created_at", datetime.now().isoformat()))
                )
                
                self.add_template(template)
                
            except Exception as e:
                print(f"Error loading template {template_file}: {e}")

# Template helper functions
def create_hashtag_string(hashtags: List[str], max_count: int = None) -> str:
    """Create hashtag string respecting brand limits"""
    if max_count is None:
        max_count = settings.brand.max_hashtags
    
    filtered_hashtags = hashtags[:max_count]
    return " ".join(f"#{tag.lstrip('#')}" for tag in filtered_hashtags)

def format_thread_content(thread_parts: List[str]) -> str:
    """Format content as a thread"""
    formatted_parts = []
    for i, part in enumerate(thread_parts, 1):
        if i == 1:
            formatted_parts.append(f"🧵 {part}")
        else:
            formatted_parts.append(f"{i}/ {part}")
    return "\n\n".join(formatted_parts)

def get_optimal_content_length(content_type: str) -> int:
    """Get optimal content length for different platforms"""
    lengths = {
        "tweet": 250,  # Leave room for hashtags
        "thread": 280,  # Per thread part
        "reply": 200,   # Shorter for replies
        "quote_tweet": 200  # Leave room for quoted content
    }
    return lengths.get(content_type, 250)

# Usage example
if __name__ == "__main__":
    engine = TemplateEngine()
    
    # Example: Generate a tech insight tweet
    variables = {
        "insight_topic": "API Design",
        "main_point": "Good APIs are like good jokes - they don't need explanation",
        "elaboration": "When developers need extensive documentation to understand basic functionality, your API needs simplification.",
        "call_to_action": "What's your API design pet peeve?",
        "hashtags": create_hashtag_string(["APIDesign", "DeveloperExperience", "TechTips"])
    }
    
    content = engine.generate_content("tech_insight", variables)
    print("Generated Content:")
    print(content)