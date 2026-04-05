#!/usr/bin/env python3
"""
Simple Social Media Publisher - Updated for Business Definitions
PowerNow Asia: Shared Power Bank Rental Service
Lee1 Healthcare: TCM Acupuncture for Weight Loss & Body Wellness
"""

import os
import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

class SimpleSocialPublisher:
    """Simple publisher for Facebook and Instagram posts"""
    
    def __init__(self):
        self.brands = {
            'powernow_asia': {
                'name': 'PowerNow Asia',
                'description': 'Shared Power Bank Rental Service',
                'facebook_token': os.environ.get('POWERNOW_FB_TOKEN', ''),
                'instagram_token': os.environ.get('POWERNOW_IG_TOKEN', ''),
                'page_id': os.environ.get('POWERNOW_FB_PAGE_ID', ''),
                'instagram_id': os.environ.get('POWERNOW_IG_ID', ''),
                'content_themes': [
                    'powerbank_rental',
                    'charging_stations',
                    'rental_benefits',
                    'how_to_use',
                    'customer_testimonials'
                ]
            },
            'lee1_healthcare': {
                'name': 'Lee1 Healthcare',
                'description': 'Traditional Chinese Medicine Acupuncture for Weight Loss & Body Wellness',
                'facebook_token': os.environ.get('LEE1_FB_TOKEN', ''),
                'instagram_token': os.environ.get('LEE1_IG_TOKEN', ''),
                'page_id': os.environ.get('LEE1_FB_PAGE_ID', ''),
                'instagram_id': os.environ.get('LEE1_IG_ID', ''),
                'content_themes': [
                    'acupuncture_weightloss',
                    'tcm_body_wellness',
                    'treatment_packages',
                    'success_stories',
                    'health_tips'
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
        return {'powernow_asia': [], 'lee1_healthcare': []}
    
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
    
    def mark_content_used(self, brand: str, content_id: int, platform: str):
        """Mark content as used on specific platform"""
        for content in self.content_library.get(brand, []):
            if content['id'] == content_id:
                content['used'] = True
                if platform not in content['platforms_used']:
                    content['platforms_used'].append(platform)
                self.save_content_library()
                break
    
    def generate_daily_schedule(self):
        """Generate daily posting schedule"""
        schedule = []
        
        # Morning posts (9:00 AM)
        schedule.append({
            'time': '09:00',
            'posts': [
                {'brand': 'powernow_asia', 'theme': 'powerbank_rental'},
                {'brand': 'lee1_healthcare', 'theme': 'acupuncture_weightloss'}
            ]
        })
        
        # Afternoon posts (1:00 PM)
        schedule.append({
            'time': '13:00',
            'posts': [
                {'brand': 'powernow_asia', 'theme': 'charging_stations'},
                {'brand': 'lee1_healthcare', 'theme': 'tcm_body_wellness'}
            ]
        })
        
        # Evening posts (5:00 PM)
        schedule.append({
            'time': '17:00',
            'posts': [
                {'brand': 'powernow_asia', 'theme': 'customer_testimonials'},
                {'brand': 'lee1_healthcare', 'theme': 'success_stories'}
            ]
        })
        
        return schedule
    
    def preview_schedule(self):
        """Preview the daily posting schedule"""
        print("\n" + "="*50)
        print("📅 DAILY POSTING SCHEDULE")
        print("="*50)
        
        schedule = self.generate_daily_schedule()
        
        for time_slot in schedule:
            print(f"\n⏰ {time_slot['time']}")
            print("-" * 30)
            
            for post in time_slot['posts']:
                brand = post['brand']
                theme = post['theme']
                brand_name = self.brands[brand]['name']
                
                # Get available content
                available = self.get_unused_content(brand, theme)
                count = len(available)
                
                print(f"  🏢 {brand_name}: {theme}")
                print(f"     Available content: {count} posts")
                
                if count > 0 and count <= 3:
                    for content in available[:2]:
                        preview = content['text'][:60].replace('\n', ' ') + "..."
                        print(f"     • {preview}")
        
        print("\n" + "="*50)
        print("Total available posts:")
        for brand in ['powernow_asia', 'lee1_healthcare']:
            brand_name = self.brands[brand]['name']
            total = len(self.get_unused_content(brand))
            print(f"  {brand_name}: {total} posts")
        print("="*50)
    
    def simulate_post(self, brand: str, content_type: str):
        """Simulate posting without actual API calls"""
        available = self.get_unused_content(brand, content_type)
        
        if not available:
            print(f"❌ No available content for {brand} - {content_type}")
            return False
        
        content = random.choice(available)
        brand_name = self.brands[brand]['name']
        
        print(f"\n📤 SIMULATED POST: {brand_name}")
        print(f"   Theme: {content_type}")
        print(f"   Content ID: {content['id']}")
        print("-" * 40)
        print(content['text'])
        print("-" * 40)
        print(f"   Platforms: Facebook, Instagram")
        print(f"   Status: ✅ Ready to post")
        
        # Mark as used in simulation
        self.mark_content_used(brand, content['id'], 'facebook')
        self.mark_content_used(brand, content['id'], 'instagram')
        
        return True
    
    def run_daily_simulation(self):
        """Run simulation of daily posting schedule"""
        print("\n" + "="*50)
        print("🚀 DAILY POSTING SIMULATION")
        print("="*50)
        
        schedule = self.generate_daily_schedule()
        total_posts = 0
        successful_posts = 0
        
        for time_slot in schedule:
            print(f"\n⏰ {time_slot['time']}")
            print("-" * 30)
            
            for post in time_slot['posts']:
                brand = post['brand']
                theme = post['theme']
                brand_name = self.brands[brand]['name']
                
                print(f"\n  🏢 {brand_name}")
                print(f"  Theme: {theme}")
                
                if self.simulate_post(brand, theme):
                    successful_posts += 1
                    print(f"  Status: ✅ Posted successfully")
                else:
                    print(f"  Status: ❌ No content available")
                
                total_posts += 1
                time.sleep(0.5)  # Small delay for readability
        
        print("\n" + "="*50)
        print("📊 SIMULATION SUMMARY")
        print("="*50)
        print(f"Total posts scheduled: {total_posts}")
        print(f"Successful posts: {successful_posts}")
        print(f"Failed posts: {total_posts - successful_posts}")
        
        # Show remaining content
        print(f"\n📦 Remaining content:")
        for brand in ['powernow_asia', 'lee1_healthcare']:
            brand_name = self.brands[brand]['name']
            remaining = len(self.get_unused_content(brand))
            print(f"  {brand_name}: {remaining} posts")
    
    def check_tokens(self):
        """Check if social media tokens are configured"""
        print("\n" + "="*50)
        print("🔑 SOCIAL MEDIA TOKEN STATUS")
        print("="*50)
        
        for brand_key, brand_info in self.brands.items():
            print(f"\n🏢 {brand_info['name']}")
            print(f"   Description: {brand_info['description']}")
            
            fb_token = "✅ Configured" if brand_info['facebook_token'] else "❌ Not configured"
            ig_token = "✅ Configured" if brand_info['instagram_token'] else "❌ Not configured"
            fb_page = "✅ Configured" if brand_info['page_id'] else "❌ Not configured"
            ig_id = "✅ Configured" if brand_info['instagram_id'] else "❌ Not configured"
            
            print(f"   Facebook Token: {fb_token}")
            print(f"   Instagram Token: {ig_token}")
            print(f"   Facebook Page ID: {fb_page}")
            print(f"   Instagram ID: {ig_id}")
        
        print("\n" + "="*50)
        print("📝 TOKEN SETUP INSTRUCTIONS:")
        print("="*50)
        print("1. Create Facebook Developer App")
        print("2. Get Page Access Token")
        print("3. Connect Instagram Business Account")
        print("4. Set environment variables:")
        print("   export POWERNOW_FB_TOKEN='your_token'")
        print("   export LEE1_FB_TOKEN='your_token'")
        print("   etc...")
    
    def add_sample_content(self):
        """Add sample content for testing"""
        print("\n📝 Adding sample content...")
        
        # PowerNow Asia sample content
        powernow_samples = [
            {
                'type': 'powerbank_rental',
                'text': '🔋 Need a power boost? Rent PowerNow Asia power banks at malls and cafes across KL! Easy rent, easy return. Stay charged! 📱 #PowerBank #Rental #PowerNowAsia #KL'
            },
            {
                'type': 'charging_stations',
                'text': '📍 Find us at Pavilion KL, Mid Valley, and Sunway Pyramid! Our charging stations are conveniently located. Never run out of battery while shopping! 🛍️ #ChargingStation #PowerNowAsia #ShoppingMalls'
            }
        ]
        
        # Lee1 Healthcare sample content
        lee1_samples = [
            {
                'type': 'acupuncture_weightloss',
                'text': '🧘‍♀️ Lose weight naturally with TCM acupuncture! Regulate metabolism, reduce cravings, and achieve sustainable results. No harsh chemicals, just natural healing. 🌿 #Acupuncture #WeightLoss #TCM #Lee1Healthcare'
            },
            {
                'type': 'tcm_body_wellness',
                'text': '🌿 Experience holistic wellness with Traditional Chinese Medicine. Acupuncture, herbal medicine, and dietary therapy for complete body balance. Restore your natural vitality! 💪 #TCM #Wellness #TraditionalMedicine #Lee1Healthcare'
            }
        ]
        
        for sample in powernow_samples:
            self.add_content('powernow_asia', sample['type'], sample['text'])
        
        for sample in lee1_samples:
            self.add_content('lee1_healthcare', sample['type'], sample['text'])
        
        print("✅ Sample content added successfully!")

def main():
    """Main function"""
    publisher = SimpleSocialPublisher()
    
    print("\n" + "="*50)
    print("📱 SIMPLE SOCIAL MEDIA PUBLISHER")
    print("="*50)
    print("PowerNow Asia: Shared Power Bank Rental")
    print("Lee1 Healthcare: TCM Acupuncture & Wellness")
    print("="*50)
    
    while True:
        print("\n📋 MENU:")
        print("1. Preview daily schedule")
        print("2. Run daily simulation")
        print("3. Check token status")
        print("4. Add sample content")
        print("5. View content library")
        print("6. Exit")
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == '1':
            publisher.preview_schedule()
        elif choice == '2':
            publisher.run_daily_simulation()
        elif choice == '3':
            publisher.check_tokens()
        elif choice == '4':
            publisher.add_sample_content()
        elif choice == '5':
            print("\n📚 Content Library:")
            for brand in ['powernow_asia', 'lee1_healthcare']:
                brand_name = publisher.brands[brand]['name']
                content_count = len(publisher.content_library.get(brand, []))
                print(f"  {brand_name}: {content_count} posts")
        elif choice == '6':
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()