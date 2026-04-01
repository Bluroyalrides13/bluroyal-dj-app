# Project Architecture & Design Documentation

## System Overview

The Luxury Ride Share Agent is a multi-component system designed to handle end-to-end ride booking with AI-driven lead qualification and dynamic pricing.

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│  (Wix Chat Widget, Web Frontend, Mobile App)                    │
└────────────────────┬────────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
    REST API    WebSocket    Webhooks
        │            │            │
┌───────┴────────┬──┴──────┬─────┴──────────────────────────────┐
│                          API LAYER                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  FastAPI Application (src/main.py)                       │  │
│  │  ├── Routes (routes.py) - REST endpoints                │  │
│  │  ├── WebSocket (websocket.py) - Real-time chat          │  │
│  │  └── CORS/Security middleware                           │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────┬──────────────────┬──────────────────┬───────────────┘
            │                  │                  │
    ┌───────┴──────┐   ┌──────┴──────┐   ┌──────┴──────────┐
    │              │   │             │   │                 │
┌───▼─┐  ┌────────┴┐  │   ┌────────┐│   │  ┌──────────┐   │
│AGENT│  │BOOKING  │  │   │PRICING ││   │  │INTEGR    │   │
│LAYER│  │MANAGER  │  │   │ENGINE  ││   │  │ATIONS    │   │
└──┬──┘  └────┬────┘  │   └────┬───┘│   │  └────┬─────┘   │
   │           │      │        │    │   │       │         │
   │       ┌───┴──────┴────────┴────┴───┴──┐    │         │
   │       │                                │    │         │
  ┌┴───┐ ┌─▼────────────────────────────────┴┐   │         │
  │    │ │     LEAD QUALIFIER                │   │         │
  │    │ │  (lead_qualifier.py)              │   │         │
  │    │ │  - Score prospects                │   │         │
  │    │ │  - Classify leads                 │   │         │
  │    │ │  - Track engagement               │   │         │
  │    │ └────────────┬──────────────────────┘   │         │
  │    │              │                           │         │
  │ C  │  CHAT INTERFACE                         │         │
  │ L  │  (chat_interface.py)                    │SQUARE  │
  │ A  │  - Conversation management              │PAYMENTS│
  │ U  │  - Message extraction                   │ & WIX  │
  │ D  │  - State tracking                       │WEBHOOKS│
  │ E  │                                          │         │
  │    │  BOOKING MANAGER                        │         │
  │    │  (booking_manager.py)                   │         │
  │    │  - Create, confirm, cancel              │         │
  │    │  - Generate quotes                      │         │
  │    │                                          │         │
  │    │  PRICING ENGINE                        │         │
  │    │  (pricing_engine.py)                   │         │
  │    │  - Dynamic pricing                     │         │
  │    │  - Discounts & promos                 │         │
  └────┘                                         │         │
       └─────────────────────────────────────────┴─────┬───┘
                                                      │
                    ┌─────────────────────────────────┼────────────┐
                    │                                 │            │
            ┌───────┴────────┐              ┌────────┴──────┐   ┌─┴──────┐
            │  DATABASE      │              │  THIRD PARTY  │   │ SERVICE│
            │  LAYER         │              │  INTEGRATIONS │   │ CONFIG │
            │                │              │               │   │        │
   ┌────────┴─────┬──────────┴────────┐   │               │   │        │
   │              │                   │   │               │   │        │
┌──┴──┐  ┌───────┴──┐  ┌────────────┐│   │               │   │        │
│USERS│  │LEADS     │  │BOOKINGS    ││   │ Wix API ──► │WEB │
│CUST │  │SESSIONS  │  │QUOTES      ││   │Square API────►CHAT   │
│PROF │  │PAYMENTS  │  │HISTORY     ││   │ Claude API──►CONFIG │
└────┘  │          │  │            ││   │               │     │
        └──────────┴──┴────────────┬┘│   │               │     │
        │                          │ │   │               │     │
     SQLite              ┌─────────┴─┴───┴───────────────┴─────┘
     (Dev)              │
                    PostgreSQL
                    (Production)
```

## Component Details

### 1. AI Agent Layer (`src/agent/`)

#### ChatInterface (`chat_interface.py`)
- **Purpose**: Manages multi-turn conversations with customers
- **Key Features**:
  - Maintains conversation state and history
  - Integrates with Claude AI
  - Extracts booking data from messages
  - Tracks lead qualification in real-time
- **Data Flow**:
  ```
  User Message → Conversation History → Claude API → 
  Response + Extraction + Lead Score
  ```

#### LeadQualifier (`lead_qualifier.py`)
- **Purpose**: AI-powered lead scoring and classification
- **Scoring Dimensions**: (weighted)
  - Budget (25%): Spending capacity
  - Frequency (25%): Booking regularity
  - Location (20%): Geographic match
  - Preference (20%): Service tier choice
  - Engagement (10%): Communication quality
- **Outputs**:
  - Overall score (0-100)
  - Recommendation (qualified/unqualified)
  - Suggested tier (executive/premier/vip)

#### BookingManager (`booking_manager.py`)
- **Purpose**: Handles full booking lifecycle
- **Operations**:
  - Create booking from request
  - Validate minimum advance notice (2 hours)
  - Generate accurate quotes
  - Confirm/modify/cancel reservations
  - Track booking status
- **Status Flow**: `quoted` → `confirmed` → `payment_pending` → `paid` → `scheduled` → `in_progress` → `completed`

#### PricingEngine (`pricing_engine.py`)
- **Purpose**: Dynamic pricing calculations
- **Pricing Components**:
  - **Base Fare**: Tier-dependent (Executive $35, Premier $50, VIP $75)
  - **Distance Charge**: per_mile × distance
  - **Time Charge**: per_minute × duration
  - **Peak Multiplier**: 1.0 (normal) - 1.5 (peak)
  - **Discounts**: Loyalty, bulk, promotional
  - **Tax**: 8% on subtotal
- **Peak Hours**: M-F: 7-10am, 12-1pm, 4-7pm
- **Special Offers**: Promo codes, loyalty program

### 2. Integration Layer (`src/integrations/`)

#### WixConnector (`wix_connector.py`)
- **Purpose**: Two-way Wix integration
- **Capabilities**:
  - Send/receive chat messages
  - Create/update contacts
  - Verify webhook signatures (HMAC-SHA256)
  - Handle form submissions
  - Add labels to contacts
- **Webhook Events**:
  - `chat_message`: Customer sends message
  - `contact_created`: New contact formed
  - `form_submission`: Booking inquiry form

#### SquarePaymentProcessor (`square_payments.py`)
- **Purpose**: Secure payment processing
- **Operations**:
  - Create payment from card/wallet
  - Process payment through Square API
  - Handle refunds (full/partial)
  - Create customer profiles
  - Retrieve payment receipts
- **Sandbox Testing**: Test with fake card 4111 1111 1111 1111

#### AvailabilityManager (`calendar_sync.py`)
- **Purpose**: Manage ride availability
- **Features**:
  - Check time window availability
  - Block unavailable times
  - Generate available time windows
  - Support for multi-driver scheduling

### 3. API Layer (`src/api/`)

#### Routes (`routes.py`)
**Chat Endpoints**:
- `POST /chat` - Send message to agent
- `GET /chat/history/{session_id}` - Get conversation
- `POST /chat/end/{session_id}` - End session

**Booking Endpoints**:
- `POST /bookings` - Create booking
- `GET /bookings/{booking_id}` - Get details
- `POST /bookings/{booking_id}/confirm` - Confirm
- `POST /bookings/{booking_id}/cancel` - Cancel

**Pricing**:
- `GET /quote?distance=X&duration=Y&service_tier=Z` - Price quote

**Webhooks**:
- `POST /webhooks/wix/chat` - Chat webhook
- `POST /webhooks/wix/contact` - Contact webhook
- `POST /webhooks/wix/form` - Form submission webhook

#### WebSocket (`websocket.py`)
- **Purpose**: Real-time chat communication
- **Connection**: `ws://api.com/ws/chat/{session_id}`
- **Messages**:
  ```json
  // Client → Server
  {"type": "chat", "message": "Hello"}
  
  // Server → Client  
  {"type": "response", "response": "...", "lead_score": 75}
  ```

### 4. Data Models (`src/models/`)

#### Schemas (`schemas.py`)
Key Pydantic models:
- `ChatMessage`: Incoming chat messages
- `ChatResponse`: Agent responses
- `BookingRequest`: Booking creation
- `Booking`: Complete booking record
- `BookingQuote`: Price quote
- `Lead`: Qualified lead record
- `ConversationSession`: Chat session tracking
- `PaymentIntent`: Square payment

#### Database (`database.py`)
**Tables**:
- `leads`: Prospect records with scores
- `customers`: Customer profiles
- `bookings`: Ride reservations
- `quotes`: Pricing quotes
- `conversation_sessions`: Chat history
- `payments`: Payment transactions

**SQL Operations**:
- Create/read/update leads
- Manage bookings
- Store conversation history
- Track payments

### 5. Configuration (`config/`)

#### Settings (`settings.py`)
- Environment variables
- Service tier definitions
- API credentials
- Database URL
- Supported cities
- Lead scoring weights

#### Prompts (`prompts.py`)
- Claude system prompt (professional, luxury tone)
- Lead qualification template
- Booking confirmation format
- Pricing quote template
- Escalation instructions

## Request Flow Examples

### Example 1: Chat → Booking → Quote → Payment

```
1. Customer Chat
   User: "I need a VIP ride NYC to JFK tomorrow 2pm"
   ↓
2. ChatInterface Process
   - Extract: location, tier, time
   - Score lead via LeadQualifier (85/100 = qualified)
   - Update conversation state
   ↓
3. BookingManager Create
   - Validate 2-hour advance notice ✓
   - Call BookingRequest creation
   ↓
4. PricingEngine Quote
   - Distance estimate: 15 miles
   - Duration estimate: 35 minutes
   - VIP rates: $75 + $90 + $36.75 + tax = $217.58
   ↓
5. Display Quote
   - Return booking with quote
   - Wait for payment confirmation
   ↓
6. Square Payment
   - Customer provides card
   - Square processes payment
   - Store payment_id in booking
   ↓
7. Confirmation
   - Send confirmation email
   - Update booking status: "scheduled"
   - Notify driver (future feature)
```

### Example 2: Wix Webhook → Chat Session → Lead Creation

```
1. Wix Chat Widget
   Customer sends: "Need executive rides NYC"
   ↓
2. Webhook Received
   POST /webhooks/wix/chat
   - Verify signature
   - Extract contact_id, message
   ↓
3. Process Message
   ChatInterface.process_message()
   - Generate response
   - Calculate lead_score
   ↓
4. Send Back to Wix
   wix.send_chat_message(response)
   ↓
5. Continue Conversation
   (Multi-turn until qualified or escalated)
   ↓
6. Create Lead (if qualified)
   - Save to database
   - Assign to sales team
   - Tag in Wix
```

## Performance Characteristics

### Throughput
- **Chat API**: ~100 req/sec (FastAPI limit)
- **Claude API**: ~5 req/sec (Anthropic limit)
- **Database**: SQLite ~1000 op/sec → PostgreSQL ~5000 op/sec

### Latency
- Chat response: 2-5 seconds (Claude)
- Quote generation: <500ms
- WebSocket: <100ms

### Scale Considerations
- Vertical (single machine): SQLite + Uvicorn workers
- Horizontal (multi-machine): PostgreSQL + Redis + Load Balancer

## Security Architecture

### Input Validation
- Pydantic schema validation
- Email validation
- Phone number validation
- Service tier enum checking

### Integration Security
- **Wix**: HMAC-SHA256 webhook verification
- **Square**: API key stored in environment
- **Claude**: API key validation
- **Database**: SQL injection prevention (parameterized queries)

### API Security
- CORS configuration
- Rate limiting (at reverse proxy)
- HTTPS enforcement (production)
- Secure cookie flags

## Error Handling

### Strategy
1. **Validation Errors**: Return 400 with message
2. **Auth Errors**: Return 401/403
3. **Not Found**: Return 404
4. **Server Errors**: Return 500, log error
5. **AI Errors**: Return graceful fallback response

### Example Error Response
```json
{
  "success": false,
  "message": "Error processing booking",
  "error": "Booking must be 2+ hours in advance"
}
```

## Database Relationships

```
Customers
  ├── Bookings (1:Many)
  │   ├── Quotes (1:1)
  │   └── Payments (1:1)
  └── ConversationSessions (1:Many)

Leads
  └── ConversationSessions (1:Many)
```

## Extensibility Points

### Adding New Features

1. **New Chat Capability**:
   ```python
   # Edit chat_interface.py
   # Add extraction logic
   # Call appropriate manager
   ```

2. **New Service Tier**:
   ```python
   # Edit config/settings.py
   # Add to SERVICE_TIERS dict
   ```

3. **New Integration**:
   ```python
   # Create src/integrations/new_service.py
   # Import in routes.py
   # Add webhook endpoint
   ```

4. **New Price Rule**:
   ```python
   # Edit pricing_engine.py
   # Add to calculate_fare() or get_peak_factor()
   ```

---

**Architecture designed for scalability, maintainability, and clear separation of concerns.**
