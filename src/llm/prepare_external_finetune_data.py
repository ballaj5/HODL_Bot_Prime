# src/llm/prepare_external_finetune_data.py
import os
import json
import logging
import pandas as pd
import argparse
from datasets import load_dataset

# --- Assuming these modules are in the python path ---
from src.utils.indicators import compute_indicators

# --- Configuration ---
FINETUNE_OUTPUT_PATH = "/workspace/data/finetuning"
os.makedirs(FINETUNE_OUTPUT_PATH, exist_ok=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_analysis_and_target(row: pd.Series) -> (str, str):
    """
    Generates a human-like analysis based on indicator values and determines the target direction.
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

    target_direction = "UP" if row['target'] == 1 else "DOWN"
    full_analysis = " ".join(analysis_parts)
    full_analysis += f" Based on this combination of factors, the likely short-term price direction is {target_direction}."
    
    return full_analysis, target_direction

def create_dataset_from_hf(max_rows: int):
    """
    Downloads the sebdg/crypto_data dataset, processes it, and saves it as a JSONL file.

    Args:
        max_rows (int): The maximum number of rows to process from the dataset.
    """
    logging.info("🚀 Downloading 'sebdg/crypto_data' from Hugging Face Hub...")
    
    try:
        # Load the dataset, streaming to handle potentially large size
        dataset = load_dataset("sebdg/crypto_data", split='train', streaming=True)
        
        # Take a limited number of rows for processing
        dataset_sample = dataset.take(max_rows)
        
        # Convert to pandas DataFrame
        df = pd.DataFrame(dataset_sample)
        logging.info(f"Successfully downloaded and sampled {len(df)} rows.")

    except Exception as e:
        logging.error(f"❌ Failed to download or process dataset from Hugging Face: {e}", exc_info=True)
        return

    finetune_data = []
    
    # The dataset is for a single asset, so we can process it as one block
    try:
        # Compute indicators and the target variable
        df_with_features = compute_indicators(df.copy())
        df_with_features['target'] = (df_with_features['close'].shift(-1) > df_with_features['close']).astype(int)
        df_with_features.dropna(inplace=True)

        logging.info(f"Processing {len(df_with_features)} records for the fine-tuning dataset...")

        for _, row in df_with_features.iterrows():
            instruction_input = (
                f"Analyze the following market data for {row.get('symbol', 'the asset')} and provide a rationale for the likely price movement:\n"
                f"- RSI: {row['rsi']:.2f}\n"
                f"- MACD: {row['macd']:.6f}\n"
                f"- EMA: {row['ema']:.4f}\n"
                f"- Current Close Price: {row['close']:.4f}"
            )
            
            expert_analysis, _ = generate_analysis_and_target(row)

            finetune_data.append({
                "instruction": "You are a crypto trading analyst. Your task is to analyze technical indicators and provide a brief, reasoned outlook on the asset's next likely price movement.",
                "input": instruction_input,
                "output": expert_analysis
            })

    except Exception as e:
        logging.error(f"Failed during feature engineering: {e}", exc_info=True)
        return

    # Save the final dataset to a JSONL file
    output_filename = "external_finetune_dataset.jsonl"
    output_filepath = os.path.join(FINETUNE_OUTPUT_PATH, output_filename)

    with open(output_filepath, 'w') as f:
        for entry in finetune_data:
            f.write(json.dumps(entry) + '\n')
            
    logging.info(f"✅ Successfully created external fine-tuning dataset with {len(finetune_data)} entries.")
    logging.info(f"File saved to: {output_filepath}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare external Hugging Face dataset for LLM fine-tuning.")
    parser.add_argument(
        "--max_rows",
        type=int,
        default=50000,
        help="The maximum number of rows to process from the dataset. Default is 50,000."
    )
    args = parser.parse_args()
    
    create_dataset_from_hf(args.max_rows)
