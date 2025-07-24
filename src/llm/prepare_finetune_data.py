# src/llm/prepare_finetune_data.py
import os
import json
import logging
import pandas as pd
from datetime import datetime, timedelta
import argparse

# --- Assuming these modules are in the python path when running from the root ---
from src.shared.constants import SYMBOLS, ALL_TIMEFRAMES
from src.utils.indicators import compute_indicators

# --- Configuration ---
HISTORY_DATA_PATH = "/workspace/data/history"
FINETUNE_OUTPUT_PATH = "/workspace/data/finetuning"
os.makedirs(FINETUNE_OUTPUT_PATH, exist_ok=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_analysis_and_target(row: pd.Series) -> (str, str):
    """
    Generates a human-like analysis based on indicator values and determines the target direction.
    
    Args:
        row: A pandas Series representing a single row of data with indicator columns.
        
    Returns:
        A tuple containing (analysis_text, target_direction).
    """
    analysis_parts = []
    
    # Analyze RSI
    if row['rsi'] > 70:
        analysis_parts.append(f"RSI is at {row['rsi']:.1f}, indicating the asset may be overbought.")
    elif row['rsi'] < 30:
        analysis_parts.append(f"RSI is at {row['rsi']:.1f}, indicating the asset may be oversold.")
    else:
        analysis_parts.append(f"RSI is neutral at {row['rsi']:.1f}.")

    # Analyze MACD
    if row['macd'] > 0:
        analysis_parts.append("The MACD is above the signal line, suggesting bullish momentum.")
    else:
        analysis_parts.append("The MACD is below the signal line, suggesting bearish momentum.")
        
    # Analyze Price vs. EMA
    if row['close'] > row['ema']:
        analysis_parts.append(f"The closing price of ${row['close']:.2f} is above its EMA of ${row['ema']:.2f}, which is a positive sign.")
    else:
        analysis_parts.append(f"The closing price of ${row['close']:.2f} is below its EMA of ${row['ema']:.2f}, which is a bearish sign.")

    # Determine the ground-truth target from the data
    target_direction = "UP" if row['target'] == 1 else "DOWN"
    
    # Combine the analysis
    full_analysis = " ".join(analysis_parts)
    full_analysis += f" Based on this combination of factors, the likely short-term price direction is {target_direction}."
    
    return full_analysis, target_direction

def create_finetune_dataset(days: int):
    """
    Processes historical data to create a JSONL dataset for fine-tuning an LLM.

    Args:
        days (int): The number of past days of data to include in the dataset.
    """
    logging.info(f"🚀 Starting dataset creation for the last {days} days of data.")
    
    finetune_data = []
    start_date = datetime.utcnow() - timedelta(days=days)

    for symbol in SYMBOLS:
        for tf in ALL_TIMEFRAMES:
            path = f"{HISTORY_DATA_PATH}/{symbol}USDT_{tf}.csv"
            if not os.path.exists(path):
                logging.warning(f"File not found, skipping: {path}")
                continue

            try:
                df = pd.read_csv(path)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                
                # Filter for the requested date range
                df_filtered = df[df['timestamp'] >= start_date].copy()

                if len(df_filtered) < 50:
                    logging.warning(f"Insufficient data for {symbol}-{tf} in the last {days} days. Skipping.")
                    continue
                
                # Compute indicators and the target variable
                df_with_features = compute_indicators(df_filtered)
                df_with_features['target'] = (df_with_features['close'].shift(-1) > df_with_features['close']).astype(int)
                df_with_features.dropna(inplace=True)

                logging.info(f"Processing {len(df_with_features)} records for {symbol}-{tf}...")

                for _, row in df_with_features.iterrows():
                    # This is the "context" or "input" for the LLM
                    instruction_input = (
                        f"Analyze the following market data for {symbol}/USDT on the {tf} timeframe and provide a rationale for the likely price movement:\n"
                        f"- RSI: {row['rsi']:.2f}\n"
                        f"- MACD: {row['macd']:.6f}\n"
                        f"- EMA: {row['ema']:.4f}\n"
                        f"- Current Close Price: {row['close']:.4f}"
                    )
                    
                    # This is the "expert response" the LLM should learn to generate
                    expert_analysis, _ = generate_analysis_and_target(row)

                    # Format in the standard "instruction" format
                    finetune_data.append({
                        "instruction": "You are a crypto trading analyst. Your task is to analyze technical indicators and provide a brief, reasoned outlook on the asset's next likely price movement.",
                        "input": instruction_input,
                        "output": expert_analysis
                    })

            except Exception as e:
                logging.error(f"Failed to process {symbol}-{tf}: {e}", exc_info=True)

    # Save the final dataset to a JSONL file
    output_filename = f"trading_finetune_dataset_{days}d.jsonl"
    output_filepath = os.path.join(FINETUNE_OUTPUT_PATH, output_filename)

    with open(output_filepath, 'w') as f:
        for entry in finetune_data:
            f.write(json.dumps(entry) + '\n')
            
    logging.info(f"✅ Successfully created fine-tuning dataset with {len(finetune_data)} entries.")
    logging.info(f"File saved to: {output_filepath}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare historical trading data for LLM fine-tuning.")
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="The number of past days of data to process for the dataset. Default is 30."
    )
    args = parser.parse_args()
    
    create_finetune_dataset(args.days)
