import subprocess
import sys
import os
import time
from datetime import datetime

def run_command(command, env_name):
    try:
        print(f"Running in {env_name} environment...")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"{env_name} completed successfully")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"{env_name} failed:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"Error running {env_name}: {e}")
        return False
    
    return True

def check_file_exists(filepath):
    return os.path.exists(filepath)

def wait_for_rankings():
    print("Waiting for rankings to be generated...")
    max_wait = 60 
    wait_time = 0
    
    while wait_time < max_wait:
        if os.path.exists('shared_data') and any(f.startswith('rankings_') for f in os.listdir('shared_data')):
            print("Rankings found!")
            return True
        time.sleep(5)
        wait_time += 5
        print(f"Still waiting... ({wait_time}s)")
    
    print("Timeout waiting for rankings")
    return False

def run_data_analysis():
    print("=" * 50)
    print("STEP 1: STOCK ANALYSIS")
    print("=" * 50)
    
    if os.name == 'nt': 
        python_exec = os.path.join("yfinance_env", "python.exe")
    else:  
        python_exec = os.path.join("yfinance_env", "bin", "python") 

    command = f'"{python_exec}" -m trader.yfinance_ML'
    success = run_command(command, "Data Analysis")

    if success:
        return wait_for_rankings()
    
    return False

def run_trading():
    print("=" * 50)
    print("STEP 2: TRADE EXECUTION")
    print("=" * 50)
    
    if os.name == 'nt': 
        python_exec = os.path.join("alpaca_env", "python.exe")
    else:
        python_exec = os.path.join("alpaca_env", "bin", "python")

    command = f'"{python_exec}" -m trader.alpaca_trader'
    return run_command(command, "Trading")

def check_prerequisites():
    print("Checking prerequisites...")
    
    required_files = ['trader/yfinance_ML.py', 'trader/alpaca_trader.py']
    required_dirs = ['yfinance_env', 'alpaca_env']
    
    for file in required_files:
        if not check_file_exists(file):
            print(f"Missing required file: {file}")
            return False
    
    for directory in required_dirs:
        if not check_file_exists(directory):
            print(f"Missing required environment: {directory}")
            print(f"Create it with: python -m venv {directory}")
            return False
    
    print("All prerequisites found")
    return True

def main():
    print("🚀 AUTOMATED TRADING SYSTEM STARTING")
    print(f"Time: {datetime.now()}")
    print("=" * 50)
    
    if not check_prerequisites():
        print("Prerequisites not met. Please set up environments and files first.")
        return False
    
    if not run_data_analysis():
        print("Data analysis failed. Stopping.")
        return False
    
    print("\n⏳ Waiting 10 seconds before trading...")
    time.sleep(10)
    
    if not run_trading():
        print("Trading failed.")
        return False
    
    print("=" * 50)
    print("TRADING SYSTEM COMPLETED SUCCESSFULLY!")
    print(f"Time: {datetime.now()}")
    print("=" * 50)
    
    return True

def show_help():
    print("""
Automated Trading System Runner

Usage:
    python main_runner.py           # Run the complete system
    python main_runner.py --help    # Show this help

Prerequisites:
1. Create environments:
   python -m venv yfinance_env
   python -m venv alpaca_env

2. Install packages:
   # In yfinance_env:
   pip install yfinance pandas numpy scikit-learn lxml
   
   # In alpaca_env:
   pip install alpaca-trade-api pandas numpy

3. Have these files (inside /trader folder):
   - yfinance_ML.py
   - alpaca_trader.py

File structure should be:
    your_project/
    ├── trader/
    │   ├── __init__.py
    │   ├── yfinance_ML.py
    │   └── alpaca_trader.py
    ├── main_runner.py      # (this file)
    ├── yfinance_env/
    ├── alpaca_env/
    └── shared_data/        # (created automatically)
    """)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h', 'help']:
        show_help()
    else:
        try:
            success = main()
            sys.exit(0 if success else 1)
        except KeyboardInterrupt:
            print("\nTrading system stopped by user")
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected error: {e}")
            sys.exit(1)


