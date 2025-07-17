# 🧠 Aave V2 Wallet Credit Scoring

This project analyzes raw transaction-level data from the Aave V2 DeFi lending protocol and assigns each wallet address a **credit score between 0 and 1000**. The goal is to assess user behavior and risk based on historical interaction patterns.

---

## 📊 Overview

Each transaction includes actions such as:
- `deposit`
- `borrow`
- `repay`
- `redeemunderlying`
- `liquidationcall`

These are used to evaluate creditworthiness, with high scores representing responsible usage (timely repayments, low liquidation risk), and low scores representing risky or exploitative behavior.

---

## 🛠️ Methodology

### ✅ Rule-Based Scoring System

We use a deterministic scoring strategy based on the following behavioral features:

| Feature                     | Contribution to Score              |
|-----------------------------|------------------------------------|
| High liquidation rate       | −300 if > 20% of all actions       |
| High borrow-to-deposit ratio| −200 if > 1.2                      |
| Repay ratio > 90%           | +100                               |
| More deposits than borrows  | +50                                |
| Bot-like behavior (fast txs)| −50 if avg interval < 10 seconds  |

Final scores are scaled between **0 and 1000**.

---

## 🧱 Architecture & Flow

```mermaid
graph TD
A[Raw JSON File] --> B[Data Flattening]
B --> C[Feature Engineering]
C --> D[Score Calculation]
D --> E[Output: wallet_credit_scores.json]
