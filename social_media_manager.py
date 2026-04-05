#!/usr/bin/env python3
"""
Social Media Manager for PowerNow Asia & Lee1 Healthcare
Manages Facebook and Instagram integration
"""

import os
import json
import time
import requests
from datetime import datetime
from typing import Dict, List, Optional

class SocialMediaManager:
    """Manage Facebook and Instagram accounts for multiple brands"""
    
    def __init__(self):
        self.config = self.load_config()
        self.brands = {
            'powernow': {
                'name': 'PowerNow Asia',
                'facebook_page_id': os.environ.get('POWERNOW_FB_PAGE_ID', ''),
                'facebook_token': os.environ.get('POWERNOW_FB_TOKEN', ''),
                'instagram_id': os.environ.get('POWERNOW_IG_ID', ''),
                'instagram_token': os.environ.get('POWERNOW_IG_TOKEN', ''),
                'business_type': 'energy_solutions'
            },
            'lee1healthcare': {
                'name': 'Lee1 Healthcare',
                'facebook_page_id': os.environ.get('LEE1_FB_PAGE_ID', ''),
                'facebook_token': os.environ.get('LEE1_FB_TOKEN', ''),
                'instagram_id': os.environ.get('LEE1_IG_ID', ''),
                'instagram_token': os.environ.get('LEE1_IG_TOKEN', ''),
                'business_type': 'healthcare'
            }
        }
        
    def load_config(self) -> Dict:
        """Load configuration from file or environment"""
        config_path = os.path.join(os.path.dirname(__file__), 'config', 'social_media.json')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        return {}
    
    def save_config(self):
        """Save configuration to file"""
        config_path = os.path.join(os.path.dirname(__file__), 'config', 'social_media.json')
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def test_facebook_connection(self, brand: str) -> bool:
        """Test Facebook API connection"""
        brand_config = self.brands.get(brand)
        if not brand_config or not brand_config['facebook_token']:
            print(f"❌ {brand_config['name']}: Facebook token not configured")
            return False
        
        try:
            url = f"https://graph.facebook.com/v20.0/{brand_config['facebook_page_id']}"
            params = {
                'access_token': brand_config['facebook_token'],
                'fields': 'id,name,fan_count'
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {brand_config['name']} Facebook: Connected")
                print(f"   Page: {data.get('name')}")
                print(f"   Followers: {data.get('fan_count', 'N/A')}")
                return True
            else:
                print(f"❌ {brand_config['name']} Facebook: Error {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ {brand_config['name']} Facebook: Connection error - {e}")
            return False
    
    def test_instagram_connection(self, brand: str) -> bool:
        """Test Instagram API connection"""
        brand_config = self.brands.get(brand)
        if not brand_config or not brand_config['instagram_token']:
            print(f"❌ {brand_config['name']}: Instagram token not configured")
            return False
        
        try:
            url = f"https://graph.facebook.com/v20.0/{brand_config['instagram_id']}"
            params = {
                'access_token': brand_config['instagram_token'],
                'fields': 'id,username,media_count,followers_count'
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {brand_config['name']} Instagram: Connected")
                print(f"   Username: {data.get('username')}")
                print(f"   Followers: {data.get('followers_count', 'N/A')}")
                print(f"   Media: {data.get('media_count', 'N/A')}")
                return True
            else:
                print(f"❌ {brand_config['name']} Instagram: Error {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ {brand_config['name']} Instagram: Connection error - {e}")
            return False
    
    def get_page_comments(self, brand: str, limit: int = 10) -> List[Dict]:
        """Get recent comments from Facebook page"""
        brand_config = self.brands.get(brand)
        if not brand_config or not brand_config['facebook_token']:
            return []
        
        try:
            url = f"https://graph.facebook.com/v20.0/{brand_config['facebook_page_id']}/feed"
            params = {
                'access_token': brand_config['facebook_token'],
                'fields': 'comments.limit(5){message,from,created_time}',
                'limit': limit
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                comments = []
                for post in data.get('data', []):
                    if 'comments' in post:
                        for comment in post['comments']['data']:
                            comments.append({
                                'brand': brand_config['name'],
                                'platform': 'facebook',
                                'message': comment.get('message', ''),
                                'from': comment.get('from', {}).get('name', 'Unknown'),
                                'created_time': comment.get('created_time', ''),
                                'post_id': post.get('id', '')
                            })
                return comments
        except Exception as e:
            print(f"❌ Error getting comments: {e}")
        
        return []
    
    def get_instagram_comments(self, brand: str, limit: int = 10) -> List[Dict]:
        """Get recent comments from Instagram"""
        brand_config = self.brands.get(brand)
        if not brand_config or not brand_config['instagram_token']:
            return []
        
        try:
            # Get recent media
            url = f"https://graph.facebook.com/v20.0/{brand_config['instagram_id']}/media"
            params = {
                'access_token': brand_config['instagram_token'],
                'fields': 'id,caption,comments_count',
                'limit': limit
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                comments = []
                for media in data.get('data', []):
                    media_id = media.get('id')
                    # Get comments for this media
                    comments_url = f"https://graph.facebook.com/v20.0/{media_id}/comments"
                    comments_params = {
                        'access_token': brand_config['instagram_token'],
                        'fields': 'text,username,timestamp',
                        'limit': 5
                    }
                    
                    comments_response = requests.get(comments_url, params=comments_params, timeout=10)
                    if comments_response.status_code == 200:
                        comments_data = comments_response.json()
                        for comment in comments_data.get('data', []):
                            comments.append({
                                'brand': brand_config['name'],
                                'platform': 'instagram',
                                'message': comment.get('text', ''),
                                'from': comment.get('username', 'Unknown'),
                                'created_time': comment.get('timestamp', ''),
                                'media_id': media_id
                            })
                return comments
        except Exception as e:
            print(f"❌ Error getting Instagram comments: {e}")
        
        return []
    
    def reply_to_comment(self, brand: str, platform: str, comment_id: str, message: str) -> bool:
        """Reply to a comment on Facebook or Instagram"""
        brand_config = self.brands.get(brand)
        if not brand_config:
            return False
        
        try:
            if platform == 'facebook':
                token = brand_config['facebook_token']
                url = f"https://graph.facebook.com/v20.0/{comment_id}/comments"
            elif platform == 'instagram':
                token = brand_config['instagram_token']
                url = f"https://graph.facebook.com/v20.0/{comment_id}/replies"
            else:
                return False
            
            params = {
                'access_token': token,
                'message': message
            }
            
            response = requests.post(url, data=params, timeout=10)
            if response.status_code == 200:
                print(f"✅ Reply sent to {platform} comment")
                return True
            else:
                print(f"❌ Error replying: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending reply: {e}")
            return False
    
    def post_to_facebook(self, brand: str, message: str, link: Optional[str] = None) -> bool:
        """Post to Facebook page"""
        brand_config = self.brands.get(brand)
        if not brand_config or not brand_config['facebook_token']:
            return False
        
        try:
            url = f"https://graph.facebook.com/v20.0/{brand_config['facebook_page_id']}/feed"
            params = {
                'access_token': brand_config['facebook_token'],
                'message': message
            }
            
            if link:
                params['link'] = link
            
            response = requests.post(url, data=params, timeout=10)
            if response.status_code == 200:
                print(f"✅ Posted to {brand_config['name']} Facebook")
                return True
            else:
                print(f"❌ Error posting: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error posting to Facebook: {e}")
            return False
    
    def post_to_instagram(self, brand: str, caption: str, image_url: Optional[str] = None) -> bool:
        """Post to Instagram (requires image)"""
        brand_config = self.brands.get(brand)
        if not brand_config or not brand_config['instagram_token']:
            return False
        
        try:
            # For Instagram, we need to create a media container first
            if image_url:
                # Step 1: Create media container
                create_url = f"https://graph.facebook.com/v20.0/{brand_config['instagram_id']}/media"
                create_params = {
                    'access_token': brand_config['instagram_token'],
                    'caption': caption,
                    'image_url': image_url
                }
                
                create_response = requests.post(create_url, data=create_params, timeout=10)
                if create_response.status_code == 200:
                    media_id = create_response.json().get('id')
                    
                    # Step 2: Publish the media
                    publish_url = f"https://graph.facebook.com/v20.0/{brand_config['instagram_id']}/media_publish"
                    publish_params = {
                        'access_token': brand_config['instagram_token'],
                        'creation_id': media_id
                    }
                    
                    publish_response = requests.post(publish_url, data=publish_params, timeout=10)
                    if publish_response.status_code == 200:
                        print(f"✅ Posted to {brand_config['name']} Instagram")
                        return True
                    else:
                        print(f"❌ Error publishing: {publish_response.status_code} - {publish_response.text}")
                        return False
                else:
                    print(f"❌ Error creating media: {create_response.status_code} - {create_response.text}")
                    return False
            else:
                print("❌ Instagram posts require an image")
                return False
                
        except Exception as e:
            print(f"❌ Error posting to Instagram: {e}")
            return False
    
    def generate_auto_reply(self, brand: str, message: str) -> str:
        """Generate automatic reply based on message content"""
        brand_config = self.brands.get(brand)
        if not brand_config:
            return "Thank you for your message. Our team will respond shortly."
        
        message_lower = message.lower()
        
        if brand == 'powernow':
            # PowerNow Asia responses
            if any(word in message_lower for word in ['price', 'cost', 'fee', 'how much']):
                return "Thank you for your interest in PowerNow Asia! Pricing depends on your specific energy needs. Please provide your location and average monthly usage for a detailed quote."
            
            elif any(word in message_lower for word in ['install', 'installation', 'setup', 'how long']):
                return "Standard installation takes 3-5 business days after site assessment. Our technician will visit to evaluate your location and provide exact timeline."
            
            elif any(word in message_lower for word in ['solar', 'renewable', 'green energy']):
                return "We specialize in solar and renewable energy solutions! Our systems can reduce your electricity bills by up to 70%. Would you like to schedule a free consultation?"
            
            elif any(word in message_lower for word in ['contact', 'phone', 'email', 'address']):
                return "You can reach us at:\n📞 +603-1234 5678\n📧 info@powernow.asia\n📍 Kuala Lumpur, Malaysia\n\nOur team is available Mon-Fri 9AM-6PM."
        
        elif brand == 'lee1healthcare':
            # Lee1 Healthcare responses
            if any(word in message_lower for word in ['appointment', 'booking', 'schedule', 'visit']):
                return "To book an appointment, please provide:\n1. Your full name\n2. Contact number\n3. Preferred date/time\n4. Type of consultation needed\n\nWe'll confirm within 24 hours."
            
            elif any(word in message_lower for word in ['price', 'cost', 'fee', 'how much']):
                return "Consultation fees start from RM50. Specific treatment costs depend on the service required. Please let us know what service you're interested in for accurate pricing."
            
            elif any(word in message_lower for word in ['doctor', 'specialist', 'expert']):
                return "We have specialists in:\n• General Medicine\n• Pediatrics\n• Cardiology\n• Dermatology\n• Orthopedics\n\nWhich specialist would you like to consult?"
            
            elif any(word in message_lower for word in ['opening', 'hours', 'time', 'when open']):
                return "Our clinic hours:\nMon-Fri: 8:30AM - 8:00PM\nSat: 9:00AM - 5:00PM\nSun: 10:00AM - 2:00PM\n\nEmergency services available 24/7."
        
        # Default response
        return f"Thank you for contacting {brand_config['name']}! We've received your message and will respond within 24 hours. For urgent matters, please call our hotline."
    
    def monitor_comments(self):
        """Monitor and auto-reply to comments"""
        print("🔍 Monitoring social media comments...")
        
        all_comments = []
        
        # Get comments from both brands
        for brand in ['powernow', 'lee1healthcare']:
            fb_comments = self.get_page_comments(brand, limit=5)
            ig_comments = self.get_instagram_comments(brand, limit=5)
            all_comments.extend(fb_comments)
            all_comments.extend(ig_comments)
        
        # Process comments
        for comment in all_comments:
            print(f"\n📝 New comment from {comment['from']} on {comment['platform']}:")
            print(f"   Brand: {comment['brand']}")
            print(f"   Message: {comment['message'][:100]}...")
            
            # Generate auto-reply
            reply = self.generate_auto_reply(
                'powernow' if 'PowerNow' in comment['brand'] else 'lee1healthcare',
                comment['message']
            )
            
            print(f"   Auto-reply: {reply[:100]}...")
            
            # Ask if should reply (in real system, this would be automated)
            # For now, just show what would be sent
            
            # Uncomment to auto-reply:
            # if comment['platform'] == 'facebook':
            #     self.reply_to_comment(brand, 'facebook', comment['post_id'], reply)
            # elif comment['platform'] == 'instagram':
            #     self.reply_to_comment(brand, 'instagram', comment['media_id'], reply)
        
        return len(all_comments)
    
    def run_monitor(self, interval_minutes: int = 5):
        """Run continuous monitoring"""
        print("🚀 Starting Social Media Monitor")
        print(f"📊 Monitoring: PowerNow Asia & Lee1 Healthcare")
        print(f"📱 Platforms: Facebook & Instagram")
        print(f"⏰ Check interval: {interval_minutes} minutes")
        print("-" * 50)
        
        # Test connections
        print("\n🔗 Testing connections...")
        for brand in ['powernow', 'lee1healthcare']:
            self.test_facebook_connection(brand)
            self.test_instagram_connection(brand)
        
        print("\n" + "=" * 50)
        
        # Monitoring loop
        while True:
            try:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Checking for new comments...")
                comment_count = self.monitor_comments()
                print(f"✅ Found {comment_count} comments to process")
                
                # Wait for next check
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                print("\n🛑 Stopping social media monitor...")
                break
            except Exception as e:
                print(f"❌ Monitor error: {e}")
                time.sleep(60)  # Wait 1 minute on error

def main():
    """Main function"""
    manager = SocialMediaManager()
    
    # Check if tokens are configured
    print("🔧 Social Media Manager Configuration Check")
    print("=" * 50)
    
    tokens_configured = False
    for brand_key, brand_info in manager.brands.items():
        print(f"\n{brand_info['name']}:")
        
        fb_configured = bool(brand_info['facebook_token'])
        ig_configured = bool(brand_info['instagram_token'])
        
        fb_status = "✅ Configured" if fb_configured else "❌ Not configured"
        ig_status = "✅ Configured" if ig_configured else "❌ Not configured"
        print(f"  Facebook: {fb_status}")
        print(f"  Instagram: {ig_status}")
        
        if fb_configured or ig_configured:
            tokens_configured = True
    
    print("\n" + "=" * 50)
    
    if not tokens_configured:
        print("\n⚠️  No social media tokens configured!")
        print("\nTo configure, set environment variables:")
        print("""
# PowerNow Asia
export POWERNOW_FB_PAGE_ID="your_page_id"
export POWERNOW_FB_TOKEN="your_facebook_token"
export POWERNOW_IG_ID="your_instagram_id"
export POWERNOW_IG_TOKEN="your_instagram_token"

# Lee1 Healthcare
export LEE1_FB_PAGE_ID="your_page_id"
export LEE1_FB_TOKEN="your_facebook_token"
export LEE1_IG_ID="your_instagram_id"
export LEE1_IG_TOKEN="your_instagram_token"
""")
        print("\nOr create config/social_media.json with your tokens.")
        print("\nRun in test mode (no tokens required):")
        print("  python social_media_manager.py --test")
        return
    
    # Start monitoring
    try:
        manager.run_monitor(interval_minutes=5)
    except KeyboardInterrupt:
        print("\n👋 Social media monitor stopped")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("🧪 Running in test mode...")
        manager = SocialMediaManager()
        
        # Test auto-reply functionality
        test_messages = [
            ("powernow", "How much does solar installation cost?"),
            ("powernow", "How long does installation take?"),
            ("lee1healthcare", "I want to book an appointment"),
            ("lee1healthcare", "What are your opening hours?")
        ]
        
        for brand, message in test_messages:
            print(f"\nTest: {message}")
            reply = manager.generate_auto_reply(brand, message)
            print(f"Auto-reply: {reply}")
    else:
        main()