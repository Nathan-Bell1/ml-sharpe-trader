import alpaca_trade_api as tradeapi
import json
import os
import pandas as pd
import time
from datetime import datetime, timedelta

class AlpacaTrader:
    def __init__(self, api_key, secret_key, base_url):
        
        self.api = tradeapi.REST(
            key_id=api_key,
            secret_key=secret_key,
            base_url=base_url
        )

        self.positions_file = 'shared_data/current_positions.json'
        self.trades_log = 'shared_data/trades_log.json'
        self.ensure_directories()
        
    def ensure_directories(self):
        if not os.path.exists('shared_data'):
            os.makedirs('shared_data')
    
    def get_account_info(self):
        try:
            account = self.api.get_account()
            return {
                'buying_power': float(account.buying_power),
                'cash': float(account.cash),
                'portfolio_value': float(account.portfolio_value),
                'day_trade_count': int(account.daytrade_count)
            }
        except Exception as e:
            print(f"Error getting account info: {e}")
            return None
    
    def load_ranked_stocks(self):
        try:
            ranking_files = [f for f in os.listdir('shared_data') if f.startswith('rankings_')]
            if not ranking_files:
                print("No ranking files found")
                return None
                
            latest_file = max(ranking_files, key=lambda x: os.path.getctime(f'shared_data/{x}'))
            
            with open(f'shared_data/{latest_file}', 'r') as f:
                rankings = json.load(f)
            
            print(f"Loaded rankings from {latest_file}")
            return rankings
            
        except Exception as e:
            print(f"Error loading rankings: {e}")
            return None
    
    def load_current_positions(self):
        try:
            with open(self.positions_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except Exception as e:
            print(f"Error loading positions: {e}")
            return {}
    
    def save_current_positions(self, positions):
        try:
            with open(self.positions_file, 'w') as f:
                json.dump(positions, f, indent=2)
        except Exception as e:
            print(f"Error saving positions: {e}")
    
    def log_trade(self, trade_info):
        try:
            try:
                with open(self.trades_log, 'r') as f:
                    trades = json.load(f)
            except FileNotFoundError:
                trades = []
            
            trades.append(trade_info)
            
            with open(self.trades_log, 'w') as f:
                json.dump(trades, f, indent=2)
                
        except Exception as e:
            print(f"Error logging trade: {e}")
    
    def get_current_positions(self):
        try:
            positions = self.api.list_positions()
            return {pos.symbol: {
                'qty': float(pos.qty),
                'market_value': float(pos.market_value),
                'avg_entry_price': float(pos.avg_entry_price),
                'unrealized_pl': float(pos.unrealized_pl)
            } for pos in positions}
        except Exception as e:
            print(f"Error getting current positions: {e}")
            return {}
    
    def calculate_position_size(self, account_info, num_positions=10):
        available_cash = account_info['buying_power'] * 0.9
        position_size = available_cash / num_positions
        return position_size
    
    def get_stock_price(self, symbol):
        try:
            latest_trade = self.api.get_latest_trade(symbol)
            return float(latest_trade.price)
        except Exception as e:
            print(f"Error getting price for {symbol}: {e}")
            return None
    
    def sell_all_positions(self):
        current_positions = self.get_current_positions()
        positions_data = self.load_current_positions()
        
        for symbol in current_positions:
            try:
                qty = current_positions[symbol]['qty']
                if qty > 0: 
                    order = self.api.submit_order(
                        symbol=symbol,
                        qty=abs(qty),
                        side='sell',
                        type='market',
                        time_in_force='gtc'
                    )
                    
                    trade_info = {
                        'timestamp': datetime.now().isoformat(),
                        'symbol': symbol,
                        'action': 'SELL',
                        'quantity': abs(qty),
                        'type': 'market',
                        'order_id': order.id,
                        'reason': 'daily_rebalance'
                    }
                    self.log_trade(trade_info)
                    
                    print(f"SELL order submitted: {symbol} x{abs(qty)}")
                    
            except Exception as e:
                print(f"Error selling {symbol}: {e}")
        
        self.save_current_positions({})
        
        print("Waiting 30 seconds for sell orders to execute...")
        time.sleep(30)
    
    def buy_top_stocks(self, top_n=10):
        rankings = self.load_ranked_stocks()
        if not rankings:
            print("No rankings available for trading")
            return
        
        account_info = self.get_account_info()
        if not account_info:
            print("Could not get account information")
            return
        
        print(f"Account Info: Buying Power: ${account_info['buying_power']:,.2f}")
        
        position_size = self.calculate_position_size(account_info, top_n)
        print(f"Position size per stock: ${position_size:,.2f}")
        
        top_stocks = rankings[:top_n]
        new_positions = {}
        
        for stock_data in top_stocks:
            symbol = stock_data['ticker']
            sharpe_ratio = stock_data['sharpe_ratio']
            
            try:
                current_price = self.get_stock_price(symbol)
                if not current_price:
                    continue
                
                qty = int(position_size / current_price)
                
                if qty > 0:
                    order = self.api.submit_order(
                        symbol=symbol,
                        qty=qty,
                        side='buy',
                        type='market',
                        time_in_force='gtc'
                    )
                    
                    new_positions[symbol] = {
                        'quantity': qty,
                        'expected_price': current_price,
                        'sharpe_ratio': sharpe_ratio,
                        'order_id': order.id,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    trade_info = {
                        'timestamp': datetime.now().isoformat(),
                        'symbol': symbol,
                        'action': 'BUY',
                        'quantity': qty,
                        'expected_price': current_price,
                        'sharpe_ratio': sharpe_ratio,
                        'type': 'market',
                        'order_id': order.id,
                        'reason': 'top_ranked_stock'
                    }
                    self.log_trade(trade_info)
                    
                    print(f"BUY order submitted: {symbol} x{qty} @ ${current_price:.2f} (Sharpe: {sharpe_ratio:.3f})")
                    
                else:
                    print(f"Position size too small for {symbol} @ ${current_price:.2f}")
                    
            except Exception as e:
                print(f"Error buying {symbol}: {e}")
        
        self.save_current_positions(new_positions)
        print(f"Submitted buy orders for {len(new_positions)} stocks")
    
    def rebalance_portfolio(self, top_n=10):
        print("=== Starting Portfolio Rebalance ===")
        print(f"Time: {datetime.now()}")
        
        print("Step 1: Selling all current positions...")
        self.sell_all_positions()
        
        print("Step 2: Buying top ranked stocks...")
        self.buy_top_stocks(top_n)
        
        print("=== Rebalance Complete ===")
    
    def get_portfolio_summary(self):
        try:
            account = self.api.get_account()
            positions = self.get_current_positions()
            
            summary = {
                'timestamp': datetime.now().isoformat(),
                'total_portfolio_value': float(account.portfolio_value),
                'cash': float(account.cash),
                'day_change': float(account.portfolio_value) - float(account.last_equity),
                'total_positions': len(positions),
                'positions': positions
            }
            
            return summary
            
        except Exception as e:
            print(f"Error getting portfolio summary: {e}")
            return None
    
    def save_rankings_for_trading(self, df_ranked):
        try:
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
            
            print(f"Rankings saved to {filename}")
            return filename
            
        except Exception as e:
            print(f"Error saving rankings: {e}")
            return None

def main():
    trader = AlpacaTrader(
        api_key='PKENGBXJUZZHSHD36D5Q',
        secret_key='4H6wniwOKCU78XyCuWMBb7HZxrZdkGDyuL98tmIX',
        base_url='https://paper-api.alpaca.markets'
    )
    
    account_info = trader.get_account_info()
    if account_info:
        print("Account Status:")
        print(f"  Portfolio Value: ${account_info['portfolio_value']:,.2f}")
        print(f"  Buying Power: ${account_info['buying_power']:,.2f}")
        print(f"  Cash: ${account_info['cash']:,.2f}")
    else:
        print("Could not connect to Alpaca API")
        return
    
    trader.rebalance_portfolio(top_n=10)
    
    summary = trader.get_portfolio_summary()
    if summary:
        print("\nPortfolio Summary:")
        print(f"  Total Value: ${summary['total_portfolio_value']:,.2f}")
        print(f"  Day Change: ${summary['day_change']:,.2f}")

if __name__ == "__main__":
    main()