# test_templates.py
from generation.content_templates.template_engine import TemplateEngine

def test_templates():
    engine = TemplateEngine()
    
    # Generate a tech insight tweet
    variables = {
        "insight_topic": "Python Programming",
        "main_point": "List comprehensions are faster than loops",
        "elaboration": "They're not just more readable, but also more efficient for creating lists.",
        "call_to_action": "What's your favorite Python optimization?",
        "hashtags": "#Python #Programming #Tips"
    }
    
    content = engine.generate_content("tech_insight", variables)
    print("Generated content:")
    print(content)

if __name__ == "__main__":
    test_templates()