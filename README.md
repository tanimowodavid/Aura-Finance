# 💰 Aura Finance - AI-Powered Savings Coach

> An AI-driven Telegram bot that provides personalized financial coaching to help users build bulletproof saving habits.

## 🎯 Overview

Aura Finance is an intelligent financial companion that meets users where they are—on Telegram. Using advanced LLM technology, it delivers personalized savings strategies, tracks financial progress, and provides behavioral coaching tailored to individual goals and patterns.

**Key Challenge Solved**: Many people struggle to build consistent saving habits due to lack of personalized guidance and accountability. Aura solves this through conversational AI that adapts to each user's unique financial context and behavioral needs.

## ✨ Features

### 🤖 AI-Powered Coaching

- Natural language conversations powered by LLM (LiteLLM for multi-model support)
- Contextual understanding of user financial situations
- Personalized action plans based on behavioral analysis

### 📋 Smart Onboarding

- Interactive guided setup to understand user's financial goals and constraints
- Captures motivation, current savings level, and preferred check-in frequency
- Establishes baseline for personalized coaching

### 📊 Progress Audits (Check-ins)

- Regular check-ins on user-defined schedules (daily, weekly, bi-weekly, monthly)
- Velocity tracking—measures savings growth between audits
- Behavioral pattern recognition to identify spending triggers
- Dynamic feedback adapted to performance (up, neutral, or down)

### 💬 Multi-Session Chat Management

- Separate conversation contexts for:
  - **Onboarding**: Initial setup and profile creation
  - **Check-ins**: Progress tracking and habit reinforcement
  - **General**: Anytime coaching and financial questions
- Full chat history logging for context continuity

### 📲 Telegram Integration

- Seamless Telegram webhook integration
- Real-time message processing
- Easy for users—no app downloads needed

## 🚀 How It Works

```
User sends message
    ↓
Django webhook receives message
    ↓
Route based on user state:
    ├─ If not onboarded → Onboarding flow
    ├─ If check-in requested → Check-in flow
    └─ Otherwise → General coaching
    ↓
LLM processes with conversation history
    ↓
Tool calling capability:
    ├─ finalize_onboarding: Creates financial profile
    └─ finish_check_in: Logs transaction, calculates velocity
    ↓
Personalized response sent back to user
```

## 🛠️ Tech Stack

- **Backend**: Django 6.0.1
- **LLM Integration**: LiteLLM (supports OpenAI, Claude, Bedrock, etc.)
- **Database**: PostgreSQL (via dj-database-url)
- **Message Queue**: Celery + RabbitMQ (for async reminders)
- **Deployment**: Render.com
- **Bot Platform**: Telegram Bot API

## 📁 Project Structure

```
aura/                    # Main app with core logic
├── services/
│   ├── aura.py         # Chat processing & routing
│   ├── llm.py          # LLM model configurations
│   ├── prompts.py      # System prompts for different flows
│   └── tools.py        # Tool handlers (onboarding, check-in)
├── models.py           # ChatMessageLog model
├── views.py            # Telegram webhook endpoint
└── utils.py            # Utility functions

users/                   # User management
├── models.py           # User & FinancialProfile models
└── views.py            # User-related endpoints

aura_core/              # Django project config
├── settings.py         # Project settings
├── urls.py             # URL routing
└── wsgi.py             # WSGI config
```

## 🎮 Usage

### For Users (via Telegram):

1. Start chatting with the bot: `/start`
2. Complete the onboarding questionnaire
3. Receive personalized savings coaching
4. Check in regularly to track progress
5. Get reminders and behavioral insights

### For Developers:

1. **Setup** (see Installation below)
2. **Add credentials**: Set environment variables (LLM API key, Telegram token, database URL)
3. **Environment Variables**:
   ```bash
   SECRET_KEY=your-django-secret
   DEBUG=True (development only)
   TELEGRAM_BOT_TOKEN=your-token
   DATABASE_URL=your-database-url
   OPENAI_API_KEY=your-key  # or other LLM provider
   ```

## 💾 Installation & Setup

### Prerequisites

- Python 3.9+
- PostgreSQL (or SQLite for development)
- Telegram Bot Token (from @BotFather)

### Local Development

```bash
# Clone the repository
git clone <repo-url>
cd Aura-Finance

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env  # Edit with your credentials

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver

# In another terminal, start Celery (for async tasks)
celery -A aura_core worker -l info
```

### Deploy to Render

1. Push to GitHub
2. Connect repository to Render
3. Set environment variables in Render dashboard
4. Deploy!

## 🔄 Key Endpoints

| Endpoint               | Method | Description                                 |
| ---------------------- | ------ | ------------------------------------------- |
| `/aura/telegram/`      | POST   | Telegram webhook (receives messages)        |
| `/aura/run-reminders/` | GET    | Trigger check-in reminders (scheduled task) |

## 🧠 The AI Engine

### LLM Models Used

- **Onboarding**: Specialized model to understand financial situation, goals, and constraints
- **Check-in**: Analyzes spending patterns, calculates velocity, suggests adjustments
- **General**: Provides flexible financial coaching and answers questions

### Tool Calling

The LLM can invoke two main tools:

1. **finalize_onboarding**: Commits user profile after onboarding
2. **finish_check_in**: Records check-in, calculates savings velocity, generates action plans

## 📈 Data Models

### User

- `telegram_id`: Unique Telegram identifier
- `is_onboarded`: Onboarding completion status
- `is_in_checkin`: Current check-in state

### FinancialProfile

- `estimated_savings`: Current total savings
- `motivation`: Why they want to save
- `check_in_frequency`: How often to audit (daily/weekly/bi-weekly/monthly)
- `behavioral_tag`: AI-identified spending pattern
- `action_plan`: Personalized savings strategy
- `financial_context`: Flexible AI-friendly notes

### ChatMessageLog

- Stores all conversations for context retention
- Separated by session type (onboarding, check-in, general)
- Enables continuous context learning

### Challenges Tackled

- ✅ Building conversational AI that understands financial context
- ✅ Creating actionable behavioral insights from chat
- ✅ Integrating LLM tool calling for profile creation & check-ins
- ✅ Managing multi-stage user journeys (onboarding → check-ins → general coaching)
- ✅ Real-time Telegram bot integration

### Future Enhancements

- 📊 Dashboard for detailed financial analytics
- 🎯 Gamification (streaks, badges for savings milestones)
- 💳 Integration with banking APIs for transaction auto-logging
- 🌍 Multi-language support
- 👥 Social sharing and accountability groups
- 📱 Native mobile app alongside Telegram bot

## 📝 License

MIT

---

**Made with ❤️ and AI-powered insights for better saving habits**
