# Luxury Ride Share Agent

A sophisticated AI-powered ride share service platform built with Claude, LangChain, and FastAPI. Designed specifically for luxury ride booking with intelligent lead qualification, dynamic pricing, and seamless Wix/Square integration.

## 🎯 Features

### 🤖 AI Agent
- **Claude Integration**: Multi-turn conversations with context awareness
- **Lead Qualification**: Automatic scoring based on budget, frequency, location, and preferences
- **Natural Language Understanding**: Capture booking requirements through conversation
- **Conversation Memory**: Persistent chat history with state tracking

### 📱 Chat & Messaging
- **Real-time WebSocket Chat**: Live communication with customers
- **Wix Integration**: Native chat embed for Wix websites
- **Multi-channel**: Support for web chat, Wix chat, and API-driven interactions
- **Session Management**: Track and manage conversation sessions

### 🚗 Booking Management
- **Reservation System**: Create, confirm, modify, and cancel bookings
- **Real-time Quotes**: Generate accurate pricing instantly
- **Availability Management**: Track vehicle availability and schedule
- **Confirmation Tracking**: Unique confirmation numbers for each booking

### 💰 Pricing & Payments

**Service Tiers:**
- **Executive**: $35 base fare - Professional business rides
- **Premier**: $50 base fare - Premium luxury experience
- **VIP**: $75 base fare - Ultimate luxury service

**Dynamic Pricing:**
- Distance-based charges (per mile)
- Time-based surcharges (per minute)
- Peak time multipliers (1.25x - 1.5x during busy hours)
- Loyalty discounts for repeat customers
- Promotional code support
- Tax calculation (8%)

### 💳 Payment Integration
- **Square**: Full payment processing support
- **Multiple Payment Methods**: Card, Apple Pay, Google Pay
- **Refund Handling**: Full and partial refund support
- **Customer Profiles**: Secure Square customer records

### 🔗 Wix Integration
- **Webhook Support**: Real-time event handling
- **Chat Embed**: Integrate chat directly into Wix sites
- **Contact Sync**: Automatic contact creation and updates
- **Form Submissions**: Capture booking inquiries from web forms
- **Signature Verification**: Secure webhook validation

## 📋 Project Structure

```
luxury-rideshare-agent/
├── src/
│   ├── agent/
│   │   ├── lead_qualifier.py       # Lead scoring & qualification
│   │   ├── booking_manager.py      # Reservation management
│   │   ├── chat_interface.py       # Multi-turn conversations
│   │   └── pricing_engine.py       # Dynamic pricing
│   ├── integrations/
│   │   ├── wix_connector.py        # Wix API integration
│   │   ├── square_payments.py      # Square payment processing
│   │   └── calendar_sync.py        # Availability management
│   ├── models/
│   │   ├── schemas.py              # Pydantic data models
│   │   └── database.py             # SQLite operations
│   ├── api/
│   │   ├── routes.py               # REST endpoints
│   │   └── websocket.py            # WebSocket chat
│   └── main.py                     # FastAPI application
├── config/
│   ├── settings.py                 # Configuration management
│   └── prompts.py                  # Claude system prompts
├── tests/
│   └── test_agent.py               # Unit tests
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment template
└── README.md                       # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Anthropic API key (Claude)
- Square account (for payments)
- Wix site (for integration)

### 1. Clone & Setup

```bash
git clone https://github.com/blueroyalrides13/luxury-rideshare-agent.git
cd luxury-rideshare-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy .env template
cp .env.example .env

# Edit .env with your credentials
# ANTHROPIC_API_KEY=...
# SQUARE_ACCESS_TOKEN=...
# WIX_API_KEY=...
# etc.
```

### 3. Run the Server

```bash
# Development
python -m src.main

# Production
uvicorn src.main:app --host 0.0.0.0 --port 8000

# With auto-reload
uvicorn src.main:app --reload
```

Server runs on `http://localhost:8000`

### 4. API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI)

## 📚 API Endpoints

### Chat
- `POST /chat` - Send message to agent
- `GET /chat/history/{session_id}` - Get conversation history
- `POST /chat/end/{session_id}` - End session and create lead
- `WS /ws/chat/{session_id}` - WebSocket for real-time chat

### Bookings
- `POST /bookings` - Create new booking
- `GET /bookings/{booking_id}` - Get booking details
- `POST /bookings/{booking_id}/confirm` - Confirm booking
- `POST /bookings/{booking_id}/cancel` - Cancel booking

### Quotes & Pricing
- `GET /quote` - Generate pricing quote

### Webhooks
- `POST /webhooks/wix/chat` - Wix chat webhook
- `POST /webhooks/wix/contact` - Wix contact webhook

### System
- `GET /health` - Health check
- `GET /status` - API status

## 💬 Chat Examples

### Basic Booking
```
User: "I need a ride from NYC to the airport"
Agent: "Welcome to Blu Royal Rides! I'd be happy to help. When would you like your ride?"
User: "Tomorrow at 2pm for 2 people, VIP please"
Agent: [Generates quote and confirms booking details]
```

### Lead Qualification
```
User: "We need regular rides for our executives"
Agent: "Great! How many rides per month are you thinking?"
User: "About 10-15 per month across our team"
Agent: [High-quality lead - scores well on frequency and budget]
```

## 🔧 Configuration

### Service Tiers
Edit `config/settings.py` to customize:
```python
SERVICE_TIERS: dict = {
    "executive": {
        "base_rate": 35.00,
        "per_mile": 3.50,
        "per_minute": 0.65,
        # ...
    },
    # ...
}
```

### Supported Cities
```python
SUPPORTED_CITIES: List[str] = [
    "New York City, NY",
    "Los Angeles, CA",
    "Chicago, IL",
    "Miami, FL",
]
```

### Lead Scoring
```python
LEAD_SCORING: dict = {
    "budget_weight": 0.25,
    "frequency_weight": 0.25,
    "location_weight": 0.20,
    "service_preference_weight": 0.20,
    "engagement_weight": 0.10,
    "high_quality_threshold": 70,
}
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src

# Run specific test
pytest tests/test_agent.py::TestLeadQualifier -v
```

## 🔐 Security

### Webhook Verification
Wix webhooks are verified using HMAC-SHA256:
```python
# Automatically handled in routes.py
if not wix.verify_webhook_signature(signature, body):
    raise HTTPException(status_code=401, detail="Invalid signature")
```

### Environment Variables
- Never commit `.env` file
- Keep API keys secure in environment
- Use different keys for dev/production

### CORS Configuration
Configure allowed origins in `config/settings.py`:
```python
CORS_ORIGINS: List[str] = [
    "http://localhost:3000",
    "https://yourdomain.com",
]
```

## 📊 Database

### SQLite (Development)
Automatically created at `luxury_rideshare.db`

Tables:
- `leads` - Lead records with qualification scores
- `customers` - Customer profiles
- `bookings` - Ride booking records
- `quotes` - Pricing quotes
- `conversation_sessions` - Chat history
- `payments` - Payment records

### PostgreSQL (Production)
```python
# In .env
DATABASE_URL=postgresql://user:password@host:5432/luxury_rideshare
```

## 🎯 Claude System Prompt

The agent uses a comprehensive system prompt defined in `config/prompts.py`:

- Professional, luxurious tone
- Lead qualification framework
- Booking capture logic
- Multi-turn conversation management
- Escalation handling

## 🚀 Deployment

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Setup (Production)
```bash
ENVIRONMENT=production
PYTHONUNBUFFERED=1
PORT=8000
SECURE_COOKIES=true
HTTPS_ONLY=true
```

## 📞 Support & Integration

### Wix Chat Integration
1. Go to Wix Site Settings
2. Add custom code to embed chat widget:
   ```html
   <script>
   const sessionId = generateUUID();
   const ws = new WebSocket(`wss://your-api.com/ws/chat/${sessionId}`);
   ws.onmessage = (event) => {
       const data = JSON.parse(event.data);
       displayChatMessage(data.response);
   };
   </script>
   ```

### Square Integration
- Generate API key in Square Dashboard
- Set `SQUARE_ENVIRONMENT` to `sandbox` for testing
- Use `production` for live payments

## 🐛 Troubleshooting

### Claude API Errors
- Check `ANTHROPIC_API_KEY` is valid
- Verify API key has required permissions
- Check rate limits (Claude API)

### Wix Webhook Issues
- Verify `WIX_WEBHOOK_SECRET` is correct
- Check webhook URL is publicly accessible
- Test webhook signature verification

### Payment Failures
- Ensure `SQUARE_ACCESS_TOKEN` is valid
- Check `SQUARE_ENVIRONMENT` setting
- Verify amount is in cents (e.g., $10.00 = 1000 cents)

## 📝 Contributing

1. Fork repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🎓 Architecture Notes

### Agent Flow
```
Customer Message → Chat Interface → Claude AI → Response Generation
                                  ↓
                            Lead Qualifier
                                  ↓
                            Extract Data
                                  ↓
                            Update Conversation State
```

### Booking Flow
```
Chat Extraction → Booking Manager → Pricing Engine → Quote Generation
                                              ↓
                                        Square Payment → Confirmation
```

## 🗺️ Roadmap

- [ ] Multi-language support
- [ ] Advanced driver matching algorithm
- [ ] Real-time GPS tracking
- [ ] Native mobile app (iOS/Android)
- [ ] Advanced analytics dashboard
- [ ] Stripe payment integration
- [ ] Calendar sync (Google Calendar, Outlook)
- [ ] CRM integration (HubSpot, Salesforce)

---

**Built with ❤️ for Blu Royal Rides**
