# Luxury Ride Share Agent - Workspace Instructions

This workspace contains a comprehensive AI-powered luxury ride share booking system built with Claude, LangChain, and FastAPI.

## Project Overview

**Luxury Ride Share Agent** is an intelligent booking platform that combines:
- Claude AI for natural language conversations and lead qualification
- FastAPI for high-performance REST APIs and WebSocket support
- Square payments for secure payment processing
- Wix integration for seamless website embedding
- SQLite database for lead and booking management

## Key Components

### 1. AI Agent (`src/agent/`)
- **lead_qualifier.py**: Claude-powered lead scoring based on budget, frequency, location, preferences
- **chat_interface.py**: Multi-turn conversations with context tracking
- **booking_manager.py**: Reservation creation, modification, cancellation
- **pricing_engine.py**: Dynamic pricing with peak rates, discounts, and promo codes

### 2. Integrations (`src/integrations/`)
- **wix_connector.py**: Wix API integration, webhook handling, chat embedding
- **square_payments.py**: Payment processing, customer profiles, refunds
- **calendar_sync.py**: Availability management and scheduling

### 3. API Layer (`src/api/`)
- **routes.py**: REST endpoints for chat, bookings, quotes, webhooks
- **websocket.py**: Real-time WebSocket chat for live conversations
- **main.py**: FastAPI application management

### 4. Data Models (`src/models/`)
- **schemas.py**: Pydantic data models for validation
- **database.py**: SQLite database operations and schema

## Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys:
# - ANTHROPIC_API_KEY (Claude)
# - SQUARE_ACCESS_TOKEN (Square)
# - WIX_API_KEY (Wix)
```

### 3. Start the Server
```bash
python -m src.main
# Server runs on http://localhost:8000
```

### 4. Access API
- **Interactive Docs**: http://localhost:8000/docs
- **Chat Endpoint**: POST /chat
- **WebSocket Chat**: WS /ws/chat/{session_id}
- **Health Check**: GET /health

## Service Tiers

- **Executive** ($35 base): Professional business rides
- **Premier** ($50 base): Premium luxury service
- **VIP** ($75 base): Ultimate luxury experience

## Supported Cities

- New York City, NY
- Los Angeles, CA
- Chicago, IL
- Miami, FL

## Development Workflow

### Running Tests
```bash
pytest tests/ -v
```

### Code Style
```bash
black src/
flake8 src/
mypy src/
```

### Adding New Features

1. **Chat Capabilities**: Extend `src/agent/chat_interface.py`
2. **Pricing Logic**: Modify `src/agent/pricing_engine.py`
3. **Integrations**: Add to `src/integrations/`
4. **API Endpoints**: Extend `src/api/routes.py`

## Common Tasks

### Create a New Booking
```python
from src.agent.booking_manager import BookingManager
from src.models.schemas import BookingRequest

manager = BookingManager()
request = BookingRequest(
    customer_id="cust_123",
    pickup_location="New York City, NY",
    dropoff_location="JFK Airport",
    booking_date="2026-04-15",
    booking_time="14:00",
    passenger_count=2,
    service_tier="premier",
    contact_email="customer@example.com"
)
booking, quote = manager.create_booking(request)
```

### Process a Chat Message
```python
from src.agent.chat_interface import ChatInterface
from src.models.schemas import ChatMessage

chat = ChatInterface()
message = ChatMessage(message="I need a ride to the airport")
response = chat.process_message(message)
print(response.response)  # Agent's reply
print(response.lead_score)  # Qualification score
```

### Generate a Pricing Quote
```python
from src.agent.pricing_engine import PricingEngine

pricing = PricingEngine()
fare = pricing.calculate_fare(
    distance=10.0,
    duration=30.0,
    service_tier="premier"
)
print(f"Total: ${fare['total']}")
```

### Create a Square Payment
```python
from src.integrations.square_payments import SquarePaymentProcessor

processor = SquarePaymentProcessor()
result = processor.create_payment(
    amount_cents=5000,  # $50.00
    source_id="nonce_from_form",
    booking_id="booking_123",
    customer_email="customer@example.com",
    idempotency_key="unique_key"
)
```

## Configuration Files

### `config/settings.py`
- API host/port
- Claude model selection
- Service tier pricing
- Supported cities
- Lead scoring weights
- Payment processor keys

### `config/prompts.py`
- Claude system prompt
- Lead qualification prompt
- Booking confirmation prompt
- Pricing quote format
- Escalation template

### `.env.example`
Template for environment variables. Create `.env` with actual values.

## Database Schema

### leads
- Lead qualification records with scoring
- Tracks prospect engagement and conversion status

### customers
- Customer profiles
- Booking history and spending
- VIP status

### bookings
- Reservation records
- Quotes and confirmation numbers
- Payment status tracking

### quotes
- Pricing details for each booking
- Fare breakdown

### conversation_sessions
- Chat history
- Extracted data from conversations

### payments
- Payment transaction records
- Square payment IDs

## Wix Integration Setup

1. **Get Wix API Credentials**:
   - Site ID from Wix dashboard
   - API key from Developer Center

2. **Set Webhook URLs**:
   - Chat: `https://your-api.com/webhooks/wix/chat`
   - Contacts: `https://your-api.com/webhooks/wix/contact`

3. **Add Chat Widget to Wix**:
   ```html
   <script>
   const sessionId = 'wix_' + Date.now();
   const ws = new WebSocket('wss://your-api.com/ws/chat/' + sessionId);
   ws.onmessage = (e) => {
       const data = JSON.parse(e.data);
       // Display agent response in chat widget
   };
   </script>
   ```

## Square Integration Setup

1. **Get Square API Key**:
   - Create account at square.com
   - Generate API key in Developer Dashboard
   - Use sandbox for testing

2. **Payment Flow**:
   ```
   Customer enters payment info → Square tokenizes → 
   Agent calls processor.create_payment() → 
   Transaction processed → Confirmation sent
   ```

## Production Deployment

### Environment
```bash
ENVIRONMENT=production
PYTHONUNBUFFERED=1
```

### Database
Switch from SQLite to PostgreSQL:
```bash
DATABASE_URL=postgresql://user:password@host:5432/luxury_rideshare
```

### Server
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Troubleshooting

### Claude API Issues
- Verify `ANTHROPIC_API_KEY` is correct
- Check API quota and rate limits
- Review Claude documentation for model updates

### Webhook Signature Errors
- Ensure `WIX_WEBHOOK_SECRET` matches Wix settings
- Verify webhook is using correct endpoint URL

### Payment Failures
- Check `SQUARE_ACCESS_TOKEN` is valid
- Ensure amount is in cents (e.g., $10 = 1000 cents)
- Toggle `SQUARE_ENVIRONMENT` between sandbox/production

## Next Steps

1. Configure `.env` with your API keys
2. Install dependencies: `pip install -r requirements.txt`
3. Start server: `python -m src.main`
4. Test endpoints at http://localhost:8000/docs
5. Integrate Wix chat widget into your website
6. Deploy to production (Docker/Cloud Platform)

---

For more details, see [README.md](README.md)
