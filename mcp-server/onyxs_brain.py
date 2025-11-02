# -*- coding: utf-8 -*-
"""
Onyxs Brain - Interactive Adaptive Fitness AI

This is Onyxs's "brain" - the main conversational interface that remembers
everything you talk about and progressively learns your preferences.
"""

import ollama
import httpx
import json


# ============================================================================
# PART 1: ONYXS'S PERSONALITY
# ============================================================================

SYSTEM_PROMPT = """You are Onyxs, an adaptive fitness and nutrition AI assistant.

Your core traits:
- Helpful and knowledgeable about nutrition, fitness, and health
- Clear and concise in your responses
- Progressively learning - you adapt to how the user communicates
- Friendly but professional

Your goal is to help users understand nutrition and make informed decisions about their health.
When users ask about food, use the search_food function to provide accurate USDA data.
"""


# ============================================================================
# PART 2: TOOLS (FUNCTIONS ONYXS CAN USE)
# ============================================================================

tools = [
    {
        'type': 'function',
        'function': {
            'name': 'search_food',
            'description': 'Search the USDA nutrition database for food information including calories, protein, carbs, and fat',
            'parameters': {
                'type': 'object',
                'properties': {
                    'query': {
                        'type': 'string',
                        'description': 'The food name to search for (e.g., "chicken breast", "apple", "salmon")',
                    },
                    'limit': {
                        'type': 'integer',
                        'description': 'Number of results to return (default: 15)',
                    },
                },
                'required': ['query'],
            },
        },
    },
]


# ============================================================================
# PART 3: THE ACTUAL FUNCTIONS
# ============================================================================

def search_food(query: str, limit: int = 15):
    """
    Searches the USDA nutrition database via your FastAPI server

    This is what actually gets called when Onyxs decides it needs nutrition data.
    """
    url = "http://127.0.0.1:8000/search_food"

    response = httpx.post(
        url,
        json={"query": query, "limit": limit}
    )

    return response.json()


# ============================================================================
# PART 4: ONYXS'S BRAIN - THE MAIN CHAT FUNCTION
# ============================================================================

def chat_with_onyxs():
    """
    This is Onyxs's brain - the main interactive chat loop.

    It maintains conversation memory and handles continuous dialogue.
    """

    # Welcome message
    print("\n" + "="*70)
    print(">� ONYXS - Your Adaptive Fitness AI")
    print("="*70)
    print("\nI'm Onyxs, your fitness and nutrition assistant.")
    print("I remember our conversations and adapt to help you better!")
    print("\nAsk me about nutrition, fitness, or anything health-related.")
    print("Type 'exit', 'quit', or 'bye' to end our conversation.\n")
    print("="*70 + "\n")

    # Initialize conversation history
    # This is Onyxs's "memory" - it stores EVERYTHING we talk about
    conversation_history = [
        {'role': 'system', 'content': SYSTEM_PROMPT}
    ]

    # Available functions that Onyxs can call
    available_functions = {
        'search_food': search_food,
    }

    # Main conversation loop - this keeps going until you say goodbye
    while True:
        # Get your input
        user_input = input("You: ").strip()

        # Check if you want to exit
        if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
            print("\nOnyxs: Goodbye! Stay healthy and keep striving for your goals! =�\n")
            break

        # Skip if you didn't type anything
        if not user_input:
            continue

        # Add your message to Onyxs's memory
        conversation_history.append({
            'role': 'user',
            'content': user_input
        })

        # Send the ENTIRE conversation to Ollama (so it remembers everything)
        response = ollama.chat(
            model='llama3.2:3b',
            messages=conversation_history,
            tools=tools,
        )

        # Check if Onyxs wants to use a tool (like search_food)
        if response['message'].get('tool_calls'):
            # Onyxs decided it needs to call a function!

            for tool in response['message']['tool_calls']:
                function_name = tool['function']['name']
                function_args = tool['function']['arguments']

                # Call the actual Python function
                function_to_call = available_functions[function_name]
                function_response = function_to_call(**function_args)

                # Add the function call and its result to memory
                conversation_history.append(response['message'])
                conversation_history.append({
                    'role': 'tool',
                    'content': json.dumps(function_response),
                })

            # Get Onyxs's final response (now that it has the nutrition data)
            final_response = ollama.chat(
                model='llama3.2:3b',
                messages=conversation_history
            )

            # Add Onyxs's response to memory
            conversation_history.append(final_response['message'])

            # Show you what Onyxs said
            print(f"\nOnyxs: {final_response['message']['content']}\n")

        else:
            # No function needed - Onyxs answered directly
            conversation_history.append(response['message'])
            print(f"\nOnyxs: {response['message']['content']}\n")


# ============================================================================
# PART 5: START ONYXS WHEN THIS FILE RUNS
# ============================================================================

if __name__ == "__main__":
    chat_with_onyxs()
