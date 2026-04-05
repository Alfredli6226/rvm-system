# Social Media Setup Guide

## 🎯 Business Definitions

### **1. PowerNow Asia**
- **Business**: Shared Power Bank Rental Service
- **Content Themes**: Power bank rental, charging stations, rental benefits, how-to guides, customer testimonials
- **Target Audience**: Students, professionals, travelers, shoppers in KL area
- **Key Messages**: Convenience, affordability, availability, ease of use

### **2. Lee1 Healthcare**
- **Business**: Traditional Chinese Medicine Acupuncture for Weight Loss & Body Wellness
- **Content Themes**: Acupuncture weight loss, TCM body wellness, treatment packages, success stories, health tips
- **Target Audience**: Adults seeking natural weight loss, body wellness, stress relief
- **Key Messages**: Natural healing, holistic approach, proven results, professional care

## 📱 Platform Setup

### **Facebook Setup**

#### **1. Create Facebook Developer Account**
1. Go to https://developers.facebook.com/
2. Create a new app (choose "Business")
3. Add "Facebook Login" and "Pages" products

#### **2. Get Page Access Token**
1. Go to your Facebook Page
2. Settings → Page Roles
3. Ensure you're an admin
4. Go to https://developers.facebook.com/tools/explorer/
5. Select your app
6. Get User Token with `pages_manage_posts`, `pages_read_engagement`, `pages_show_list` permissions
7. Exchange for Page Token

#### **3. Connect Instagram Business Account**
1. Facebook Page Settings → Instagram
2. Connect Instagram Business Account
3. Get Instagram Business Account ID

### **Instagram Setup**

#### **1. Convert to Business Account**
1. Instagram Profile → Settings → Account
2. Switch to Professional Account → Business
3. Connect to Facebook Page

#### **2. Get Instagram Access Token**
1. Through Facebook Graph API
2. Requires Facebook Page with connected Instagram
3. Token includes `instagram_basic`, `instagram_content_publish`, `pages_read_engagement`

## 🔑 Environment Variables

### **PowerNow Asia Tokens**
```bash
export POWERNOW_FB_TOKEN="your_facebook_page_token"
export POWERNOW_FB_PAGE_ID="your_facebook_page_id"
export POWERNOW_IG_TOKEN="your_instagram_token"
export POWERNOW_IG_ID="your_instagram_business_account_id"
```

### **Lee1 Healthcare Tokens**
```bash
export LEE1_FB_TOKEN="your_facebook_page_token"
export LEE1_FB_PAGE_ID="your_facebook_page_id"
export LEE1_IG_TOKEN="your_instagram_token"
export LEE1_IG_ID="your_instagram_business_account_id"
```

### **Permanent Setup (add to ~/.zshrc or ~/.bashrc)**
```bash
# Social Media Tokens
export POWERNOW_FB_TOKEN="EAAG..."
export POWERNOW_FB_PAGE_ID="123456789"
export POWERNOW_IG_TOKEN="IGQVJ..."
export POWERNOW_IG_ID="178414123456789"

export LEE1_FB_TOKEN="EAAG..."
export LEE1_FB_PAGE_ID="987654321"
export LEE1_IG_TOKEN="IGQVJ..."
export LEE1_IG_ID="178414987654321"
```

## 🚀 Running the Publisher

### **1. Simulation Mode (No Tokens)**
```bash
# Just preview and simulate
./start_publisher.sh

# Or directly
python3 simple_social_publisher.py
```

### **2. Production Mode (With Tokens)**
```bash
# Set tokens first
export POWERNOW_FB_TOKEN="your_token"
export LEE1_FB_TOKEN="your_token"
# ... etc

# Run publisher
./start_publisher.sh
```

### **3. Manual Testing**
```bash
# Test PowerNow Asia content
python3 -c "
import os
os.environ['POWERNOW_FB_TOKEN'] = 'test'
from simple_social_publisher import SimpleSocialPublisher
p = SimpleSocialPublisher()
p.preview_schedule()
"

# Test Lee1 Healthcare content
python3 -c "
import os
os.environ['LEE1_FB_TOKEN'] = 'test'
from simple_social_publisher import SimpleSocialPublisher
p = SimpleSocialPublisher()
p.run_daily_simulation()
"
```

## 📝 Content Management

### **1. Content Library Structure**
```json
{
  "powernow_asia": [
    {
      "id": 1,
      "type": "powerbank_rental",
      "text": "Post content here...",
      "image_path": null,
      "created_at": "2026-04-05T23:10:00",
      "used": false,
      "platforms_used": []
    }
  ],
  "lee1_healthcare": [...]
}
```

### **2. Adding New Content**

#### **Method A: Edit JSON file directly**
```bash
nano content/content_library.json
```

#### **Method B: Use Python script**
```python
from simple_social_publisher import SimpleSocialPublisher

p = SimpleSocialPublisher()

# Add PowerNow Asia content
p.add_content(
    brand='powernow_asia',
    content_type='powerbank_rental',
    text='New post about power bank rental...'
)

# Add Lee1 Healthcare content
p.add_content(
    brand='lee1_healthcare',
    content_type='acupuncture_weightloss',
    text='New post about acupuncture for weight loss...'
)
```

#### **Method C: Command line**
```bash
# Add sample content through menu
python3 simple_social_publisher.py
# Choose option 4
```

### **3. Content Types**

#### **PowerNow Asia Content Types:**
- `powerbank_rental` - General rental information
- `charging_stations` - Location announcements
- `rental_benefits` - Benefits of using service
- `how_to_use` - Tutorials and guides
- `customer_testimonials` - Customer reviews

#### **Lee1 Healthcare Content Types:**
- `acupuncture_weightloss` - Weight loss treatments
- `tcm_body_wellness` - General wellness
- `treatment_packages` - Package offers
- `success_stories` - Patient testimonials
- `health_tips` - TCM health advice

## 📅 Posting Schedule

### **Daily Schedule (3 posts per day per brand)**
```
09:00 AM - Morning Posts
  • PowerNow Asia: Power bank rental
  • Lee1 Healthcare: Acupuncture weight loss

01:00 PM - Afternoon Posts
  • PowerNow Asia: Charging stations
  • Lee1 Healthcare: TCM body wellness

05:00 PM - Evening Posts
  • PowerNow Asia: Customer testimonials
  • Lee1 Healthcare: Success stories
```

### **Customizing Schedule**
Edit `generate_daily_schedule()` method in `simple_social_publisher.py`:
```python
def generate_daily_schedule(self):
    schedule = []
    
    # Add your custom time slots
    schedule.append({
        'time': '08:00',
        'posts': [
            {'brand': 'powernow_asia', 'theme': 'powerbank_rental'},
            {'brand': 'lee1_healthcare', 'theme': 'health_tips'}
        ]
    })
    # ... more time slots
    
    return schedule
```

## 🔧 Troubleshooting

### **Common Issues**

#### **1. "No module named requests"**
```bash
pip3 install requests
```

#### **2. Facebook Token Errors**
- Check token expiration (tokens expire every 60 days)
- Verify permissions: `pages_manage_posts`, `pages_read_engagement`
- Ensure Page ID is correct

#### **3. Instagram Connection Issues**
- Instagram account must be Business account
- Must be connected to Facebook Page
- Need `instagram_basic` and `instagram_content_publish` permissions

#### **4. "No available content"**
- Add more content to library
- Check content types match themes
- Mark unused content: `"used": false`

### **Debug Mode**
```bash
# Enable debug logging
export DEBUG=1
./start_publisher.sh

# Or run Python with debug
python3 -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from simple_social_publisher import SimpleSocialPublisher
p = SimpleSocialPublisher()
p.check_tokens()
"
```

## 📊 Monitoring

### **1. Content Usage**
```bash
# Check used/unused content
python3 -c "
from simple_social_publisher import SimpleSocialPublisher
p = SimpleSocialPublisher()

for brand in ['powernow_asia', 'lee1_healthcare']:
    total = len(p.content_library.get(brand, []))
    unused = len(p.get_unused_content(brand))
    used = total - unused
    print(f'{brand}: {used}/{total} posts used')
"
```

### **2. Token Status**
```bash
# Check token configuration
python3 simple_social_publisher.py
# Choose option 3
```

### **3. Schedule Preview**
```bash
# Preview next day's schedule
python3 simple_social_publisher.py
# Choose option 1
```

## 🚀 Production Deployment

### **1. Cron Job for Automatic Posting**
```bash
# Edit crontab
crontab -e

# Add daily posting schedule
0 9 * * * cd /path/to/rvm_customer_service_system && ./start_publisher.sh >> /var/log/social_publisher.log 2>&1
0 13 * * * cd /path/to/rvm_customer_service_system && ./start_publisher.sh >> /var/log/social_publisher.log 2>&1
0 17 * * * cd /path/to/rvm_customer_service_system && ./start_publisher.sh >> /var/log/social_publisher.log 2>&1
```

### **2. Log Rotation**
```bash
# Create logrotate config
sudo nano /etc/logrotate.d/social_publisher

# Add configuration
/var/log/social_publisher.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
    create 644 root root
}
```

### **3. Monitoring Script**
```bash
#!/bin/bash
# monitor_social.sh

LOG_FILE="/var/log/social_publisher.log"
ERROR_PATTERNS=("ERROR" "FAILED" "Token expired" "Permission denied")

for pattern in "${ERROR_PATTERNS[@]}"; do
    if grep -q "$pattern" "$LOG_FILE"; then
        echo "ALERT: Found '$pattern' in social publisher log"
        # Send notification (Telegram, email, etc.)
    fi
done
```

## 📞 Support

### **Quick Reference**
- **Publisher Script**: `simple_social_publisher.py`
- **Content Library**: `content/content_library.json`
- **Start Script**: `./start_publisher.sh`
- **Setup Guide**: This file (`SOCIAL_MEDIA_SETUP.md`)

### **Getting Help**
1. Check error messages in console
2. Verify token permissions
3. Test with simulation mode first
4. Review Facebook/Instagram API documentation

### **Emergency Stop**
```bash
# Stop all posting
unset POWERNOW_FB_TOKEN LEE1_FB_TOKEN POWERNOW_IG_TOKEN LEE1_IG_TOKEN

# Or disable in script
mv simple_social_publisher.py simple_social_publisher.py.disabled
```

---

**Last Updated**: 2026-04-05  
**Status**: ✅ Ready for token configuration  
**Next Step**: Get Facebook/Instagram tokens and test posting