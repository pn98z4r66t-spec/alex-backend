# OpenAI ChatGPT Integration Guide

## Overview

The Alex AI Workspace backend now supports **OpenAI ChatGPT API** as an AI provider, offering more powerful and reliable AI capabilities compared to local providers (Ollama, LM Studio).

---

## Features

✅ **Multiple AI Providers** - Choose between Ollama, LM Studio, or OpenAI  
✅ **Seamless Integration** - Same API interface for all providers  
✅ **ChatGPT Models** - Access to GPT-4, GPT-3.5-turbo, and other OpenAI models  
✅ **Token Usage Tracking** - Monitor API usage and costs  
✅ **Response Caching** - Reduce API calls and costs  
✅ **Error Handling** - Robust error handling for API failures  

---

## Configuration

### 1. Get OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to **API Keys** section
4. Click **Create new secret key**
5. Copy the API key (starts with `sk-...`)

### 2. Configure Environment Variables

Edit your `.env` file:

```env
# AI Provider Selection
AI_PROVIDER=openai

# OpenAI Configuration
OPENAI_API_KEY=sk-your-actual-api-key-here
AI_MODEL=gpt-3.5-turbo
AI_TIMEOUT=30
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=2048
```

### 3. Available Models

Choose from these OpenAI models:

| Model | Description | Best For | Cost |
|-------|-------------|----------|------|
| `gpt-4` | Most capable model | Complex tasks, reasoning | Higher |
| `gpt-4-turbo` | Faster GPT-4 | Balance of speed and quality | Medium |
| `gpt-3.5-turbo` | Fast and efficient | General tasks, chat | Lower |
| `gpt-4.1-mini` | Compact model | Quick responses | Lowest |

**Recommendation:** Start with `gpt-3.5-turbo` for cost-effectiveness, upgrade to `gpt-4` for complex tasks.

---

## Usage

### Basic Chat

```python
from src.services.ai_service import get_ai_service

ai_service = get_ai_service()
response = ai_service.chat("Hello, how can you help me?")
print(response['response'])
print(f"Tokens used: {response['usage']['total_tokens']}")
```

### Task Summarization

```python
summary = ai_service.summarize(
    "Long task description here..."
)
print(summary['response'])
```

### Document Analysis

```python
analysis = ai_service.generate_response(
    "Analyze this document and extract key points: ..."
)
print(analysis)
```

### With Custom Parameters

```python
response = ai_service.chat(
    "Write a creative story",
    model="gpt-4",
    temperature=0.9,  # More creative
    max_tokens=1000
)
```

---

## API Endpoints

All existing API endpoints work the same way with OpenAI:

### Chat with AI

```http
POST /api/ai-chat/send
Content-Type: application/json
Cookies: access_token=<token>

{
  "message": "Hello, AI!",
  "conversation_history": []
}
```

### Analyze Document

```http
POST /api/documents/analyze/<file_id>
Content-Type: application/json
Cookies: access_token=<token>

{
  "analysis_type": "summary"
}
```

### Task AI Assistance

```http
POST /api/tasks/<task_id>/ai-assist
Content-Type: application/json
Cookies: access_token=<token>

{
  "action": "suggest_next_steps"
}
```

---

## Cost Management

### Token Usage

OpenAI charges based on tokens used:
- **Input tokens:** Prompt text
- **Output tokens:** Generated response
- **Total tokens:** Input + Output

### Pricing (as of Oct 2025)

| Model | Input (per 1K tokens) | Output (per 1K tokens) |
|-------|----------------------|------------------------|
| gpt-3.5-turbo | $0.0005 | $0.0015 |
| gpt-4 | $0.03 | $0.06 |
| gpt-4-turbo | $0.01 | $0.03 |

### Cost Optimization Tips

1. **Enable Caching** - Reduce duplicate API calls
   ```python
   ai_service = AIService(enable_cache=True)
   ```

2. **Limit Max Tokens** - Control response length
   ```env
   AI_MAX_TOKENS=1024  # Shorter responses
   ```

3. **Use Appropriate Model** - Don't use GPT-4 for simple tasks
   ```env
   AI_MODEL=gpt-3.5-turbo  # Cost-effective for most tasks
   ```

4. **Monitor Usage** - Check token usage in responses
   ```python
   print(f"Tokens: {response['usage']['total_tokens']}")
   ```

---

## Switching Between Providers

### Use OpenAI (Cloud)

```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
AI_MODEL=gpt-3.5-turbo
```

### Use Ollama (Local)

```env
AI_PROVIDER=ollama
AI_API_URL=http://localhost:11434/api/generate
AI_MODEL=phi3
```

### Use LM Studio (Local)

```env
AI_PROVIDER=lmstudio
AI_API_URL=http://localhost:1234/v1
AI_MODEL=local-model
```

**No code changes required!** Just update environment variables and restart the server.

---

## Testing

### Run Integration Test

```bash
cd /home/ubuntu
export OPENAI_API_KEY='your-api-key-here'
python3 test_openai_integration.py
```

### Expected Output

```
============================================================
OpenAI Integration Test
============================================================
AI Provider: openai
AI Model: gpt-3.5-turbo
API Key Set: Yes
============================================================

1. Initializing AI Service with OpenAI provider...
✅ AI Service initialized successfully

2. Testing simple chat...
✅ Chat response received
   Tokens: 25

3. Testing task summarization...
✅ Summarization successful

4. Testing document analysis...
✅ Analysis successful

============================================================
✅ ALL TESTS PASSED!
============================================================
```

---

## Troubleshooting

### Error: "OpenAI API key is required"

**Solution:** Set the `OPENAI_API_KEY` environment variable:
```bash
export OPENAI_API_KEY='sk-your-key-here'
```

### Error: "Incorrect API key provided"

**Solution:** 
1. Verify your API key is correct
2. Check if the key has been revoked
3. Generate a new key from OpenAI dashboard

### Error: "Rate limit exceeded"

**Solution:**
1. Wait a few minutes and try again
2. Upgrade your OpenAI plan
3. Enable caching to reduce API calls

### Error: "Model not found"

**Solution:** Use a valid model name:
- `gpt-3.5-turbo`
- `gpt-4`
- `gpt-4-turbo`

### Slow Responses

**Solution:**
1. Reduce `AI_MAX_TOKENS` for shorter responses
2. Use `gpt-3.5-turbo` instead of `gpt-4`
3. Check your internet connection

---

## Security Best Practices

### 1. Protect API Key

❌ **Don't:**
- Commit API key to Git
- Share API key publicly
- Hardcode API key in code

✅ **Do:**
- Store in `.env` file (add to `.gitignore`)
- Use environment variables
- Rotate keys regularly

### 2. Rate Limiting

Enable rate limiting to prevent abuse:
```python
RATELIMIT_DEFAULT = "200 per day;50 per hour"
```

### 3. Input Validation

Always validate user input before sending to AI:
```python
if len(prompt) > 10000:
    raise APIError('Prompt too long', 400)
```

### 4. Error Handling

Never expose API errors to users:
```python
try:
    response = ai_service.chat(prompt)
except Exception as e:
    logger.error(f'AI error: {str(e)}')
    return {'error': 'AI service unavailable'}
```

---

## Comparison: OpenAI vs Local Providers

| Feature | OpenAI | Ollama | LM Studio |
|---------|--------|--------|-----------|
| **Setup** | API key only | Install + download models | Install + download models |
| **Cost** | Pay per token | Free | Free |
| **Performance** | Excellent | Good | Good |
| **Reliability** | Very high | Depends on hardware | Depends on hardware |
| **Privacy** | Cloud-based | Fully local | Fully local |
| **Model Quality** | State-of-the-art | Good | Good |
| **Internet Required** | Yes | No | No |
| **Hardware Requirements** | None | GPU recommended | GPU recommended |

### When to Use OpenAI

✅ Production applications  
✅ Need highest quality responses  
✅ Don't want to manage infrastructure  
✅ Want guaranteed uptime  
✅ Need latest models  

### When to Use Local Providers

✅ Privacy-sensitive data  
✅ No internet connection  
✅ Want to avoid API costs  
✅ Have powerful hardware  
✅ Development/testing  

---

## Advanced Features

### Custom System Prompts

```python
response = ai_service.provider.chat_with_history([
    {"role": "system", "content": "You are a helpful task management assistant."},
    {"role": "user", "content": "Help me prioritize my tasks"}
])
```

### Streaming Responses

(Coming soon - for real-time chat interfaces)

### Function Calling

(Coming soon - for structured data extraction)

---

## Monitoring & Logging

### Enable Detailed Logging

```python
import logging
logging.basicConfig(level=logging.INFO)
```

### Track Token Usage

```python
response = ai_service.chat("Hello")
tokens = response['usage']['total_tokens']
cost = tokens * 0.000002  # Approximate cost for gpt-3.5-turbo
print(f"Cost: ${cost:.6f}")
```

### Cache Statistics

```python
stats = ai_service.get_cache_stats()
print(f"Cache size: {stats['size']}")
```

---

## Migration Guide

### From Ollama to OpenAI

1. Get OpenAI API key
2. Update `.env`:
   ```env
   AI_PROVIDER=openai
   OPENAI_API_KEY=sk-your-key-here
   AI_MODEL=gpt-3.5-turbo
   ```
3. Restart server
4. Test with existing endpoints

**No code changes needed!**

---

## FAQ

**Q: How much will it cost?**  
A: Depends on usage. For typical task management (100 requests/day), expect $1-5/month with gpt-3.5-turbo.

**Q: Can I use both OpenAI and Ollama?**  
A: Not simultaneously, but you can switch by changing `AI_PROVIDER` in `.env`.

**Q: Is my data sent to OpenAI?**  
A: Yes, prompts and responses go through OpenAI's API. See their [privacy policy](https://openai.com/policies/privacy-policy).

**Q: Can I use GPT-4?**  
A: Yes, set `AI_MODEL=gpt-4` in `.env`. Note: GPT-4 is more expensive.

**Q: What if OpenAI is down?**  
A: Implement fallback to local provider or show error message to users.

---

## Support

- **OpenAI Documentation:** https://platform.openai.com/docs
- **OpenAI Status:** https://status.openai.com
- **GitHub Issues:** Report bugs or request features

---

**Version:** 3.0.0  
**Last Updated:** October 2025  
**Status:** ✅ Production Ready

**Made with ❤️ using OpenAI ChatGPT API**

