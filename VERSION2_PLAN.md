# RemindMe — Version 2 Plan

## Goals

1. Add LLM-powered intent routing for better natural language understanding
2. Improve reminder parsing accuracy
3. Add recurring reminders (daily, weekly, monthly)
4. Address TA feedback from Version 1 demo

## LLM Integration

### Architecture

The LLM will be used as a tool-calling agent that:

1. Receives user message
2. Decides intent: `create_reminder`, `list_reminders`, `delete_reminder`, `help`, `general_chat`
3. Extracts structured data for reminders (text, datetime, recurrence)
4. Calls appropriate handler

### Implementation

- Add `llm_router.py` service that calls OpenRouter API
- Use function calling to extract reminder data
- Fallback to regex parser if LLM is unavailable

### Environment Variables

```
LLM_API_KEY=your_openrouter_api_key
LLM_API_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=google/gemma-3-4b-it
```

## Recurring Reminders

### Database Schema

Add `recurrence` column to reminders table:

```sql
ALTER TABLE reminders ADD COLUMN recurrence VARCHAR(20) DEFAULT NULL;
-- Values: NULL, 'daily', 'weekly', 'monthly'
```

### Logic

When a recurring reminder is sent:
1. Mark current as sent
2. Create next occurrence based on recurrence pattern

## TA Feedback Points

(To be filled after Version 1 demo)

## Deployment

- Add LLM API key to `.env.secret`
- Update Docker Compose if needed
- Update README with new features
