#!/usr/bin/env python3
"""
Simple Social Media Publisher
Focused only on posting content to Facebook and Instagram
"""

import os
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

class SimpleSocialPublisher:
    """Simple publisher for Facebook and Instagram posts"""
    
    def __init__(self):
        self.brands = {
            'powernow': {
                'name': 'PowerNow Asia',
                'facebook_token': os.environ.get('POWERNOW_FB_TOKEN', ''),
                'instagram_token': os.environ.get('POWERNOW_IG_TOKEN', ''),
                'page_id': os.environ.get('POWERNOW_FB_PAGE_ID', ''),
                'instagram_id': os.environ.get('POWERNOW_IG_ID', ''),
                'content_themes': [
                    'energy_saving_tips',
                    'solar_success_stories',
                    'customer_testimonials',
                    'industry_news',
                    'weekend_specials'
                ]
            },
            'lee1healthcare': {
                'name': 'Lee1 Healthcare',
                'facebook_token': os.environ.get('LEE1_FB_TOKEN', ''),
                'instagram_token': os.environ.get('LEE1_IG_TOKEN', ''),
                'page_id': os.environ.get('LEE1_FB_PAGE_ID', ''),
                'instagram_id': os.environ.get('LEE1_IG_ID', ''),
                'content_themes': [
                    'health_tips',
                    'specialist_intros',
                    'preventive_care',
                    'medical_equipment',
                    'patient_stories'
                ]
            }
        }
        
        self.content_library = self.load_content_library()
        self.scheduled_posts = []
        
    def load_content_library(self) -> Dict:
        """Load content library from JSON file"""
        lib_path = Path(__file__).parent / 'content' / 'content_library.json'
        if lib_path.exists():
            with open(lib_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'powernow': [], 'lee1healthcare': []}
    
    def save_content_library(self):
        """Save content library to file"""
        lib_path = Path(__file__).parent / 'content' / 'content_library.json'
        lib_path.parent.mkdir(exist_ok=True)
        with open(lib_path, 'w', encoding='utf-8') as f:
            json.dump(self.content_library, f, indent=2, ensure_ascii=False)
    
    def add_content(self, brand: str, content_type: str, text: str, image_path: Optional[str] = None):
        """Add content to library"""
        if brand not in self.content_library:
            self.content_library[brand] = []
        
        content_item = {
            'id': len(self.content_library[brand]) + 1,
            'type': content_type,
            'text': text,
            'image_path': image_path,
            'created_at': datetime.now().isoformat(),
            'used': False,
            'platforms_used': []
        }
        
        self.content_library[brand].append(content_item)
        self.save_content_library()
        print(f"✅ Added content to {brand} library (ID: {content_item['id']})")
        return content_item['id']
    
    def get_unused_content(self, brand: str, content_type: Optional[str] = None) -> List[Dict]:
        """Get unused content from library"""
        if brand not in self.content_library:
            return []
        
        unused = [c for c in self.content_library[brand] if not c['used']]
        if content_type:
            unused = [c for c in unused if c['type'] == content_type]
        
        return unused
    
    def post_to_facebook(self, brand: str, message: str, image_url: Optional[str] = None) -> bool:
        """Post to Facebook page"""
        brand_config = self.brands.get(brand)
        if not brand_config or not brand_config['facebook_token']:
            print(f"❌ {brand_config['name']}: Facebook token not configured")
            return False
        
        try:
            if image_url:
                # Post with photo
                url = f"https://graph.facebook.com/v20.0/{brand_config['page_id']}/photos"
                params = {
                    'access_token': brand_config['facebook_token'],
                    'message': message,
                    'url': image_url
                }
            else:
                # Post without photo
                url = f"https://graph.facebook.com/v20.0/{brand_config['page_id']}/feed"
                params = {
                    'access_token': brand_config['facebook_token'],
                    'message': message
                }
            
            response = requests.post(url, data=params, timeout=30)
            if response.status_code == 200:
                post_id = response.json().get('id', '')
                print(f"✅ Posted to {brand_config['name']} Facebook")
                print(f"   Post ID: {post_id}")
                print(f"   Message: {message[:100]}...")
                return True
            else:
                print(f"❌ Error posting to Facebook: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error posting to Facebook: {e}")
            return False
    
    def post_to_instagram(self, brand: str, caption: str, image_url: str) -> bool:
        """Post to Instagram (requires image)"""
        brand_config = self.brands.get(brand)
        if not brand_config or not brand_config['instagram_token']:
            print(f"❌ {brand_config['name']}: Instagram token not configured")
            return False
        
        try:
            # Step 1: Create media container
            create_url = f"https://graph.facebook.com/v20.0/{brand_config['instagram_id']}/media"
            create_params = {
                'access_token': brand_config['instagram_token'],
                'caption': caption,
                'image_url': image_url
            }
            
            create_response = requests.post(create_url, data=create_params, timeout=30)
            if create_response.status_code == 200:
                media_id = create_response.json().get('id')
                
                # Step 2: Publish the media
                publish_url = f"https://graph.facebook.com/v20.0/{brand_config['instagram_id']}/media_publish"
                publish_params = {
                    'access_token': brand_config['instagram_token'],
                    'creation_id': media_id
                }
                
                publish_response = requests.post(publish_url, data=publish_params, timeout=30)
                if publish_response.status_code == 200:
                    print(f"✅ Posted to {brand_config['name']} Instagram")
                    print(f"   Media ID: {media_id}")
                    print(f"   Caption: {caption[:100]}...")
                    return True
                else:
                    print(f"❌ Error publishing to Instagram: {publish_response.status_code}")
                    print(f"   Response: {publish_response.text}")
                    return False
            else:
                print(f"❌ Error creating Instagram media: {create_response.status_code}")
                print(f"   Response: {create_response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error posting to Instagram: {e}")
            return False
    
    def cross_post(self, brand: str, message: str, image_url: Optional[str] = None):
        """Post to both Facebook and Instagram"""
        print(f"\n🔄 Cross-posting for {self.brands[brand]['name']}")
        print("-" * 50)
        
        results = {
            'facebook': False,
            'instagram': False
        }
        
        # Post to Facebook
        if image_url:
            results['facebook'] = self.post_to_facebook(brand, message, image_url)
        else:
            results['facebook'] = self.post_to_facebook(brand, message)
        
        # Post to Instagram (requires image)
        if image_url:
            results['instagram'] = self.post_to_instagram(brand, message, image_url)
        else:
            print("⚠️ Instagram post skipped (requires image)")
        
        print("-" * 50)
        print(f"📊 Results: Facebook: {'✅' if results['facebook'] else '❌'}, "
              f"Instagram: {'✅' if results['instagram'] else '❌'}")
        
        return results
    
    def schedule_post(self, brand: str, platform: str, message: str, 
                     image_url: Optional[str], post_time: datetime):
        """Schedule a post for future"""
        scheduled_post = {
            'id': len(self.scheduled_posts) + 1,
            'brand': brand,
            'platform': platform,
            'message': message,
            'image_url': image_url,
            'scheduled_time': post_time.isoformat(),
            'status': 'scheduled'
        }
        
        self.scheduled_posts.append(scheduled_post)
        print(f"✅ Scheduled post #{scheduled_post['id']} for {post_time}")
        return scheduled_post['id']
    
    def post_now_from_library(self, brand: str, content_type: Optional[str] = None):
        """Post unused content from library"""
        unused_content = self.get_unused_content(brand, content_type)
        
        if not unused_content:
            print(f"❌ No unused content found for {brand}")
            return False
        
        # Get first unused content
        content = unused_content[0]
        
        print(f"\n📝 Posting from {brand} content library")
        print(f"   Content ID: {content['id']}")
        print(f"   Type: {content['type']}")
        print(f"   Text: {content['text'][:100]}...")
        
        # Mark as used
        content['used'] = True
        self.save_content_library()
        
        # Post to both platforms
        image_url = f"file://{content['image_path']}" if content['image_path'] else None
        return self.cross_post(brand, content['text'], image_url)
    
    def generate_daily_content(self, brand: str):
        """Generate content for today based on theme"""
        brand_config = self.brands.get(brand)
        if not brand_config:
            return None
        
        # Get day of week
        day_index = datetime.now().weekday()  # 0=Monday, 6=Sunday
        themes = brand_config['content_themes']
        theme = themes[day_index % len(themes)]
        
        if brand == 'powernow':
            content_templates = {
                'energy_saving_tips': [
                    "💡 Energy Saving Tip of the Day!",
                    "Did you know? Switching to LED bulbs can save up to 80% on lighting costs!",
                    "Tip: Unplug devices when not in use to reduce phantom energy consumption.",
                    "Save energy, save money! 💰"
                ],
                'solar_success_stories': [
                    "☀️ Solar Success Story!",
                    "Mr. Tan from Subang Jaya reduced his electricity bill by 70% with our solar installation!",
                    "Contact us for your own solar success story!",
                    "#SolarPower #RenewableEnergy"
                ],
                'customer_testimonials': [
                    "🌟 Customer Testimonial",
                    "\"PowerNow Asia transformed our energy consumption! Highly recommended!\" - Sarah L.",
                    "Thank you for trusting us with your energy needs!",
                    "#HappyCustomer #EnergySolutions"
                ],
                'industry_news': [
                    "📰 Energy Industry Update",
                    "Malaysia aims for 31% renewable energy by 2025!",
                    "Stay ahead with the latest energy trends and solutions.",
                    "#RenewableEnergy #Malaysia"
                ],
                'weekend_specials': [
                    "🎉 Weekend Special!",
                    "Book a free energy audit this weekend and get 10% off solar installation!",
                    "Limited slots available. Contact us now!",
                    "#WeekendSpecial #EnergyAudit"
                ]
            }
        else:  # lee1healthcare
            content_templates = {
                'health_tips': [
                    "🏥 Health Tip of the Day!",
                    "Stay hydrated! Drink at least 8 glasses of water daily for optimal health.",
                    "Remember: Prevention is better than cure!",
                    "#HealthTips #Wellness"
                ],
                'specialist_intros': [
                    "👨‍⚕️ Meet Our Specialist",
                    "Dr. Lim specializes in cardiology with 15 years of experience.",
                    "Book your consultation today for expert care!",
                    "#Cardiology #Healthcare"
                ],
                'preventive_care': [
                    "🛡️ Preventive Care Matters",
                    "Regular health screenings can detect issues early and save lives!",
                    "Schedule your annual check-up with us.",
                    "#PreventiveCare #HealthCheck"
                ],
                'medical_equipment': [
                    "⚕️ Advanced Medical Equipment",
                    "Our clinic features state-of-the-art diagnostic equipment for accurate results.",
                    "Your health deserves the best technology!",
                    "#MedicalTechnology #Healthcare"
                ],
                'patient_stories': [
                    "❤️ Patient Success Story",
                    "\"The care I received at Lee1 Healthcare was exceptional!\" - Mr. Wong",
                    "We're committed to your health and wellbeing.",
                    "#PatientCare #SuccessStory"
                ]
            }
        
        template = content_templates.get(theme, content_templates[list(content_templates.keys())[0]])
        message = "\n".join(template)
        
        return {
            'theme': theme,
            'message': message,
            'hashtags': template[-1] if '#' in template[-1] else ''
        }
    
    def run_daily_schedule(self):
        """Run daily posting schedule"""
        print("\n📅 Running daily posting schedule")
        print("=" * 50)
        
        posting_times = [
            ('09:00', 'Morning post'),
            ('13:00', 'Afternoon post'),
            ('17:00', 'Evening post')
        ]
        
        for post_time, description in posting_times:
            print(f"\n⏰ {description} ({post_time})")
            print("-" * 30)
            
            # Post for PowerNow Asia
            powernow_content = self.generate_daily_content('powernow')
            if powernow_content:
                print(f"🏢 PowerNow Asia: {powernow_content['theme']}")
                # In real implementation, would post here
                # self.cross_post('powernow', powernow_content['message'])
            
            # Post for Lee1 Healthcare
            lee1_content = self.generate_daily_content('lee1healthcare')
            if lee1_content:
                print(f"🏥 Lee1 Healthcare: {lee1_content['theme']}")
                # In real implementation, would post here
                # self.cross_post('lee1healthcare', lee1_content['message'])
        
        print("\n" + "=" * 50)
        print("✅ Daily schedule completed")
    
    def show_status(self):
        """Show publisher status"""
        print("\n📊 Social Media Publisher Status")
        print("=" * 50)
        
        for brand_key, brand_info in self.brands.items():
            print(f"\n{brand_info['name']}:")
            print(f"  Facebook: {'✅ Configured' if brand_info['facebook_token'] else '❌ Not configured'}")
            print(f"  Instagram: {'✅ Configured' if brand_info['instagram_token'] else '❌ Not configured'}")
            
            # Content library stats
            brand_content = self.content_library.get(brand_key, [])
            total = len(brand_content)
            unused = len([c for c in brand_content if not c['used']])
            print(f"  Content Library: {unused}/{total} unused")
        
        print(f"\n📅 Scheduled posts: {len(self.scheduled_posts)}")
        print(f"⏰ Next run: Daily at 09:00, 13:00, 17:00")

def main():
    """Main function"""
    publisher = SimpleSocialPublisher()
    
    print("🚀 Simple Social Media Publisher")
    print("=" * 50)
    
    # Show status
    publisher.show_status()
    
    # Test content generation
    print("\n🧪 Testing content generation:")
    print("-" * 30)
    
    powernow_content = publisher.generate_daily_content('powernow')
    if powernow_content:
        print(f"🏢 PowerNow Asia ({powernow_content['theme']}):")
        print(powernow_content['message'])
    
    print()
    
    lee1_content = publisher.generate_daily_content('lee1healthcare')
    if lee1_content:
        print(f"🏥 Lee1 Healthcare ({lee1_content['theme']}):")
        print(lee1_content['message'])
    
    print("\n" + "=" * 50)
    print("📋 Available commands:")
    print("  python simple_social_publisher.py --status    # Show status")
    print("  python simple_social_publisher.py --schedule  # Run daily schedule")
    print("  python simple_social_publisher.py --add       # Add content to library")
    print("  python simple_social_publisher.py --post      # Post from library")

if __name__ == "__main__":
    import sys
    
    publisher = SimpleSocialPublisher()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--status":
            publisher.show_status()
        elif sys.argv[1] == "--schedule":
            publisher.run_daily_schedule()
        elif sys.argv[1] == "--add":
            # Example: Add content
            brand = input("Brand (powernow/lee1healthcare): ")
            content_type = input("Content type: ")
            text = input("Content text: ")
            image_path = input("Image path (optional): ") or None
            publisher.add_content(brand, content_type, text, image_path)
        elif sys.argv[1] == "--post":
            brand = input("Brand (powernow/lee1healthcare): ")
            publisher.post_now_from_library(brand)
        else:
            print(f"Unknown command: {sys.argv[1]}")
            print("Available: --status, --schedule, --add, --post")
    else:
        main()