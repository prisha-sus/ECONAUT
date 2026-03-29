# LLM API Fallback System - Production Guide

## Overview
The ET AI Concierge now includes a robust LLM API fallback system to handle rate limits, API outages, and provider failures gracefully.

## How It Works

### Automatic Fallback Priority
1. **Groq** (Primary) - Fast, cost-effective
2. **Google Gemini** (Secondary) - Reliable backup
3. **Local Ollama** (Tertiary) - Offline fallback
4. **Emergency Fallback** (Last Resort) - Returns helpful error messages

### Key Features

#### 🔄 Automatic Switching
- Detects API failures automatically
- Switches to next available provider seamlessly
- No user interruption during transitions

#### 🛡️ Rate Limit Handling
- Monitors API usage and limits
- Switches providers when limits are reached
- Prevents service disruption

#### 🏥 Health Monitoring
- Continuous API health checks
- Proactive provider switching
- Real-time status monitoring

## Setup Requirements

### Environment Variables
```bash
# Primary Provider (Groq)
GROQAI_API_KEY=your_groq_api_key

# Secondary Provider (Google Gemini)
GOOGLE_API_KEY=your_google_api_key

# Optional: Local Ollama (for offline fallback)
# No API key needed, just install Ollama locally
```

### Dependencies
```bash
pip install langchain-groq langchain-google-genai langchain-ollama
```

## Usage

### Automatic Mode (Recommended)
```python
from src.core.llm_provider import get_llm

# Automatically handles fallbacks
llm = get_llm()
response = llm.invoke("Your query here")
```

### Manual Provider Selection
```python
# Force specific provider
llm = get_llm(provider="gemini")
llm = get_llm(provider="local")
```

### Health Monitoring
```bash
# Check all providers
python api_monitor.py

# Check specific provider
python api_monitor.py check groq

# Force switch provider
python api_monitor.py switch gemini
```

## Error Scenarios & Solutions

### Scenario 1: Groq API Limit Reached
**What happens:** System automatically switches to Gemini
**User experience:** Seamless continuation
**Logs:** `WARNING: Provider groq failed, switching to gemini`

### Scenario 2: All Cloud APIs Down
**What happens:** Falls back to local Ollama
**User experience:** Slightly slower responses, works offline
**Requirements:** Ollama installed locally

### Scenario 3: Complete API Failure
**What happens:** Emergency fallback with helpful message
**User experience:** Polite error message with alternatives
**Message:** "Services temporarily unavailable, please try again later"

## Production Deployment

### Monitoring
- Run `api_monitor.py` regularly to check health
- Monitor logs for fallback events
- Set up alerts for emergency fallback usage

### Scaling
- Multiple API keys for each provider (if supported)
- Load balancing across providers
- Geographic distribution for better reliability

### Cost Management
- Monitor usage across providers
- Set budget limits per provider
- Automatic switching helps distribute costs

## Testing

### Integration Tests
```bash
python integration_tests.py  # Tests fallback system
```

### Manual Testing
```bash
# Test provider switching
python api_monitor.py switch gemini

# Test fallback recovery
# Temporarily disable primary API key
# Run system - should automatically fallback
```

## Troubleshooting

### Common Issues

1. **"API key not configured"**
   - Check environment variables
   - Ensure `.env` file is loaded
   - Verify key validity

2. **"Provider X failed"**
   - Check internet connection
   - Verify API service status
   - Check rate limits

3. **Emergency fallback triggered**
   - All providers are down
   - Check network connectivity
   - Review API key validity

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# This will show detailed fallback logs
llm = get_llm()
```

## Best Practices

1. **Always use `get_llm()`** instead of direct provider imports
2. **Monitor API usage** to avoid unexpected costs
3. **Test fallback scenarios** regularly
4. **Keep multiple providers active** for redundancy
5. **Have local fallback ready** for offline operation

## Current Status
- ✅ Groq primary provider active
- ✅ Gemini secondary provider configured
- ✅ Local Ollama tertiary fallback available
- ✅ Emergency fallback implemented
- ✅ Health monitoring operational
- ✅ Automatic switching tested

The system is now production-ready with comprehensive fallback protection! 🚀</content>
<parameter name="filePath">c:\Users\Ishvari\Downloads\ET_Gen_AI_Member4_Complete\ET_Gen_AI\LLM_FALLBACK_GUIDE.md