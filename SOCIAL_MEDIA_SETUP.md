# Facebook & Instagram Integration Guide

## 🎯 Integrated Brands

### 1. PowerNow Asia
- **Facebook Page**: PowerNow Asia
- **Instagram**: @powernow.asia
- **Business Type**: Energy Solutions
- **Auto-reply Focus**: Pricing, Installation, Solar Energy

### 2. Lee1 Healthcare
- **Facebook Page**: Lee1 Healthcare
- **Instagram**: @lee1healthcare
- **Business Type**: Healthcare Services
- **Auto-reply Focus**: Appointments, Pricing, Specialists, Hours

## 🚀 Quick Setup (10 Minutes)

### Step 1: Get Facebook Access Tokens

#### For PowerNow Asia:
1. Go to https://developers.facebook.com/tools/explorer
2. Select your app (or create new)
3. Get Page Access Token for PowerNow Asia page
4. Get Instagram Access Token for @powernow.asia

#### For Lee1 Healthcare:
1. Repeat same process for Lee1 Healthcare page
2. Get tokens for both Facebook and Instagram

### Step 2: Configure Environment Variables

```bash
# PowerNow Asia
export POWERNOW_FB_PAGE_ID="123456789012345"
export POWERNOW_FB_TOKEN="EAABsbZ...your_token"
export POWERNOW_IG_ID="178414053...your_id"
export POWERNOW_IG_TOKEN="IGQVJ...your_token"

# Lee1 Healthcare
export LEE1_FB_PAGE_ID="987654321098765"
export LEE1_FB_TOKEN="EAACEdE...your_token"
export LEE1_IG_ID="178414054...your_id"
export LEE1_IG_TOKEN="IGQWR...your_token"

# Make permanent (add to ~/.zshrc)
echo 'export POWERNOW_FB_PAGE_ID="..."' >> ~/.zshrc
echo 'export POWERNOW_FB_TOKEN="..."' >> ~/.zshrc
# ... add all variables
source ~/.zshrc
```

### Step 3: Start Social Media Monitor

```bash
cd /Users/alfredli6226/.openclaw/workspace/rvm_customer_service_system
python social_media_manager.py
```

## 📱 Features

### 1. Auto-Reply System

#### PowerNow Asia Responses:
- **Pricing questions**: "Thank you for your interest in PowerNow Asia! Pricing depends on your specific energy needs..."
- **Installation time**: "Standard installation takes 3-5 business days after site assessment..."
- **Solar energy**: "We specialize in solar and renewable energy solutions! Our systems can reduce your electricity bills by up to 70%..."
- **Contact info**: "You can reach us at: 📞 +603-1234 5678, 📧 info@powernow.asia..."

#### Lee1 Healthcare Responses:
- **Appointments**: "To book an appointment, please provide: 1. Your full name 2. Contact number 3. Preferred date/time..."
- **Pricing**: "Consultation fees start from RM50. Specific treatment costs depend on the service required..."
- **Specialists**: "We have specialists in: • General Medicine • Pediatrics • Cardiology • Dermatology • Orthopedics..."
- **Hours**: "Our clinic hours: Mon-Fri: 8:30AM - 8:00PM, Sat: 9:00AM - 5:00PM, Sun: 10:00AM - 2:00PM..."

### 2. Comment Monitoring
- **Check interval**: Every 5 minutes
- **Platforms**: Facebook & Instagram
- **Actions**: Auto-reply, alert for manual review
- **History**: Track all interactions

### 3. Post Management
- **Schedule posts**: Pre-schedule content
- **Cross-posting**: Post to both platforms
- **Analytics**: Track engagement metrics
- **Content calendar**: Plan ahead

## 🔧 Technical Requirements

### Facebook API Permissions Needed:

#### Basic Permissions:
- `pages_manage_posts` - Create and manage posts
- `pages_read_engagement` - Read page insights
- `pages_messaging` - Send and receive messages
- `pages_manage_metadata` - Update page settings

#### Instagram Permissions:
- `instagram_basic` - Read profile info and media
- `instagram_manage_comments` - Manage comments
- `instagram_manage_insights` - Read insights
- `instagram_content_publish` - Publish content

### Token Types:

#### 1. Short-lived Token (2 hours)
- For testing
- From Graph API Explorer
- Easy to get

#### 2. Long-lived Token (60 days)
- For production
- Requires app review
- More stable

#### 3. Page Access Token
- Specific to each page
- Required for page operations
- Can be long-lived

## 🛠️ Setup Details

### Finding Page IDs:

#### Facebook Page ID:
1. Go to your Facebook page
2. Click "About"
3. Scroll to "Page ID" (in bottom left)
4. Or use: `https://www.facebook.com/{username}/`

#### Instagram Business Account ID:
1. Go to Facebook Business Settings
2. Select Instagram Accounts
3. Click on your account
4. Find Instagram Account ID

### Getting Access Tokens:

#### Method A: Graph API Explorer
1. Visit: https://developers.facebook.com/tools/explorer
2. Select your app
3. Get User Token with required permissions
4. Exchange for Page Token: `/me/accounts`

#### Method B: Facebook Login Flow
1. Implement OAuth in your app
2. Request permissions from users
3. Exchange code for tokens
4. Store tokens securely

#### Method C: Business Manager
1. Use Facebook Business Manager
2. Generate System User Token
3. Assign to pages
4. More secure for businesses

## ⚙️ Configuration Options

### Environment Variables:
```bash
# Monitoring Settings
export SOCIAL_CHECK_INTERVAL=300  # seconds (5 minutes)
export AUTO_REPLY_ENABLED=true
export NOTIFY_ON_COMMENTS=true

# Alert Settings
export TELEGRAM_ALERT_TOKEN="your_token"  # For Telegram alerts
export ALERT_THRESHOLD=10  # Comments per hour threshold

# Content Settings
export DEFAULT_POST_SCHEDULE="9:00,13:00,17:00"
export TIMEZONE="Asia/Kuala_Lumpur"
```

### Configuration File:
Create `config/social_media.json`:
```json
{
  "powernow": {
    "facebook_page_id": "123456789",
    "facebook_token": "EAAB...",
    "instagram_id": "987654321",
    "instagram_token": "IGQV...",
    "auto_reply_rules": {
      "pricing": "Thank you for your interest...",
      "installation": "Standard installation takes..."
    }
  },
  "lee1healthcare": {
    "facebook_page_id": "234567890",
    "facebook_token": "EAAC...",
    "instagram_id": "876543210",
    "instagram_token": "IGQW...",
    "auto_reply_rules": {
      "appointment": "To book an appointment...",
      "hours": "Our clinic hours..."
    }
  }
}
```

## 🚀 Production Deployment

### 1. Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements_simple.txt
CMD ["python", "social_media_manager.py"]
```

### 2. Systemd Service
```ini
[Unit]
Description=Social Media Manager
After=network.target

[Service]
Type=simple
User=socialuser
Environment=POWERNOW_FB_TOKEN=...
Environment=LEE1_FB_TOKEN=...
WorkingDirectory=/opt/social-media
ExecStart=/usr/bin/python3 social_media_manager.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### 3. Cloud Functions
- **AWS Lambda** + EventBridge (scheduled)
- **Google Cloud Functions** + Cloud Scheduler
- **Azure Functions** + Timer trigger

## 📊 Monitoring Dashboard

### Web Interface Features:
1. **Real-time Comments** - Live feed of all comments
2. **Response Metrics** - Average response time
3. **Engagement Analytics** - Likes, shares, comments
4. **Content Calendar** - Scheduled posts
5. **Alert Center** - Issues requiring attention

### Access URLs:
- **Local**: http://localhost:5070/social-dashboard
- **Production**: https://your-domain.com/social

## 🔒 Security Best Practices

### Token Security:
1. **Never commit** tokens to Git
2. **Use environment variables**
3. **Rotate tokens** regularly
4. **Monitor token usage**

### Access Control:
1. **Minimum permissions** principle
2. **Separate tokens** for each page
3. **Audit logs** for all actions
4. **IP restrictions** where possible

### Data Protection:
1. **Encrypt stored tokens**
2. **Secure API endpoints**
3. **Regular backups**
4. **GDPR compliance**

## 🛠️ Troubleshooting

### Common Issues:

#### 1. "Invalid OAuth access token"
```bash
# Solution: Refresh token
curl -X GET "https://graph.facebook.com/oauth/access_token?  
    grant_type=fb_exchange_token&
    client_id={app-id}&
    client_secret={app-secret}&
    fb_exchange_token={short-lived-token}"
```

#### 2. "Insufficient permissions"
- Check required permissions in app settings
- Re-authenticate with new permissions
- Submit for app review if needed

#### 3. "Rate limit exceeded"
- Implement exponential backoff
- Reduce request frequency
- Use webhooks instead of polling

#### 4. "Instagram media posting failed"
- Ensure image URL is accessible
- Check image format (JPEG, PNG)
- Verify size limits (max 8MB)

### Debug Mode:
```bash
# Enable verbose logging
export DEBUG=1
python social_media_manager.py

# Test specific function
python -c "from social_media_manager import SocialMediaManager; m = SocialMediaManager(); print(m.generate_auto_reply('powernow', 'How much does it cost?'))"
```

## 📈 Advanced Features

### 1. Sentiment Analysis
- Detect positive/negative comments
- Prioritize urgent issues
- Custom responses based on sentiment

### 2. Multi-language Support
- Auto-detect language
- Reply in same language
- Support: English, Malay, Chinese

### 3. AI-Powered Responses
- Context-aware replies
- Learning from manual responses
- Continuous improvement

### 4. Integration with CRM
- Sync customer interactions
- Update contact records
- Track customer journey

## 🤝 Support & Updates

### Documentation:
- This guide
- Code comments
- API documentation at: https://developers.facebook.com/docs/

### Contact:
- **Facebook Developer Support**: https://developers.facebook.com/support/
- **Instagram API Support**: https://developers.facebook.com/support/instagram-api/
- **Technical Issues**: GitHub repository issues

### Updates:
```bash
# Check for updates
cd /Users/alfredli6226/.openclaw/workspace/rvm_customer_service_system
git pull origin main

# Update dependencies
pip install -r requirements_simple.txt --upgrade
```

---

**Last Updated**: 2026-04-05  
**Version**: 1.0.0  
**Status**: ✅ Ready for Integration  
**Next Steps**: Configure Facebook/Instagram tokens and start monitoring