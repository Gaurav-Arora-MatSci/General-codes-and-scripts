#!/usr/bin/env python3
"""
===============================================================================
extract_cfgs.py

This script extracts specific configuration blocks from a .cfg file generated
from VASP/OUTCAR using MTP (or similar tools). Each configuration is bounded
by markers:

    BEGIN_CFG
    ...
    END_CFG

The script supports three extraction modes (which can be combined):

1. --config N      : Extract a specific configuration number (1-based index).
                     Example: --config 5 → only the 5th configuration.

2. --last N        : Extract the last N configurations in the file.
                     Example: --last 20 → last 20 configurations.

3. --every K       : Extract every K-th configuration.
                     Example: --every 5 → every 5th configuration.

You can also combine options. For example:
    --config 5 --last 20 --every 5

This will extract:
    - The 5th configuration,
    - The last 20 configurations,
    - Every 5th configuration,
and save them (without duplicates) to the specified output file.

USAGE EXAMPLES:
---------------
Extract every 5th configuration:
    python extract_cfgs.py --input all_configs.cfg --output every5.cfg --every 5

Extract last 20 configurations:
    python extract_cfgs.py --input all_configs.cfg --output last20.cfg --last 20

Extract only the 5th configuration:
    python extract_cfgs.py --input all_configs.cfg --output config5.cfg --config 5

Extract a combination (5th, last 20, and every 5th):
    python extract_cfgs.py --input all_configs.cfg --output combined.cfg --config 5 --last 20 --every 5
===============================================================================
"""

import argparse

def extract_cfgs(input_file, output_file, 
                 config_number=None, 
                 last_n=None, 
                 every_k=None):
    """
    Extract configurations from a .cfg file based on given options.
    """
    with open(input_file, "r") as f:
        lines = f.readlines()

    # Split file into separate configuration blocks
    configs = []
    current_cfg = []
    for line in lines:
        if line.strip() == "BEGIN_CFG":
            # Start a new config block
            current_cfg = [line]
        elif line.strip() == "END_CFG":
            # End of config block → save it
            current_cfg.append(line)
            configs.append(current_cfg)
            current_cfg = []
        else:
            # Accumulate lines for current config
            if current_cfg is not None:
                current_cfg.append(line)

    selected_cfgs = []

    # Option 1: Extract a specific config by index
    if config_number is not None and 1 <= config_number <= len(configs):
        selected_cfgs.append(configs[config_number - 1])

    # Option 2: Extract last n configs
    if last_n is not None and last_n > 0:
        selected_cfgs.extend(configs[-last_n:])

    # Option 3: Extract every k-th config
    if every_k is not None and every_k > 0:
        selected_cfgs.extend(configs[i] for i in range(0, len(configs), every_k))

    # Remove duplicates while preserving order
    seen = set()
    unique_cfgs = []
    for cfg in selected_cfgs:
        cfg_id = id(cfg)  # Use object ID to detect uniqueness
        if cfg_id not in seen:
            unique_cfgs.append(cfg)
            seen.add(cfg_id)

    # Write results into output file
    with open(output_file, "w") as f:
        for cfg in unique_cfgs:
            f.writelines(cfg)

    print(f"Extracted {len(unique_cfgs)} configurations into {output_file}")


if __name__ == "__main__":
    # Command-line argument parsing
    parser = argparse.ArgumentParser(
        description="Extract specific configurations from a .cfg file"
    )
    parser.add_argument("--input", required=True, help="Path to input .cfg file")
    parser.add_argument("--output", required=True, help="Path to save extracted configurations")
    parser.add_argument("--config", type=int, help="Extract specific config number (1-based index)")
    parser.add_argument("--last", type=int, help="Extract last N configs")
    parser.add_argument("--every", type=int, help="Extract every K-th config")

    args = parser.parse_args()

    # Call extraction function with user options
    extract_cfgs(
        input_file=args.input,
        output_file=args.output,
        config_number=args.config,
        last_n=args.last,
        every_k=args.every
    )
