# Algorithmic Trading System Using Machine Learning Predicted Sharpe Ratios

## Overview

This project implements a daily trading system for S&P 500 stocks based on predicted Sharpe ratios. Using machine learning models from scikit-learn, the system forecasts each stock’s future return and volatility. It ranks stocks by their predicted Sharpe ratio and rebalances the portfolio by selling holdings that fall out of the top 10 and buying new stocks that enter the top ranks, while retaining existing holdings that remain in the top selections. Trades are executed through the free paper trading API provided by Alpaca Markets.

## The Three Development Stages:
### 1. Data Fetching using Yahoo Finance
My first step when creating the trading bot was to brainstorm a performance metric to rank the stocks. I originally thought of just predicting returns and using that as my only trading metric, but I knew that would lead to risky investments with a limited portfolio. So to balance the result, I predicted the volatility too and combined both to form the Sharpe score.

#### To clarify, in this bot I am ranking stocks using the simplified Sharpe ratio, omiting the risk-free rate portion of the equation from my calculations to obatain the risk-adjusted return.

Now I was able to start applying the RandomForestRegressor (imported from Scikit-learn) to my downloaded Yahoo Finance data. I decided to formulate my Sharpe esimate for the next trading day, as opposed to a week ahead as that allows me to make the most accurate predictions using recent data. I trained the ML model on the entire history of past data that I had for stock returns and also volitility. I had to create my own volitility estimate. For each stock I used the standard deviation of the last 5 days of its returns. 

When developing the dataframe with the top 10 highest ranked stocks, I decided to look purely at the stocks in the S&P 500 for simplicity. 

### 2. Trading Using Alpaca Markets

Deciding on Alpaca for my trading simulation wasn't a hard choice as it had all the tools I needed to place trades and was easily accessible to new users without a fee. I did not require a live trader for the sake of the project but one can be implemented. Alpaca has their own live trader if a user wants to apply the trading bot for their own use.

I implemented the use of a .env file so that each user could, privately, use their own account with an api_key and secret_key from Alpaca Markets.

### 3. Main Trading Runner

After trial and error, I decided to use a separate file to join step 1 (the Yahoo Finance logic) and step 2 (the Alpaca logic) since their dependencies differ. So, I created a separate python enviorment for each using Anaconda and automated the running process. The main_runner.py file runs the yfinance_ML.py file to generate data of which stocks to buy and then runs the alpaca_trader.py to actually process said trades. 

A lot of the work in the main_trader.py file was searching for file and venv locations and coordinating them together. Additionally, making the program compatible for all operating systems added a few more lines of code.

---

## Concluding Results

This project aimed to explore applying machine learning to trading strategies rather than generating profitable investments. As expected, the strategy performed poorly, with an estimated daily loss of about $1,000 on a $180,000 portfolio. Key areas for improvement include:

1. **Feature and Model Complexity**  
   Using only basic price and volume data with simple Random Forest models limited predictive power. Incorporating technical indicators and experimenting with more advanced models like gradient boosting or neural networks would improve results.

2. **Realistic Backtesting**  
   The current setup lacks transaction costs, slippage, and portfolio management. Implementing a proper backtesting engine with cash tracking and realistic trades would provide more meaningful insights.

3. **Reducing Overtrading**  
   Daily rebalancing causes excessive turnover and noise. Longer holding periods or adaptive signals would create a more stable strategy.

Overall, this project was a valuable learning experience that highlighted challenges in combining machine learning with finance.

---

## How to Use the Trading Bot

Follow these steps to run the automated trading bot:

### Requirements

- Python 3.10 recommended for both environments
- Go to the requirements folder

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

### 2. Set Up Virtual Environments

Create two separate environments: one for data analysis, one for trading.

```bash
# Data analysis (yfinance)
python -m venv yfinance_env

# Trading (Alpaca)
python -m venv alpaca_env
```

### 3. Install Dependencies

Activate each environment and install required packages.

**In `yfinance_env`:**

```bash
# Activate (Windows)
yfinance_env\Scripts\activate

# Activate (macOS/Linux)
source yfinance_env/bin/activate

pip install -r .\requirements\yfinance_req.txt
```

**In `alpaca_env`:**

```bash
# Activate (Windows)
alpaca_env\Scripts\activate

# Activate (macOS/Linux)
source alpaca_env/bin/activate

pip install -r .\requirements\alpaca_req.txt
```

### 4. Configure API Keys

Create a `.env` file in the project root directory and add your Alpaca paper trading credentials:

```env
ALPACA_API_KEY=your_api_key_here
ALPACA_SECRET_KEY=your_secret_key_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets
```

> Each user must use their own Alpaca API keys to run the bot.

### 5. Run the Bot

From the project root, run:

```bash
python main_runner.py
```

---

**File Structure:**

```
ML-SHARPE-TRADER/
├── alpaca_env/
├── requirements/
│   ├── alpaca_req.txt
│   └── yfinance_req.txt
├── shared_data/
├── trader/
│   ├── __init__.py
│   ├── alpaca_trader.py
│   └── yfinance_ML.py
├── yfinance_env/
├── main_runner.py
└── README.md

```