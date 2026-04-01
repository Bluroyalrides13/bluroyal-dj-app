# Quick Reference Card

## 🚀 Getting Started (30 seconds)

```bash
cd "Blu Royal Temp"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with API keys
python -m src.main
```

Then visit: **http://localhost:8000/docs**

---

## 📚 Common Commands

### Development
```bash
# Run server
python -m src.main

# Run tests
pytest tests/ -v

# Run examples
python examples.py

# Format code
black src/

# Check types
mypy src/
```

### Docker
```bash
# Build image
docker build -t luxury-rideshare .

# Run container
docker run -p 8000:8000 luxury-rideshare

# Run with compose
docker-compose up -d
docker-compose logs -f app
docker-compose down
```

---

## 💬 Chat API

```bash
# Send message
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "I need a ride", "session_id": "user123"}'

# Get history
curl "http://localhost:8000/chat/history/user123"

# End session
curl -X POST "http://localhost:8000/chat/end/user123"
```

---

## 🚗 Booking API

```bash
# Create booking
curl -X POST "http://localhost:8000/bookings" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "cust_123",
    "pickup_location": "New York City, NY",
    "dropoff_location": "JFK Airport",
    "booking_date": "2026-04-05",
    "booking_time": "14:00",
    "passenger_count": 2,
    "service_tier": "premier",
    "contact_email": "user@example.com"
  }'

# Get booking
curl "http://localhost:8000/bookings/{booking_id}"

# Confirm booking
curl -X POST "http://localhost:8000/bookings/{booking_id}/confirm"

# Cancel booking
curl -X POST "http://localhost:8000/bookings/{booking_id}/cancel"
```

---

## 💰 Pricing API

```bash
# Get quote
curl "http://localhost:8000/quote?distance=10&duration=30&service_tier=premier"

# With peak pricing
curl "http://localhost:8000/quote?distance=10&duration=30&service_tier=vip&peak_factor=1.25"
```

---

## 🔌 WebSocket Chat

```javascript
// Browser console
const sessionId = 'user_' + Date.now();
const ws = new WebSocket(`ws://localhost:8000/ws/chat/${sessionId}`);

// Listen for responses
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log("Agent:", data.response);
  console.log("Lead Score:", data.lead_score);
};

// Send message
ws.send(JSON.stringify({
  type: "chat",
  message: "I need a VIP ride tomorrow"
}));

// End session
ws.send(JSON.stringify({
  type: "end_session"
}));
```

---

## 🔧 Configuration

### .env Variables
```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...
SQUARE_ACCESS_TOKEN=sq_live_...
WIX_API_KEY=wix_...

# Optional
LANGCHAIN_API_KEY=...
DATABASE_URL=sqlite:///luxury_rideshare.db
ENVIRONMENT=development
PORT=8000
LOG_LEVEL=INFO
```

### Service Tiers (in config/settings.py)
```python
{
    "executive": {
        "base_rate": 35.00,
        "per_mile": 3.50,
        "per_minute": 0.65,
    },
    "premier": {
        "base_rate": 50.00,
        "per_mile": 4.50,
        "per_minute": 0.85,
    },
    "vip": {
        "base_rate": 75.00,
        "per_mile": 6.00,
        "per_minute": 1.25,
    }
}
```

---

## 🐍 Python API Examples

### Chat Processing
```python
from src.agent.chat_interface import ChatInterface
from src.models.schemas import ChatMessage

chat = ChatInterface()
msg = ChatMessage(message="I need a ride")
response = chat.process_message(msg)

print(response.response)      # Agent's reply
print(response.lead_score)    # 0-100
print(response.extracted_data) # Captured info
```

### Booking Creation
```python
from src.agent.booking_manager import BookingManager
from src.models.schemas import BookingRequest

manager = BookingManager()
request = BookingRequest(
    customer_id="cust_123",
    pickup_location="New York City, NY",
    dropoff_location="JFK Airport",
    booking_date="2026-04-05",
    booking_time="14:00",
    passenger_count=2,
    service_tier="premier",
    contact_email="user@example.com"
)

booking, quote = manager.create_booking(request)
print(f"Total: ${quote.total_fare}")
```

### Pricing Calculation
```python
from src.agent.pricing_engine import PricingEngine

pricing = PricingEngine()
fare = pricing.calculate_fare(
    distance=10.0,
    duration=30.0,
    service_tier="premier",
    peak_factor=1.0
)

print(f"Total: ${fare['total']}")
print(pricing.format_quote(fare))  # Pretty format
```

### Lead Qualification
```python
from src.agent.lead_qualifier import LeadQualifier

qualifier = LeadQualifier()
conversation = [
    {"role": "user", "content": "I need premium rides NYC"},
    {"role": "assistant", "content": "Welcome!"},
    {"role": "user", "content": "Weekly bookings preferred"},
    {"role": "assistant", "content": "Great!"},
]

scores = qualifier.qualify_lead(conversation)
overall = scores["overall_score"]  # 0-100
```

---

## 📁 File Structure Quick Ref

```
src/
├── agent/
│   ├── chat_interface.py      # Main chat logic
│   ├── lead_qualifier.py      # Lead scoring
│   ├── booking_manager.py     # Booking CRUD
│   └── pricing_engine.py      # Pricing logic
├── integrations/
│   ├── wix_connector.py       # Wix API
│   ├── square_payments.py     # Payments
│   └── calendar_sync.py       # Availability
├── models/
│   ├── schemas.py             # Data models
│   └── database.py            # DB operations
├── api/
│   ├── routes.py              # REST endpoints
│   └── websocket.py           # WebSocket
└── main.py                    # FastAPI app

config/
├── settings.py                # Config & env vars
└── prompts.py                 # Claude prompts

tests/
└── test_agent.py              # Unit tests

examples.py                      # Demo code
```

---

## 🐛 Debugging Tips

### Check API Is Running
```bash
curl http://localhost:8000/health
# Should return: {"status": "healthy", ...}
```

### View API Docs
```
http://localhost:8000/docs        # Swagger UI
http://localhost:8000/redoc       # ReDoc
```

### Check Logs
```bash
# In terminal running server
# Or check docker logs
docker-compose logs -f app
```

### Test Database
```python
from src.models.database import DatabaseManager
db = DatabaseManager()
db.init_db()  # Reset to fresh
```

### Validate Configuration
```python
from config.settings import Settings
settings = Settings()
print(settings.SERVICE_TIERS)
print(settings.CLAUDE_MODEL)
```

---

## ⚡ Performance Tuning

### For Local Development
Keep defaults in .env.example

### For Production
```env
ENVIRONMENT=production
DATABASE_URL=postgresql://...
WORKERS=4
LOG_LEVEL=WARNING
```

### Database Optimization
```bash
# Switch to PostgreSQL
DATABASE_URL=postgresql://user:pass@host/db

# Add indexes (in database.py)
cursor.execute("CREATE INDEX idx_booking_customer ON bookings(customer_id)")
```

---

## 🔐 Security Checklist

- [ ] .env not committed to git
- [ ] API keys rotated monthly
- [ ] HTTPS enabled (production)
- [ ] Database backups enabled
- [ ] CORS configured for your domain
- [ ] Rate limiting enabled
- [ ] Error messages don't expose internals
- [ ] Wix webhook secrets verified
- [ ] Square using production keys on production

---

## 📞 Support Resources

| Topic | Resource |
|-------|----------|
| Claude AI | https://docs.anthropic.com |
| FastAPI | https://fastapi.tiangolo.com |
| Square | https://developer.squareup.com |
| Wix | https://dev.wix.com |
| Docker | https://docs.docker.com |
| SQLite | https://www.sqlite.org/docs.html |
| PostgreSQL | https://www.postgresql.org/docs |

---

## 🎯 Development Workflow

1. **Feature Development**
   ```bash
   git checkout -b feature/my-feature
   # Code...
   pytest tests/
   black src/
   git commit...
   ```

2. **Testing**
   ```bash
   pytest tests/test_agent.py -v
   python examples.py
   ```

3. **Local Deployment**
   ```bash
   python -m src.main
   # Test at http://localhost:8000/docs
   ```

4. **Production Deployment**
   ```bash
   docker-compose -f docker-compose.yml up -d
   ```

---

## 🆘 Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Activate venv: `source venv/bin/activate` |
| `API Key Invalid` | Check .env has correct keys from console |
| `Port 8000 in use` | Change PORT in .env or `lsof -ti:8000 \| xargs kill` |
| `Database locked` | For SQLite, restart app. Use PostgreSQL for production |
| `Claude timeout` | Check ANTHROPIC_API_KEY, API quota |
| `Wix webhook fails` | Verify WIX_WEBHOOK_SECRET exactly matches |
| `Payment declined` | Use sandbox token for testing (SQUARE_ENVIRONMENT=sandbox) |

---

**Bookmark this page for quick reference!**

Last Updated: April 2026
