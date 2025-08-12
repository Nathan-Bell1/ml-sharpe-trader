import json
import os
import pandas as pd
import yfinance as yf
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

def get_sp500_tickers():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    table = pd.read_html(url)[0]
    return [ticker.replace(".", "-") for ticker in table['Symbol'].tolist()]

class TradingEngine:
    def __init__(self, balance=100_000):
        self.balance = balance
        self.portfolio = {}

    def fetch_data(self, ticker, period="1y", interval="1d"):
        df = yf.download(ticker, period=period, interval=interval, auto_adjust=True, progress=False)
        df.dropna(inplace=True)
        df['Return'] = df['Close'].pct_change()

        df['ReturnTarget'] = df['Return'].shift(-1)  
        df['VolatilityTarget'] = df['Return'].rolling(5).std().shift(-1)  

        df.dropna(inplace=True)
        return df

    def train_models(self, df):
        features = ['Open', 'High', 'Low', 'Close', 'Volume']
        X = df[features]

        y_return = df['ReturnTarget']
        y_vol = df['VolatilityTarget']

        X_train, X_test, y_train_r, y_test_r = train_test_split(X, y_return, test_size=0.2, shuffle=False)
        _, _, y_train_v, y_test_v = train_test_split(X, y_vol, test_size=0.2, shuffle=False)

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        model_return = RandomForestRegressor(n_estimators=100, random_state=42)
        model_vol = RandomForestRegressor(n_estimators=100, random_state=42)

        model_return.fit(X_train_scaled, y_train_r)
        model_vol.fit(X_train_scaled, y_train_v)

        return model_return, model_vol, scaler

    def predict_sharpe(self, model_return, model_vol, scaler, df):
        latest = df[['Open', 'High', 'Low', 'Close', 'Volume']].iloc[-1:]
        X_latest = scaler.transform(latest)

        pred_return = model_return.predict(X_latest)[0]
        pred_vol = model_vol.predict(X_latest)[0]

        if pred_vol == 0:
            return -999 

        sharpe = pred_return / pred_vol
        return sharpe

    def rank_stocks(self, tickers):
        scores = []
        total = len(tickers)
        for i, ticker in enumerate(tickers, 1):
            try:
                df = self.fetch_data(ticker)
                model_return, model_vol, scaler = self.train_models(df)
                sharpe = self.predict_sharpe(model_return, model_vol, scaler, df)
                scores.append((ticker, sharpe))
            except Exception as e:
                print(f"Error processing {ticker}: {e}")
        ranked = sorted(scores, key=lambda x: x[1], reverse=True)
        return ranked

    def save_rankings_for_alpaca(self, df_ranked):
        try:
            if not os.path.exists('shared_data'):
                os.makedirs('shared_data')

            rankings = []
            for _, row in df_ranked.iterrows():
                rankings.append({
                    'ticker': row['Ticker'],
                    'sharpe_ratio': float(row['SharpeRatio'])
                })

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'shared_data/rankings_{timestamp}.json'

            with open(filename, 'w') as f:
                json.dump(rankings, f, indent=2)

            return filename

        except Exception as e:
            print(f"Error saving rankings: {e}")
            return None

    def save_current_holdings(self, holdings):
        try:
            if not os.path.exists('shared_data'):
                os.makedirs('shared_data')

            filename = 'shared_data/current_holdings.json'
            with open(filename, 'w') as f:
                json.dump(holdings, f, indent=2)
        except Exception as e:
            print(f"Error saving holdings: {e}")

    def run(self, tickers=None, top_n=10):
        if tickers is None:
            tickers = get_sp500_tickers()

        ranked = self.rank_stocks(tickers[:])

        df_ranked = pd.DataFrame(ranked, columns=['Ticker', 'SharpeRatio'])
        df_ranked = df_ranked.sort_values(by='SharpeRatio', ascending=False).head(top_n)

        self.save_rankings_for_alpaca(df_ranked)

        updated_holdings = {row['Ticker']: {'sharpe_ratio': row['SharpeRatio']} for _, row in df_ranked.iterrows()}
        self.save_current_holdings(updated_holdings)

        return df_ranked

if __name__ == "__main__":
    engine = TradingEngine()
    df = engine.run(tickers=None, top_n=10)
