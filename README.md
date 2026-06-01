# ⚽ SP 2026 — Stavni Analizator

AI-powered stavni analizator za Svetovno Prvenstvo 2026.

## Kaj zmore
- 🔍 Analiza tekem z web searchom (poškodbe, forma, postave, trenerji)
- 💡 Iskanje value betov (napačno postavljene kvote)
- 📊 Kelly kriterij za upravljanje bankrolla
- 📬 Telegram obvestila 1 dan pred tekmami

## Namestitev

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Konfiguracija

V stranski plošči vnesi:
1. **Anthropic API ključ** — dobi na https://console.anthropic.com
2. **Bankroll** — začetni znesek (npr. 20 €)
3. **Telegram token** — od @BotFather
4. **Telegram Chat ID** — tvoj osebni ID

## Hosting (brezplačno)

### Streamlit Cloud
1. Push kodo na GitHub
2. Pojdi na https://share.streamlit.io
3. Poveži repozitorij — aplikacija je online!
4. Dodaj API ključe v Settings → Secrets

### Secrets format za Streamlit Cloud
```toml
ANTHROPIC_API_KEY = "sk-ant-..."
TELEGRAM_TOKEN = "1234:ABC..."
TELEGRAM_CHAT_ID = "123456789"
```
