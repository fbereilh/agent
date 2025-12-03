"""Quick test script for the agent."""

import os
from agent import RestaurantAgent
from dotenv import load_dotenv

load_dotenv()

# Check if API key is loaded
api_key = os.getenv("ANTHROPIC_API_KEY")
print(f"API Key loaded: {'Yes' if api_key else 'No'}")
if api_key:
    print(f"Key starts with: {api_key[:10]}...")

# Initialize agent
print("\nInitializing agent...")
agent = RestaurantAgent(db_path='test_chromadb')

# Send test message
print("\nSending message: 'Hola'")
response = agent('Hola')

print(f"\nAgent response:\n{response}")
print(f"\nTotal messages in history: {len(agent.history)}")
