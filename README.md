# Sharpe Ratio ML-Based Trading Bot

video demo: https://youtu.be/7FM4VRJnjPw   

## Overview

This project that I made is a daily trading system that calculates and trades S&P 500 stocks by Sharpe ratios. Using machine learning tools from sklearn, the program predicts future return and volatility of each stock. Then, the program sells any current holdings and buys the top 10 highest scoring (highest Sharpe score) stocks from a trading account. For this project I used the free paper trader from Alpaca Markets API to execute trades.

## The Three Development Stages:
### 1. Data Fetching using Yahoo Finance
My first step when creating the trading bot was to brainstorm a performance metric to rank the stocks. I orginally thought of just predicting returns and using that as my only trading metric, but I knew that would lead to risky investments with a limited portfolio. So to balance the result, I predicted the volitlity too and combined both to form the Sharpe score.

#### To clarify, in this bot I am ranking stocks using the simplified Sharpe ratio, omiting the risk-free rate portion of the equation from my calculations to obatain the risk-adjusted return.

Now I was able to start applying the RandomForrestRegressor (imported from Scikit-learn) to my downloaded Yahoo Finance data. I decided to formulate my Sharpe esimate for the next trading day, as opposed to a week ahead as that will give the most accurate predictions using recent data. I trained the ML model on the entire history of past data that I had for stock returns and also volitility. I had to create my own volitility estimate. For each stock I used the standard deviation of the last 5 days of its returns. 

Developing a dataframe with the top 10 highest ranked stocksm I decided to look purely at the stocks in the S&P 500 for simplicity. 

### 2. Trading Using Alpaca Markets

Deciding on Alpaca for my trading simulation wasn't a hard choice as it had all the tools I needed a place to trade that was easily accessible to new users and without a fee. I did not require a live trader for the sake of the project but one can be implemented later. Alpaca has their own live trader if a user wants to apply the trading bot for their own use.

I implemented the use of a .env file so that each user could, privately, use their own account with an api_key and secret_key from Alpaca.

### 3. Main Trading Runner

After trial and error, I decided to use a seperate file to join Step 1 (the Yahoo Finance logic) and Step 2 (the Alpaca logic) since their dependencies differ. So, I created a seperate python enviorment for each using Anaconda and automated the running process. My main_runner.py file runs the yfinance_ML.py file to give me the stocks I want to buy and next runs the alpaca_trader.py to actually process trades. 

A lot of the work in the main file was searching for file and venv locations and coordinating them together. Additonally, making the program compatible for all operating systems added a few more lines of code too.

---

## How to Use the Trading Bot

Follow these steps to run the automated trading bot:

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

> Alternatively, if you’re using Conda:
```bash
conda create -n yfinance_env python=3.10
conda create -n alpaca_env python=3.10
```

### 3. Install Dependencies

Activate each environment and install required packages.

**In `yfinance_env`:**

```bash
# Activate (Windows)
yfinance_env\Scripts\activate

# Activate (macOS/Linux)
source yfinance_env/bin/activate

pip install yfinance pandas numpy scikit-learn lxml
```

**In `alpaca_env`:**

```bash
# Activate (Windows)
alpaca_env\Scripts\activate

# Activate (macOS/Linux)
source alpaca_env/bin/activate

pip install alpaca-trade-api pandas numpy python-dotenv
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

This will:

- Analyze and rank stocks based on ML-predicted Sharpe ratio.
- Wait for the rankings to be generated.
- Sell old positions and buy the top 10 ranked stocks.

---

**File Structure:**

```
your_project/
├── trader/
│   ├── __init__.py
│   ├── yfinance_ML.py
│   └── alpaca_trader.py
├── yfinance_env/
├── alpaca_env/
├── shared_data/
├── .env
└── main_runner.py
```
