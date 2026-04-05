#!/usr/bin/env python3
"""
Multi-Brand Social Media Publisher - Fixed Version
Supports 4 brands: MyGreenPlus, ShiftByAlf, PowerNow Asia, Lee1 Healthcare
"""

import os
import json
import time
import random
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

class MultiBrandPublisher:
    """Publisher for 4 brands across Facebook and Instagram"""
    
    def __init__(self):
        self.brands = {
            'mygreenplus': {
                'name': 'MyGreenPlus',
                'description': 'Smart RVM Recycling Machine Service',
                'facebook_token': os.environ.get('MYGREENPLUS_FB_TOKEN', ''),
                'instagram_token': os.environ.get('MYGREENPLUS_IG_TOKEN', ''),
                'page_id': os.environ.get('MYGREENPLUS_FB_PAGE_ID', ''),
                'instagram_id': os.environ.get('MYGREENPLUS_IG_ID', ''),
                'content_themes': [
                    'environmental_education',
                    'customer_success',
                    'product_features',
                    'sustainability_tips',
                    'community_impact'
                ],
                'posting_times': ['09:00', '14:00', '18:00']
            },
            'shiftbyalf': {
                'name': 'ShiftByAlf',
                'description': '[Business definition pending]',
                'facebook_token': os.environ.get('SHIFTBVALF_FB_TOKEN', ''),
                'instagram_token': os.environ.get('SHIFTBVALF_IG_TOKEN', ''),
                'page_id': os.environ.get('SHIFTBVALF_FB_PAGE_ID', ''),
                'instagram_id': os.environ.get('SHIFTBVALF_IG_ID', ''),
                'content_themes': [
                    'brand_intro',
                    'coming_soon',
                    'product_teasers',
                    'brand_values',
                    'engagement_posts'
                ],
                'posting_times': ['10:00', '15:00', '19:00']
            },
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
                ],
                'posting_times': ['08:00', '13:00', '17:00']
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
                ],
                'posting_times': ['11:00', '16:00', '20:00']
            }
        }
        
        self.content_library = self.load_content_library()
        
    def load_content_library(self) -> Dict:
        """Load content library from JSON file"""
        lib_path = Path(__file__).parent / 'content' / 'content_library.json'
        if lib_path.exists():
            with open(lib_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {brand: [] for brand in self.brands.keys()}
    
    def get_unused_content(self, brand: str, content_type: Optional[str] = None) -> List[Dict]:
        """Get unused content from library"""
        if brand not in self.content_library:
            return []
        
        unused = [c for c in self.content_library[brand] if not c['used']]
        if content_type:
            unused = [c for c in unused if c['type'] == content_type]
        
        return unused
    
    def generate_daily_schedule(self):
        """Generate optimized daily posting schedule for 4 brands"""
        schedule = []
        
        # Stagger posting times to avoid overlap
        time_slots = {
            '08:00': ['powernow_asia'],
            '09:00': ['mygreenplus'],
            '10:00': ['shiftbyalf'],
            '11:00': ['lee1_healthcare'],
            '13:00': ['powernow_asia'],
            '14:00': ['mygreenplus'],
            '15:00': ['shiftbyalf'],
            '16:00': ['lee1_healthcare'],
            '17:00': ['powernow_asia'],
            '18:00': ['mygreenplus'],
            '19:00': ['shiftbyalf'],
            '20:00': ['lee1_healthcare']
        }
        
        for time_str, brands in time_slots.items():
            posts = []
            for brand_key in brands:
                brand_info = self.brands[brand_key]
                # Select a theme for this post
                available_themes = []
                for theme in brand_info['content_themes']:
                    if self.get_unused_content(brand_key, theme):
                        available_themes.append(theme)
                
                if available_themes:
                    selected_theme = random.choice(available_themes)
                    posts.append({
                        'brand': brand_key,
                        'theme': selected_theme
                    })
            
            if posts:
                schedule.append({
                    'time': time_str,
                    'posts': posts
                })
        
        return schedule
    
    def preview_schedule(self):
        """Preview the daily posting schedule"""
        print("\n" + "="*60)
        print("📅 MULTI-BRAND DAILY POSTING SCHEDULE")
        print("="*60)
        
        schedule = self.generate_daily_schedule()
        
        for time_slot in schedule:
            print(f"\n⏰ {time_slot['time']}")
            print("-" * 40)
            
            for post in time_slot['posts']:
                brand_key = post['brand']
                theme = post['theme']
                brand_name = self.brands[brand_key]['name']
                brand_desc = self.brands[brand_key]['description']
                
                # Get available content
                available = self.get_unused_content(brand_key, theme)
                count = len(available)
                
                print(f"  🏢 {brand_name}")
                print(f"     Business: {brand_desc}")
                print(f"     Theme: {theme}")
                print(f"     Available content: {count} posts")
                
                if count > 0 and count <= 2:
                    for content in available[:1]:
                        preview = content['text'][:80].replace('\n', ' ') + "..."
                        print(f"     • {preview}")
        
        print("\n" + "="*60)
        print("📊 TOTAL CONTENT AVAILABLE:")
        print("="*60)
        for brand_key, brand_info in self.brands.items():
            brand_name = brand_info['name']
            total = len(self.content_library.get(brand_key, []))
            unused = len(self.get_unused_content(brand_key))
            used = total - unused
            
            print(f"  {brand_name}:")
            print(f"    Total: {total} posts | Used: {used} | Available: {unused}")
            
            # Show content types
            if total > 0:
                types = {}
                for content in self.content_library.get(brand_key, []):
                    content_type = content['type']
                    types[content_type] = types.get(content_type, 0) + 1
                
                print(f"    Content types: {', '.join(types.keys())}")
    
    def simulate_daily_posting(self):
        """Simulate daily posting for all brands"""
        print("\n" + "="*60)
        print("🚀 DAILY POSTING SIMULATION - 4 BRANDS")
        print("="*60)
        
        schedule = self.generate_daily_schedule()
        total_posts = 0
        successful_posts = 0
        
        for time_slot in schedule:
            print(f"\n⏰ {time_slot['time']}")
            print("-" * 40)
            
            for post in time_slot['posts']:
                brand_key = post['brand']
                theme = post['theme']
                brand_name = self.brands[brand_key]['name']
                brand_desc = self.brands[brand_key]['description']
                
                print(f"\n  🏢 {brand_name}")
                print(f"  Business: {brand_desc}")
                print(f"  Theme: {theme}")
                
                available = self.get_unused_content(brand_key, theme)
                
                if not available:
                    print(f"  Status: ❌ No content available")
                    total_posts += 1
                    continue
                
                content = random.choice(available)
                
                print(f"  📤 SIMULATED POST:")
                print(f"     Content ID: {content['id']}")
                print(f"     Preview: {content['text'][:60]}...")
                print(f"     Platforms: Facebook, Instagram")
                print(f"     Status: ✅ Ready to post")
                
                successful_posts += 1
                total_posts += 1
                
                time.sleep(0.3)  # Small delay for readability
        
        print("\n" + "="*60)
        print("📊 SIMULATION SUMMARY")
        print("="*60)
        print(f"Total posts scheduled: {total_posts}")
        print(f"Successful posts: {successful_posts}")
        print(f"Failed posts: {total_posts - successful_posts}")
        
        # Show remaining content
        print(f"\n📦 REMAINING CONTENT:")
        for brand_key, brand_info in self.brands.items():
            brand_name = brand_info['name']
            remaining = len(self.get_unused_content(brand_key))
            print(f"  {brand_name}: {remaining} posts")
    
    def check_brand_status(self):
        """Check status of all brands"""
        print("\n" + "="*60)
        print("🔍 BRAND STATUS CHECK")
        print("="*60)
        
        for brand_key, brand_info in self.brands.items():
            print(f"\n🏢 {brand_info['name']}")
            print(f"   Description: {brand_info['description']}")
            
            # Token status
            fb_token = "✅ Configured" if brand_info['facebook_token'] else "❌ Not configured"
            ig_token = "✅ Configured" if brand_info['instagram_token'] else "❌ Not configured"
            fb_page = "✅ Configured" if brand_info['page_id'] else "❌ Not configured"
            ig_id = "✅ Configured" if brand_info['instagram_id'] else "❌ Not configured"
            
            print(f"   Facebook Token: {fb_token}")
            print(f"   Instagram Token: {ig_token}")
            print(f"   Facebook Page ID: {fb_page}")
            print(f"   Instagram ID: {ig_id}")
            
            # Content status
            total = len(self.content_library.get(brand_key, []))
            unused = len(self.get_unused_content(brand_key))
            
            print(f"   Content: {total} total, {unused} available")
            print(f"   Posting times: {', '.join(brand_info['posting_times'])}")
    
    def update_shiftbyalf_definition(self, business_definition: str):
        """Update ShiftByAlf business definition"""
        self.brands['shiftbyalf']['description'] = business_definition
        print(f"✅ Updated ShiftByAlf business definition:")
        print(f"   {business_definition}")
        
        # Suggest content themes based on business definition
        print(f"\n📝 Suggested content themes for ShiftByAlf:")
        
        # Simple theme suggestions based on keywords
        business_lower = business_definition.lower()
        if any(word in business_lower for word in ['fashion', 'clothing', 'apparel']):
            print("   • Fashion trends")
            print("   • Style tips")
            print("   • New collections")
            print("   • Customer styling")
            print("   • Fashion events")
        elif any(word in business_lower for word in ['food', 'restaurant', 'cafe']):
            print("   • Menu highlights")
            print("   • Special offers")
            print("   • Customer reviews")
            print("   • Behind the scenes")
            print("   • Food photography")
        elif any(word in business_lower for word in ['tech', 'software', 'app']):
            print("   • Product features")
            print("   • Tech tips")
            print("   • Updates & releases")
            print("   • User testimonials")
            print("   • Industry insights")
        else:
            print("   • Brand story")
            print("   • Product/services")
            print("   • Customer success")
            print("   • Industry news")
            print("   • Engagement posts")

def test_multi_brand():
    """Test function"""
    print("🧪 Testing Multi-Brand Social Media Publisher")
    print("="*60)
    
    # Create publisher instance
    publisher = MultiBrandPublisher()
    
    # Test 1: Check brand status
    print("\n🔍 Test 1: Brand Status Check")
    print("-"*40)
    publisher.check_brand_status()
    
    # Test 2: Preview schedule
    print("\n📅 Test 2: Daily Schedule Preview")
    print("-"*40)
    publisher.preview_schedule()
    
    # Test 3: Simulate posting
    print("\n🚀 Test 3: Daily Posting Simulation")
    print("-"*40)
    publisher.simulate_daily_posting()
    
    print("\n" + "="*60)
    print("✅ Multi-brand system test completed!")
    print("="*60)
    print("\n📋 URGENT ACTION NEEDED:")
    print("Tell me: What is ShiftByAlf business?")
    print("\nOnce defined, I'll create proper content and complete the system!")

if __name__ == "__main__":
    test_multi_brand()