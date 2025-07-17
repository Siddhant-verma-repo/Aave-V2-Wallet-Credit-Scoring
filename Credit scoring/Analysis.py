import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set the correct path to your file
base_dir = os.path.dirname(__file__)  # Gets the directory where the script is located
input_file = os.path.join(base_dir, "wallet_credit_scores.json")
output_img = os.path.join(base_dir, "score_distribution.png")

# Load the wallet scores
with open(input_file, "r") as f:
    data = json.load(f)

# Convert to DataFrame
df_scores = pd.DataFrame(data)

# Create score ranges
bins = list(range(0, 1100, 100))
labels = [f"{i}-{i+99}" for i in bins[:-1]]
df_scores["score_range"] = pd.cut(df_scores["score"], bins=bins, labels=labels, include_lowest=True)

# Count how many wallets fall into each range
score_dist = df_scores["score_range"].value_counts().sort_index()

# Plot the distribution
plt.figure(figsize=(12, 6))
sns.barplot(x=score_dist.index, y=score_dist.values, palette="viridis")
plt.title("Wallet Credit Score Distribution (0–1000)")
plt.xlabel("Score Range")
plt.ylabel("Number of Wallets")
plt.xticks(rotation=45)
plt.tight_layout()
plt.grid(axis='y')
plt.savefig(output_img)

# Basic behavioral analysis
low_range_wallets = df_scores[df_scores["score"] <= 300]
high_range_wallets = df_scores[df_scores["score"] >= 900]

low_stats = {
    "total_wallets": len(low_range_wallets),
    "min_score": low_range_wallets["score"].min(),
    "max_score": low_range_wallets["score"].max(),
    "avg_score": low_range_wallets["score"].mean()
}

high_stats = {
    "total_wallets": len(high_range_wallets),
    "min_score": high_range_wallets["score"].min(),
    "max_score": high_range_wallets["score"].max(),
    "avg_score": high_range_wallets["score"].mean()
}

# Print summary results
print("🔻 Low Scoring Wallets (0–300):", low_stats)
print("🔺 High Scoring Wallets (900–1000):", high_stats)
print("\n📊 Wallets per Score Range:")
for label, count in score_dist.items():
    print(f"{label}: {count}")

print(f"\n✅ Score distribution chart saved to: {output_img}")
