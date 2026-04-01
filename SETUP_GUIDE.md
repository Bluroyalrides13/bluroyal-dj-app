# 🚀 Luxury Ride Share Agent - Setup & Deployment Guide

## Project Summary

Your comprehensive AI-powered luxury ride share booking system is now ready! This guide will help you set up, configure, and deploy the system.

### What You've Built

A production-ready platform featuring:
- **Claude AI** for intelligent conversations and lead qualification
- **FastAPI** web server with REST & WebSocket endpoints
- **Square** payment processing integration
- **Wix** website integration with webhooks
- **SQLite/PostgreSQL** database for persistence
- **LangChain** for AI orchestration
- **Docker** containerization for easy deployment

---

## 📋 Quick Setup (5 minutes)

### Option 1: Manual Setup (Recommended for Development)

```bash
# 1. Navigate to project directory
cd "Blu Royal Temp"

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 5. Run the server
python -m src.main
```

**Server will be available at: http://localhost:8000**

### Option 2: Docker Setup (Recommended for Production)

```bash
# 1. Set up environment
cp .env.production .env

# 2. Edit .env with your credentials

# 3. Start services with Docker Compose
docker-compose up -d

# 4. Check status
docker-compose ps
docker-compose logs app
```

---

## 🔑 Required API Keys & Configuration

### 1. **Anthropic (Claude AI)**

```bash
# Get your API key from: https://console.anthropic.com

# Add to .env:
ANTHROPIC_API_KEY=sk-ant-... (your key here)
```

### 2. **Square Payments**

```bash
# Sign up at: https://squareup.com/us/en/account/create

# Get API key from: https://developer.squareup.com/apps

# For testing use SANDBOX environment:
SQUARE_ACCESS_TOKEN=sq_test_... (your token)
SQUARE_ENVIRONMENT=sandbox

# For production:
# SQUARE_ENVIRONMENT=production
```

### 3. **Wix Integration**

```bash
# In Wix Admin:
# 1. Go to Settings → Custom Apps
# 2. Create new app and get API key

WIX_API_KEY=wix_your_key_here
WIX_SITE_ID=your-site-id
WIX_WEBHOOK_SECRET=your_webhook_secret
```

### 4. **LangChain (Optional)**

```bash
# For LangChain integrations:
LANGCHAIN_API_KEY=your_api_key (optional)
LANGCHAIN_ENABLED=true
```

---

## 📊 Project Structure Reference

```
Blu Royal Temp/
├── src/
│   ├── main.py                    # FastAPI entry point
│   ├── agent/                     # AI Agent modules
│   │   ├── lead_qualifier.py      # Lead scoring
│   │   ├── chat_interface.py      # Conversation management
│   │   ├── booking_manager.py     # Reservation handling
│   │   └── pricing_engine.py      # Quote generation
│   ├── integrations/              # Third-party integrations
│   │   ├── wix_connector.py       # Wix API
│   │   ├── square_payments.py     # Square payments
│   │   └── calendar_sync.py       # Availability
│   ├── models/                    # Data models
│   │   ├── schemas.py             # Pydantic models
│   │   └── database.py            # SQLite operations
│   └── api/                       # REST API
│       ├── routes.py              # Endpoints
│       └── websocket.py           # WebSocket chat
├── config/
│   ├── settings.py                # Configuration
│   └── prompts.py                 # Claude prompts
├── tests/
│   └── test_agent.py              # Unit tests
├── requirements.txt               # Dependencies
├── .env.example                   # Environment template
├── Dockerfile                     # Container image
├── docker-compose.yml             # Multi-container setup
├── examples.py                    # Usage examples
├── setup.sh                       # Quick setup script
├── deploy.sh                      # Deployment script
└── README.md                      # Full documentation
```

---

## 🎯 Testing the System

### 1. **Run Examples**

```bash
# Test all components
python examples.py
```

This will demonstrate:
- Chat conversations & lead qualification
- Pricing calculations
- Booking management
- Discounts and promotions

### 2. **Interactive API Testing**

Visit: **http://localhost:8000/docs**

This gives you Swagger UI with all endpoints:
- `/chat` - Send chat messages
- `/bookings` - Create/manage bookings
- `/quote` - Generate quotes
- `/ws/chat/{session_id}` - WebSocket chat

### 3. **Run Unit Tests**

```bash
pytest tests/ -v
```

---

## 💬 Chat Examples

### Create a Booking via Chat

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I need a premium ride from NYC to JFK airport tomorrow at 2pm",
    "session_id": "session_123"
  }'
```

### WebSocket Chat (Real-time)

```javascript
// Browser console
const sessionId = 'user_' + Date.now();
const ws = new WebSocket(`ws://localhost:8000/ws/chat/${sessionId}`);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log("Agent:", data.response);
  console.log("Lead Score:", data.lead_score);
};

ws.send(JSON.stringify({
  type: "chat",
  message: "Hi, I need luxury rides regularly"
}));
```

---

## 🔧 Configuration Guide

### Service Tiers

Edit `config/settings.py` to customize pricing:

```python
SERVICE_TIERS = {
    "executive": {
        "base_rate": 35.00,      # Base fare
        "per_mile": 3.50,        # Per mile charge
        "per_minute": 0.65,      # Per minute charge
        "min_advance_booking": 120,  # Minutes
    },
    "premier": {
        "base_rate": 50.00,
        "per_mile": 4.50,
        "per_minute": 0.85,
        "min_advance_booking": 120,
    },
    "vip": {
        "base_rate": 75.00,
        "per_mile": 6.00,
        "per_minute": 1.25,
        "min_advance_booking": 120,
    },
}
```

### Supported Cities

Add/modify in `config/settings.py`:

```python
SUPPORTED_CITIES = [
    "New York City, NY",
    "Los Angeles, CA",
    "Chicago, IL",
    "Miami, FL",
    # Add your cities here
]
```

### Lead Scoring Weights

Adjust qualification thresholds:

```python
LEAD_SCORING = {
    "budget_weight": 0.25,              # 25%
    "frequency_weight": 0.25,           # 25%
    "location_weight": 0.20,            # 20%
    "service_preference_weight": 0.20,  # 20%
    "engagement_weight": 0.10,          # 10%
    "high_quality_threshold": 70,       # Score ≥ 70 = qualified
}
```

---

## 🚀 Production Deployment

### Using Docker Compose

```bash
# 1. Prepare environment
cp .env.production .env
nano .env  # Edit with real credentials

# 2. Start services
docker-compose up -d

# 3. Verify health
curl http://localhost:8000/health

# 4. View logs
docker-compose logs -f app

# 5. Stop services
docker-compose down
```

### Environment Setup

**.env.production** contains:
- Production database (PostgreSQL)
- HTTPS enforced
- Secure cookie settings
- Real API credentials
- Production Wix/Square keys

### SSL/HTTPS Setup

```bash
# Use Let's Encrypt with Reverseproxy (nginx/Caddy)
# Example with Nginx:

server {
    listen 443 ssl http2;
    server_name api.yourride.com;
    
    ssl_certificate /etc/letsencrypt/live/api.yourride.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourride.com/privkey.pem;
    
    location / {
        proxy_pass http://app:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## 🔐 Security Checklist

- [ ] Set `ENVIRONMENT=production`
- [ ] Use strong database passwords
- [ ] Enable HTTPS/SSL certificates
- [ ] Verify Wix webhook signatures
- [ ] Rotate API keys regularly
- [ ] Use environment variables (not hardcoded)
- [ ] Set up firewall rules
- [ ] Enable database backups
- [ ] Configure rate limiting (if using nginx)
- [ ] Enable CORS properly

---

## 📊 API Endpoints Summary

### Chat
- `POST /chat` - Send message to agent
- `GET /chat/history/{session_id}` - Get conversation
- `POST /chat/end/{session_id}` - End conversation
- `WS /ws/chat/{session_id}` - WebSocket chat

### Bookings
- `POST /bookings` - Create booking
- `GET /bookings/{booking_id}` - Get booking
- `POST /bookings/{booking_id}/confirm` - Confirm
- `POST /bookings/{booking_id}/cancel` - Cancel

### Pricing
- `GET /quote` - Get price quote
- `GET /quote?distance=10&duration=30&service_tier=premier`

### Webhooks
- `POST /webhooks/wix/chat` - Chat webhook
- `POST /webhooks/wix/contact` - Contact webhook

### System
- `GET /health` - Health check
- `GET /status` - System status

---

## 🧪 Testing Code Examples

### Test Booking Creation

```python
from src.agent.booking_manager import BookingManager
from src.models.schemas import BookingRequest

manager = BookingManager()
request = BookingRequest(
    customer_id="cust_001",
    pickup_location="New York City, NY",
    dropoff_location="JFK Airport",
    booking_date="2026-04-05",
    booking_time="14:00",
    passenger_count=2,
    service_tier="premier",
    contact_email="guest@example.com"
)

booking, quote = manager.create_booking(request)
print(f"Booking: {booking.confirmation_number}")
print(f"Total: ${quote.total_fare}")
```

### Test Chat Agent

```python
from src.agent.chat_interface import ChatInterface
from src.models.schemas import ChatMessage

chat = ChatInterface()
msg = ChatMessage(message="I need a ride to the airport")
response = chat.process_message(msg)

print(f"Agent: {response.response}")
print(f"Lead Score: {response.lead_score}")
```

### Test Pricing

```python
from src.agent.pricing_engine import PricingEngine

pricing = PricingEngine()
fare = pricing.calculate_fare(
    distance=15,
    duration=35,
    service_tier="premier",
    peak_factor=1.25
)

print(f"Total: ${fare['total']}")
print(f"Breakdown:\n{pricing.format_quote(fare)}")
```

---

## 🐛 Troubleshooting

### Issue: "Invalid API Key"
**Solution:** Check your .env file has correct keys from console.anthropic.com

### Issue: ImportError modules not found
**Solution:** Ensure virtual environment is activated: `source venv/bin/activate`

### Issue: Database errors
**Solution:** Check DATABASE_URL in .env, or delete luxury_rideshare.db to reinitialize

### Issue: Wix webhook signature invalid
**Solution:** Verify WIX_WEBHOOK_SECRET matches Wix settings exactly

### Issue: Port 8000 already in use
**Solution:** Change PORT in .env or kill process: `lsof -ti:8000 | xargs kill -9`

---

## 📈 Performance Optimization

### For High Traffic

1. **Database**: Switch to PostgreSQL
2. **Caching**: Add Redis for session caching
3. **Load Balancing**: Use multiple app instances
4. **CDN**: Serve static assets from CDN
5. **Rate Limiting**: Configure with nginx/Caddy

### Configuration

```python
# In .env for production
DATABASE_URL=postgresql://user:pass@host/db
REDIS_URL=redis://localhost:6379
WORKERS=4
```

---

## 📚 Next Steps

### 1. **Integrate with Wix**
   - Add API key and site ID
   - Set up webhook endpoints
   - Embed chat widget

### 2. **Build Frontend**
   - Create booking form UI
   - Connect to `/chat` endpoint
   - Integrate WebSocket chat

### 3. **Configure Payments**
   - Set up Square account
   - Test with sandbox tokens
   - Switch to production

### 4. **Deploy**
   - Push to Git repository
   - Set up CI/CD pipeline
   - Deploy to cloud (AWS, GCP, DigitalOcean)

### 5. **Monitor & Maintain**
   - Set up logging (Sentry, LogRocket)
   - Monitor API performance
   - Track lead conversion metrics

---

## 📞 Support

- **API Documentation**: http://localhost:8000/docs
- **Claude AI**: https://docs.anthropic.com
- **Square Docs**: https://developer.squareup.com/docs
- **FastAPI**: https://fastapi.tiangolo.com

---

## 📄 License

MIT License - See LICENSE file for details

---

**Built with ❤️ for Blu Royal Rides**

Last Updated: April 2026
