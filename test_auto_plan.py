#!/usr/bin/env python3
"""
Test script to verify intelligent auto-plan detection
"""

import asyncio
from src.core.agent import TerraformAgent
from src.core.config import Config

async def test_auto_plan():
    """Test that agent automatically runs plan when needed"""
    config = Config()
    agent = TerraformAgent(config)

    print("=" * 80)
    print("Testing Intelligent Auto-Plan Detection")
    print("=" * 80)
    print()
    print("Starting with FRESH agent (no plan context)")
    print()
    print("User Query: 'explain the resources that are changing based on the plan'")
    print()
    print("Expected Behavior: Agent should detect it needs plan context")
    print("                   and automatically run 'terraform plan' first")
    print()
    print("=" * 80)
    print()

    # Ask about plan without running it first
    # The agent should be smart enough to run plan automatically
    response = await agent.process_command_async(
        'explain the resources that are changing based on the plan'
    )

    print("AGENT RESPONSE:")
    print(response)
    print()
    print("=" * 80)
    print()

    # Verify that plan was actually run
    if agent.last_plan_details:
        print("✅ SUCCESS: Agent automatically ran terraform plan!")
        print(f"   Plan summary: {agent.last_plan_summary}")
        print(f"   Details captured: {len(agent.last_plan_details.get('resources_to_change', []))} resources to change")
    else:
        print("❌ FAILED: Agent did not run plan automatically")

if __name__ == "__main__":
    asyncio.run(test_auto_plan())
