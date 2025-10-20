#!/usr/bin/env python3
"""
Debug script to test plan parser
"""

import asyncio
from src.terraform.cli import TerraformCLI
from src.core.config import Config

async def debug_parser():
    """Debug the plan parser"""
    config = Config()
    cli = TerraformCLI(terraform_path=config.terraform_path, working_dir=config.terraform_dir)

    # Run plan
    print("Running terraform plan...")
    result = await cli.plan(detailed_exitcode=True)

    if result.success:
        print("\n" + "="*80)
        print("PARSING PLAN OUTPUT")
        print("="*80)

        # Parse summary
        summary = cli.get_plan_summary(result.stdout)
        print(f"\nSummary: {summary}")

        # Parse details
        details = cli.parse_plan_details(result.stdout)
        print(f"\nDetails: {details}")

        # Show a snippet of the plan output
        print("\n" + "="*80)
        print("PLAN OUTPUT SNIPPET (first 50 lines)")
        print("="*80)
        lines = result.stdout.split("\n")
        for i, line in enumerate(lines[:50], 1):
            print(f"{i:3}: {line}")

if __name__ == "__main__":
    asyncio.run(debug_parser())
