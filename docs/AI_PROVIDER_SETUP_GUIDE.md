# AI Provider Setup Guide

**Alex AI Workspace** supports multiple AI providers for maximum flexibility. Choose the provider that best fits your needs.

---

## Supported AI Providers

### 1. LM Studio (Recommended for Beginners) ⭐

**Best for:** Ease of use, visual interface, quick setup

**Pros:**
- ✅ Beautiful, user-friendly GUI
- ✅ Drag-and-drop model management
- ✅ OpenAI-compatible API
- ✅ Excellent performance
- ✅ Easy model switching
- ✅ Built-in model browser
- ✅ Real-time monitoring

**Cons:**
- ❌ Desktop application only
- ❌ Not ideal for server deployments

---

### 2. Ollama

**Best for:** Server deployments, automation, CLI enthusiasts

**Pros:**
- ✅ Lightweight and fast
- ✅ CLI-based (great for automation)
- ✅ Docker support
- ✅ Server-friendly
- ✅ Active development

**Cons:**
- ❌ No GUI
- ❌ CLI-only model management
- ❌ Custom API (not OpenAI-compatible)

---

## Quick Start Guide

### Option 1: LM Studio Setup (Recommended)

#### Step 1: Download and Install

1. Visit [https://lmstudio.ai](https://lmstudio.ai)
2. Download for your platform (Windows, macOS, Linux)
3. Install the application

#### Step 2: Download a Model

1. Open LM Studio
2. Click on the **Search** tab (🔍)
3. Search for a model (recommended models):
   - **Phi-3 Mini** (3.8B) - Fast, good for most tasks
   - **Llama 3 8B** - Excellent quality
   - **Mistral 7B** - Great balance
4. Click **Download** next to your chosen model
5. Wait for download to complete

#### Step 3: Load the Model

1. Go to the **Chat** tab (💬)
2. Click **Select a model to load**
3. Choose your downloaded model
4. Wait for model to load (you'll see "Model loaded" message)

#### Step 4: Start the Server

1. Go to the **Local Server** tab (🌐)
2. Click **Start Server**
3. Server will start on `http://localhost:1234`
4. Keep LM Studio running while using Alex AI Workspace

#### Step 5: Configure Alex AI Workspace

Edit your `.env` file:

```bash
# AI Provider Configuration
AI_PROVIDER=lmstudio
AI_API_URL=http://localhost:1234/v1
AI_MODEL=local-model
AI_TIMEOUT=60
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=2048
```

#### Step 6: Test the Connection

```bash
# Start your backend
python run.py

# In another terminal, test the AI endpoint
curl -X POST http://localhost:5000/api/ai/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, AI!"}'
```

---

### Option 2: Ollama Setup

#### Step 1: Install Ollama

**macOS/Linux:**
```bash
curl https://ollama.ai/install.sh | sh
```

**Windows:**
Download from [https://ollama.ai/download](https://ollama.ai/download)

#### Step 2: Pull a Model

```bash
# Recommended models
ollama pull phi3          # 3.8B - Fast and efficient
ollama pull llama3:8b     # 8B - High quality
ollama pull mistral       # 7B - Balanced
```

#### Step 3: Test Ollama

```bash
# Start a chat to verify
ollama run phi3

# Type a message and press Enter
# Press Ctrl+D to exit
```

#### Step 4: Configure Alex AI Workspace

Edit your `.env` file:

```bash
# AI Provider Configuration
AI_PROVIDER=ollama
AI_API_URL=http://localhost:11434
AI_MODEL=phi3
AI_TIMEOUT=30
```

#### Step 5: Test the Connection

```bash
# Ollama runs automatically as a service
# Just start your backend
python run.py

# Test the AI endpoint
curl -X POST http://localhost:5000/api/ai/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, AI!"}'
```

---

## Provider Comparison

| Feature | LM Studio | Ollama |
|---------|-----------|--------|
| **Interface** | Beautiful GUI | CLI only |
| **Setup Difficulty** | Very Easy ⭐⭐⭐⭐⭐ | Medium ⭐⭐⭐ |
| **Model Management** | Drag & Drop | CLI commands |
| **API Type** | OpenAI-compatible | Custom |
| **Default Port** | 1234 | 11434 |
| **Performance** | Excellent | Good |
| **Server Deployment** | ❌ Desktop only | ✅ Perfect |
| **Automation** | ❌ Limited | ✅ Excellent |
| **Monitoring** | ✅ Built-in UI | ❌ CLI only |
| **Model Switching** | ✅ One click | ⚠️ CLI command |
| **Streaming** | ✅ Yes | ✅ Yes |
| **Embeddings** | ✅ Yes | ✅ Yes |

---

## Recommended Models

### For General Use

| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| **Phi-3 Mini** | 3.8B | ⚡⚡⚡⚡⚡ | ⭐⭐⭐⭐ | Fast responses, good quality |
| **Llama 3 8B** | 8B | ⚡⚡⚡⚡ | ⭐⭐⭐⭐⭐ | Best quality, slightly slower |
| **Mistral 7B** | 7B | ⚡⚡⚡⚡ | ⭐⭐⭐⭐⭐ | Balanced performance |

### For Specific Tasks

- **Code Generation:** CodeLlama, DeepSeek Coder
- **Creative Writing:** Llama 3, Mistral
- **Analysis:** Phi-3, Llama 3
- **Fast Responses:** Phi-3 Mini, TinyLlama

---

## Configuration Reference

### Environment Variables

```bash
# Required
AI_PROVIDER=lmstudio          # or 'ollama'
AI_API_URL=http://localhost:1234/v1  # LM Studio URL
# AI_API_URL=http://localhost:11434   # Ollama URL

# Optional (with defaults)
AI_MODEL=local-model          # Model name
AI_TIMEOUT=60                 # Request timeout in seconds
AI_TEMPERATURE=0.7            # Creativity (0.0-2.0)
AI_MAX_TOKENS=2048            # Max response length
```

### Temperature Guide

- **0.0-0.3:** Factual, deterministic (good for analysis)
- **0.4-0.7:** Balanced (recommended for most tasks)
- **0.8-1.0:** Creative (good for writing)
- **1.1-2.0:** Very creative (experimental)

---

## Switching Between Providers

You can easily switch between providers by changing the `.env` file:

### Switch to LM Studio

```bash
AI_PROVIDER=lmstudio
AI_API_URL=http://localhost:1234/v1
AI_MODEL=local-model
AI_TIMEOUT=60
```

### Switch to Ollama

```bash
AI_PROVIDER=ollama
AI_API_URL=http://localhost:11434
AI_MODEL=phi3
AI_TIMEOUT=30
```

**Restart the backend** after changing providers:

```bash
# Stop the server (Ctrl+C)
# Start again
python run.py
```

---

## Troubleshooting

### LM Studio Issues

**Problem:** "Cannot connect to LM Studio"

**Solutions:**
1. ✅ Ensure LM Studio is running
2. ✅ Check that a model is loaded
3. ✅ Verify the server is started (Local Server tab)
4. ✅ Check the port (default: 1234)
5. ✅ Try restarting LM Studio

**Problem:** "Model not loaded"

**Solutions:**
1. ✅ Go to Chat tab
2. ✅ Select a model from the dropdown
3. ✅ Wait for "Model loaded" message
4. ✅ Then start the server

### Ollama Issues

**Problem:** "Ollama not responding"

**Solutions:**
1. ✅ Check if Ollama is running: `ollama list`
2. ✅ Restart Ollama service
3. ✅ Verify the model is pulled: `ollama pull phi3`
4. ✅ Check port 11434 is not blocked

**Problem:** "Model not found"

**Solutions:**
1. ✅ List available models: `ollama list`
2. ✅ Pull the model: `ollama pull MODEL_NAME`
3. ✅ Update `.env` with correct model name

### General Issues

**Problem:** "AI responses are slow"

**Solutions:**
1. ✅ Use a smaller model (Phi-3 Mini)
2. ✅ Reduce `AI_MAX_TOKENS`
3. ✅ Increase `AI_TIMEOUT`
4. ✅ Check system resources (RAM, CPU)

**Problem:** "AI responses are poor quality"

**Solutions:**
1. ✅ Try a larger model (Llama 3 8B)
2. ✅ Adjust `AI_TEMPERATURE` (try 0.7)
3. ✅ Increase `AI_MAX_TOKENS`
4. ✅ Use a task-specific model

---

## Performance Tips

### For Best Performance

1. **Use appropriate model size:**
   - 8GB RAM: Phi-3 Mini (3.8B)
   - 16GB RAM: Mistral 7B or Llama 3 8B
   - 32GB+ RAM: Llama 3 70B (if available)

2. **Optimize settings:**
   - Lower temperature for faster, focused responses
   - Reduce max_tokens for quicker responses
   - Use caching (enabled by default)

3. **System optimization:**
   - Close unnecessary applications
   - Ensure adequate RAM
   - Use SSD for model storage

---

## API Endpoints

### Check AI Status

```bash
GET /api/ai/status
```

**Response:**
```json
{
  "available": true,
  "provider": "lmstudio",
  "model": "local-model",
  "features": ["chat", "streaming", "embeddings"]
}
```

### Chat with AI

```bash
POST /api/ai/chat
Content-Type: application/json
Authorization: Bearer YOUR_TOKEN

{
  "message": "Hello, AI!",
  "temperature": 0.7,
  "max_tokens": 500
}
```

### List Available Agents

```bash
GET /api/ai/agents
```

---

## Advanced Configuration

### Using Multiple Models

You can switch models per request:

```bash
POST /api/ai/chat
{
  "message": "Write a poem",
  "model": "llama3:8b",
  "temperature": 1.0
}
```

### Streaming Responses

For real-time streaming (coming soon):

```bash
POST /api/ai/chat/stream
{
  "message": "Tell me a story",
  "stream": true
}
```

---

## Security Considerations

1. **Local AI is private:** Your data never leaves your machine
2. **No API keys needed:** No external services required
3. **Firewall:** Keep AI ports (1234, 11434) localhost-only
4. **Authentication:** Always use JWT tokens for API access

---

## Resources

### LM Studio
- Website: https://lmstudio.ai
- Documentation: https://lmstudio.ai/docs
- Models: Built-in model browser

### Ollama
- Website: https://ollama.ai
- Documentation: https://github.com/ollama/ollama
- Models: https://ollama.ai/library

### Model Sources
- Hugging Face: https://huggingface.co/models
- GGUF Models: https://huggingface.co/models?library=gguf

---

## Conclusion

Both LM Studio and Ollama are excellent choices for running local AI:

- **Choose LM Studio** if you want ease of use and a beautiful interface
- **Choose Ollama** if you need server deployment or CLI automation

The Alex AI Workspace supports both seamlessly - you can even switch between them anytime!

---

**Need Help?**

- Check the troubleshooting section above
- Review the API documentation
- Test with simple prompts first
- Ensure your model is loaded and server is running

**Happy AI-powered productivity! 🚀**

