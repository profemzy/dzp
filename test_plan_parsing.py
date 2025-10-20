#!/usr/bin/env python3
"""
Test script to verify enhanced plan parsing
"""

import asyncio
from src.core.agent import TerraformAgent
from src.core.config import Config

async def test_plan_parsing():
    """Test the enhanced plan parsing"""
    config = Config()
    agent = TerraformAgent(config)

    print("=" * 80)
    print("Testing Enhanced Plan Parsing")
    print("=" * 80)
    print()

    # Run terraform plan
    print("1. Running terraform plan...")
    response1 = await agent.process_command_async('terraform plan')
    print(response1)
    print()
    print("=" * 80)
    print()

    # Ask about details
    print("2. Asking about what's changing...")
    response2 = await agent.process_command_async('what resources are being changed or created?')
    print(response2)
    print()
    print("=" * 80)
    print()

    # Ask for more details
    print("3. Asking for specific attribute changes...")
    response3 = await agent.process_command_async('show me the details of what\'s changing')
    print(response3)
    print()

if __name__ == "__main__":
    asyncio.run(test_plan_parsing())
