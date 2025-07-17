import json
import pandas as pd
import numpy as np
from tqdm import tqdm

INPUT_FILE = 'user-wallet-transactions.json'  # Rename your JSON file to this
OUTPUT_FILE = 'wallet_credit_scores.json'

# Load JSON
with open(INPUT_FILE, 'r') as f:
    data = json.load(f)

# Flatten into DataFrame
records = []
for tx in data:
    wallet = tx.get("userWallet", "")
    action = tx.get("action", "").lower()
    timestamp = tx.get("timestamp")
    
    try:
        amount = int(tx.get("actionData", {}).get("amount", 0))
        price_usd = float(tx.get("actionData", {}).get("assetPriceUSD", 0))
    except:
        amount = 0
        price_usd = 0.0
    
    usd_value = (amount / 1e6) * price_usd if price_usd > 0 else 0

    records.append({
        "wallet": wallet,
        "action": action,
        "timestamp": pd.to_datetime(timestamp, unit='s', errors='coerce'),
        "usd_value": usd_value
    })

df = pd.DataFrame(records)

# Feature Engineering
wallet_scores = {}
wallet_groups = df.groupby('wallet')

for wallet, group in tqdm(wallet_groups):
    actions = group['action'].value_counts().to_dict()
    total_actions = len(group)

    deposit_amt = group[group['action'] == 'deposit']['usd_value'].sum()
    borrow_amt = group[group['action'] == 'borrow']['usd_value'].sum()
    repay_amt = group[group['action'] == 'repay']['usd_value'].sum()
    redeem_amt = group[group['action'] == 'redeemunderlying']['usd_value'].sum()
    liquidations = group[group['action'] == 'liquidationcall'].shape[0]

    active_days = group['timestamp'].dt.date.nunique()
    avg_tx_interval = group['timestamp'].sort_values().diff().dt.total_seconds().mean()
    avg_tx_interval = avg_tx_interval if not np.isnan(avg_tx_interval) else 0

    # Ratios
    borrow_to_deposit = borrow_amt / deposit_amt if deposit_amt > 0 else 0
    repay_ratio = repay_amt / borrow_amt if borrow_amt > 0 else 1
    liquidation_rate = liquidations / total_actions if total_actions > 0 else 0

    # Score Logic
    score = 1000
    score -= 300 if liquidation_rate > 0.2 else 0
    score -= 200 if borrow_to_deposit > 1.2 else 0
    score += 100 if repay_ratio > 0.9 else 0
    score += 50 if actions.get('deposit', 0) > actions.get('borrow', 0) else -50
    score -= 50 if avg_tx_interval < 10 else 0  # Bot-like frequency

    score = max(0, min(1000, int(score)))

    wallet_scores[wallet] = score

# Save results
output = [{"wallet": k, "score": v} for k, v in wallet_scores.items()]
with open(OUTPUT_FILE, 'w') as f:
    json.dump(output, f, indent=2)

print(f"✅ Scoring complete. Output saved to: {OUTPUT_FILE}")
