# 1Password Integration Setup Guide

This guide shows you how to securely store and retrieve API keys from 1Password instead of using environment variables or storing them in code.

## Prerequisites

- 1Password account
- 1Password CLI installed (you already have it!)
- API keys for Anthropic and NewsAPI

## Step 1: Sign in to 1Password CLI

If you haven't already, sign in to 1Password:

```bash
eval $(op signin)
```

You'll be prompted for your 1Password credentials. Once signed in, the session will remain active.

## Step 2: Store Your API Keys in 1Password

### Option A: Using the 1Password App (Recommended)

1. Open 1Password app
2. Create a new item (+ button) → Select "API Credential" or "Password"
3. Fill in the details:

**For Anthropic (Claude) API Key:**
- Title: `Anthropic API Key`
- Field name: `credential` or `api key`
- Value: Your Anthropic API key (starts with `sk-ant-api...`)
- Vault: Choose your vault (or use default)

**For NewsAPI Key:**
- Title: `NewsAPI`
- Field name: `credential` or `api key`
- Value: Your NewsAPI key
- Vault: Choose your vault (or use default)

### Option B: Using the CLI

**Create Anthropic API Key:**
```bash
op item create \
  --category="API Credential" \
  --title="Anthropic API Key" \
  credential="your-anthropic-api-key-here"
```

**Create NewsAPI Key:**
```bash
op item create \
  --category="API Credential" \
  --title="NewsAPI" \
  credential="your-newsapi-key-here"
```

## Step 3: Verify Your Setup

Test that the secrets manager can retrieve your keys:

```bash
cd servicenow-monitor
python src/secrets.py
```

You should see:
```
Testing Secrets Manager...
============================================================
INFO:__main__:1Password CLI available. Signed in as: your.email@example.com
INFO:__main__:Claude API Key: Retrieved from 1Password item 'Anthropic API Key'
✓ Anthropic API Key: sk-ant-api...
INFO:__main__:NewsAPI Key: Retrieved from 1Password item 'NewsAPI'
✓ NewsAPI Key: abc123def...
============================================================
```

## Step 4: Customize Item Names (If Needed)

If you named your 1Password items differently, update the secrets manager:

**Edit `src/secrets.py`** (or pass custom item names when calling):

```python
# In the get_api_keys() function, change:
'anthropic': manager.get_secret(
    secret_name="Claude API Key",
    env_var_name="ANTHROPIC_API_KEY",
    item_name="Your Custom Item Name Here"  # Change this
),
```

**Or when using directly:**

```python
from secrets import SecretsManager

manager = SecretsManager()
api_key = manager.get_secret(
    secret_name="Claude API Key",
    env_var_name="ANTHROPIC_API_KEY",
    item_name="My Custom Item Name",  # Your item name
    vault="Development",               # Optional: specific vault
    field="api_key"                    # Optional: specific field
)
```

## Step 5: Run Your Monitor

Now you can run the monitor without setting environment variables:

```bash
python src/main.py --period week
```

The secrets manager will:
1. Try to get keys from 1Password (if signed in)
2. Fall back to environment variables
3. Fall back to config file

## How It Works

The `SecretsManager` class:

1. **Checks 1Password availability**: Detects if CLI is installed and you're signed in
2. **Retrieves secrets**: Uses `op item get` to fetch credentials
3. **Falls back gracefully**: If 1Password isn't available, uses environment variables
4. **Logs clearly**: Shows exactly where each key came from

## Security Benefits

✅ **No secrets in code**: API keys never stored in source files
✅ **No environment variables**: Don't need to export keys in shell
✅ **Encrypted storage**: 1Password vault keeps keys secure
✅ **Access control**: 1Password manages who can access secrets
✅ **Audit trail**: 1Password logs when secrets are accessed
✅ **Easy rotation**: Update keys in 1Password, code automatically uses new ones

## Troubleshooting

### "Not signed in to 1Password"

Run:
```bash
eval $(op signin)
```

### "1Password item not found"

List your items to see the exact names:
```bash
op item list
```

Find your API key items and note the exact titles, then update the `item_name` parameter.

### "Field not found"

View the item details:
```bash
op item get "Anthropic API Key" --format json
```

Look at the `fields` array to see available field names, then specify with the `field` parameter.

### Using a Specific Vault

If your keys are in a specific vault:
```bash
op item list --vault "Development"
```

Then specify the vault when getting secrets:
```python
manager.get_secret(
    secret_name="Claude API Key",
    env_var_name="ANTHROPIC_API_KEY",
    item_name="Anthropic API Key",
    vault="Development"  # Specify vault name
)
```

## Fallback Options

The secrets manager tries sources in this order:

1. **1Password** (if CLI available and signed in)
2. **Environment variables** (if set)
3. **Config file** (as last resort)

This means you can still use environment variables if 1Password isn't available:

```bash
export ANTHROPIC_API_KEY='sk-ant-api...'
export NEWS_API_KEY='your-key...'
python src/main.py --period week
```

## Disable 1Password Integration

If you want to disable 1Password and only use environment variables:

```bash
python src/main.py --period week  # Still tries 1Password by default
```

Or modify the code to disable it:

```python
monitor = ServiceNowMonitor(use_1password=False)
```

## Best Practices

1. **Keep 1Password signed in**: Session stays active for several hours
2. **Use meaningful item names**: Makes it easy to find keys later
3. **Use vaults**: Organize keys by project or environment
4. **Rotate keys regularly**: Update in 1Password, code automatically uses new ones
5. **Don't commit secrets**: `.gitignore` already excludes config files with keys

## Example: Complete Workflow

```bash
# 1. Sign in to 1Password (once per session)
eval $(op signin)

# 2. Verify secrets are accessible
python src/secrets.py

# 3. Run your monitor (no env vars needed!)
python src/main.py --period week

# 4. Or start the web dashboard
python src/web_app.py
```

Your API keys are now securely managed by 1Password! 🔐
