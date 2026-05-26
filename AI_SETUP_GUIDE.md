# AI-Powered Explanations Setup Guide

## 🤖 Gemini AI (Recommended - FREE!)

Google Gemini offers a **FREE tier** with generous limits, making it perfect for this project!

### Step 1: Get Your Gemini API Key

1. **Visit:** https://makersuite.google.com/app/apikey (or https://aistudio.google.com/apikey)
2. **Sign in** with your Google account
3. **Click "Create API Key"**
4. **Copy** your API key (starts with `AIza...`)

### Step 2: Configure Your Application

Edit `backend/.env`:

```env
# Choose AI provider
AI_PROVIDER=gemini

# Add your Gemini API key
GEMINI_API_KEY=AIzaSy...your-key-here
GEMINI_MODEL=gemini-1.5-flash
```

### Step 3: Restart Backend

```powershell
# Stop backend
Get-Process python | Stop-Process -Force

# Start backend
cd backend
py -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### ✅ That's It!

Your medical lab reports will now use AI for personalized explanations!

---

## 🔧 OpenAI (Alternative - Paid)

If you prefer OpenAI's GPT models:

### Step 1: Get OpenAI API Key

1. **Visit:** https://platform.openai.com/api-keys
2. **Create account** and add billing
3. **Create API key**

### Step 2: Configure

Edit `backend/.env`:

```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...your-key-here
OPENAI_MODEL=gpt-4
```

**Cost:** ~$0.01-0.05 per report

---

## 📊 Pricing Comparison

| Provider | Free Tier | Cost | Speed | Quality |
|----------|-----------|------|-------|---------|
| **Gemini** | ✅ 60 req/min | **FREE** | ⚡ Fast | ⭐⭐⭐⭐ |
| OpenAI GPT-4 | ❌ No free tier | $0.03-0.06/1K tokens | Medium | ⭐⭐⭐⭐⭐ |
| OpenAI GPT-3.5 | ❌ No free tier | $0.002/1K tokens | ⚡ Very Fast | ⭐⭐⭐⭐ |

**Recommendation:** Start with **Gemini** (free and excellent quality!)

---

## 🎯 What AI Adds

With AI enabled, you get:

1. **Personalized Explanations**
   - Context-aware insights based on your specific results
   - Natural language understanding of patterns

2. **Smart Summaries**
   - Overall health assessment
   - Identification of concerning trends
   - Positive changes celebrated

3. **Lifestyle Tips**
   - Recommendations tailored to your results
   - Diet and exercise suggestions
   - When to consult your doctor

4. **Historical Analysis** (Trends feature)
   - Intelligent trend interpretation
   - Pattern recognition across time
   - Progress tracking insights

---

## 🧪 Test Your Setup

Upload a medical report and check the explanation section. You should see more detailed, personalized explanations compared to the basic rule-based system.

---

## ⚠️ Important Notes

### Medical Disclaimer
- AI explanations are **educational only**
- **NOT medical advice**  
- Always consult your healthcare provider

### Privacy
- Your data is sent to the AI provider (Google/OpenAI)
- API calls are encrypted (HTTPS)
- No data is stored by AI providers (per their terms)
- Consider privacy implications for sensitive health data

### Fallback System
- If AI is unavailable, the system automatically falls back to rule-based explanations
- Your app never breaks due to AI issues

---

## 🔍 Troubleshooting

### "AI Service disabled - no API key provided"

**Solution:** Check your `.env` file has the correct API key

```env
GEMINI_API_KEY=AIzaSy...  # Not empty!
```

### "google-generativeai package not installed"

**Solution:** Install the package

```powershell
py -m pip install google-generativeai
```

### API Key Not Working

**For Gemini:**
- Verify key at https://aistudio.google.com/apikey
- Check API is enabled
- Ensure no billing issues

**For OpenAI:**
- Verify key at https://platform.openai.com/api-keys
- Check you have billing set up
- Ensure sufficient credits

### Logs Show Errors

Check backend terminal for specific error messages:

```powershell
# View running backend logs
# Terminal should show AI service initialization
```

---

## 💡 Recommended Models

### Gemini Models

| Model | Speed | Cost | Best For |
|-------|-------|------|----------|
| `gemini-1.5-flash` | ⚡⚡⚡ | FREE | **Recommended** - Fast & accurate |
| `gemini-1.5-pro` | ⚡⚡ | FREE | More detailed analysis |
| `gemini-1.0-pro` | ⚡⚡⚡ | FREE | Basic explanations |

### OpenAI Models

| Model | Speed | Cost | Best For |
|-------|-------|------|----------|
| `gpt-4` | ⚡ | $$$ | Highest quality |
| `gpt-4-turbo` | ⚡⚡ | $$ | Good balance |
| `gpt-3.5-turbo` | ⚡⚡⚡ | $ | Fast & cheap |

---

## 🚀 Next Steps

1. **Get your Gemini API key** (takes 2 minutes)
2. **Add it to `.env`**
3. **Restart backend**
4. **Upload a lab report** and enjoy AI-powered insights!

---

**Questions?** Check the backend logs or create an issue on GitHub.
