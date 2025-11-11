# ServiceNow Monitor - 5 Minute Quick Start

Get up and running in 5 minutes with secure 1Password integration.

## Prerequisites

- Python 3.7+
- 1Password account and app
- 1Password CLI installed (`op` command)
- Anthropic Claude API key
- NewsAPI key (optional, but recommended)

## Step 1: Clone and Install (1 minute)

```bash
git clone https://github.com/billfasoli/servicenow-monitor.git
cd servicenow-monitor
pip install -r requirements.txt
```

## Step 2: Sign In to 1Password (30 seconds)

```bash
eval $(op signin)
```

Enter your 1Password credentials when prompted.

## Step 3: Store API Keys in 1Password (2 minutes)

### Open 1Password App

1. Click the **+** button (Add Item)
2. Select **API Credential** or **Password**

### Add Anthropic API Key

- **Title**: `Anthropic API Key`
- **Field name**: `credential` or `api key`
- **Value**: Your Claude API key (get from https://console.anthropic.com/)
- Click **Save**

### Add NewsAPI Key (Optional)

- **Title**: `NewsAPI`
- **Field name**: `credential` or `api key`
- **Value**: Your NewsAPI key (get free key at https://newsapi.org/register)
- Click **Save**

## Step 4: Test Your Setup (30 seconds)

```bash
python src/secrets.py
```

You should see:
```
✓ Anthropic API Key: sk-ant-api...
✓ NewsAPI Key: abc123...
```

## Step 5: Run Your First Report! (1 minute)

### What happened this week?

```bash
python src/main.py --period week
```

You'll see:
- 📄 **SEC Filings** - Recent 10-K, 10-Q, 8-K reports
- 📰 **Press Releases** - Company announcements
- 📰 **News Articles** - Industry coverage
- 🤖 **AI Summaries** - Key insights from Claude

### Or use the web dashboard:

```bash
python src/web_app.py
```

Open browser to `http://localhost:5000` and click **Refresh**.

## What You Can Ask

Try these queries:

```bash
# What happened this week?
python src/main.py --period week

# What happened this month?
python src/main.py --period month

# What happened this quarter?
python src/main.py --period quarter

# Custom: last 14 days
python src/main.py --days 14

# Save to file
python src/main.py --period week > report.txt
```

## Next Steps

**Explore More:**
- Read [USAGE.md](USAGE.md) for complete usage guide
- See [1PASSWORD_SETUP.md](1PASSWORD_SETUP.md) for advanced security setup
- Check [README.md](README.md) for project overview

**Customize:**
- Copy `config/config.yaml.example` to `config/config.yaml`
- Edit keywords for news monitoring
- Adjust summarization counts
- Configure output preferences

**Automate:**
- Add to cron for daily reports
- Set up email digests (coming soon)
- Schedule automated monitoring

## Troubleshooting

**"Not signed in to 1Password"**
```bash
eval $(op signin)
```

**"Item not found"**
- Check item names in 1Password app match exactly
- List items: `op item list`

**"No summaries"**
- Verify you have Claude API credits
- Check API key is correct

**Need Help?**
```bash
python src/main.py --help
```

## You're All Set! 🎉

Your ServiceNow Monitor is now running with secure API key management. The monitor will automatically retrieve your keys from 1Password whenever you run it.

**Daily Workflow:**
```bash
# Morning routine (if needed)
eval $(op signin)

# Get today's updates
python src/main.py --period week

# Or browse in web dashboard
python src/web_app.py
```

No more managing environment variables or worrying about exposed secrets!
