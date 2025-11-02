import ollama
import httpx
import json

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

def search_food(query: str, limit: int = 15):
    url = "http://127.0.0.1:8000/search_food"

    print(f" 🌐 Making POST request to {url}")
    print(f" 📦 Payload: {{'query': '{query}', 'limit': {limit}}}")

    response = httpx.post(
        url,
        json = {"query": query, "limit": limit}
    )

    return response.json()

def run_conversation(user_query: str):
    print(f"\n{'='*70}")
    print(f"👤 User Query: {user_query}")
    print(f"{'='*70}\n")
    print("📤 Sending query to Ollama with available tools...\n")

    response = ollama.chat(
          model = 'llama3.2:3b',
          messages = [{'role': 'user', 'content': user_query}],
          tools = tools,
          )

    if response['message'].get('tool_calls'):
          print("🤖 Ollama recognized it needs nutrition data!")
          print("🔧 Ollama wants to call a function...\n")

          available_functions = {
          'search_food': search_food,
          }

          for tool in response['message']['tool_calls']:
            function_name = tool['function']['name']
            function_args = tool['function']['arguments']

            print(f"📞 Function to call: {function_name}")
            print(f"📝 Arguments: {json.dumps(function_args, indent=2)}\n")

            function_to_call = available_functions[function_name]
            function_response = function_to_call(**function_args)

            print(f"\n✅ Got response from API")
            print(f"📊 Total hits: {function_response.get('totalHits', 'N/A')}")
            
            if function_response.get('foods'):
                print(f"📦 Returned {len(function_response['foods'])} food items\n")

            print("📨 Sending API results back to Ollama for formatting...\n")

            messages = [
                {'role': 'user', 'content': user_query},
                response['message'],
                {
                    'role': 'tool',
                    'content': json.dumps(function_response),
                },
            ]

            final_response = ollama.chat(
                model = 'llama3.2:3b',
                messages=messages
            )

            print(f"{'='*70}")
            print("🎯 OLLAMA'S FINAL RESPONSE:")
            print(f"{'='*70}")
            print(final_response['message']['content'])
            print(f"{'='*70}\n")

    else:
        print("💬 Ollama responded directly (no function call needed):")
        print(response['message']['content'])
        print()


if __name__ == "__main__":
    print("\n🚀 OLLAMA + FASTAPI INTEGRATION TEST")
    print("="*70)
    print("This demonstrates Ollama using function calling to search nutrition data")
    print("="*70)

    run_conversation("What's the nutrition information for grilled chicken breasts?")

