#https://claude.ai/share/1110915a-b0c0-4117-a22d-9a8641b16fe8

I'll create a comprehensive example showing how to implement tool calling with LLMs using the Google Maps API, Python backend, and Svelte frontend.Now let me create the Svelte frontend:Now let me create the setup instructions and requirements:I've created a comprehensive example of tool calling with LLMs using Ollama, Google Maps APIs, Python (FastAPI), and Svelte. Here's what the example includes:

## Key Components:

1. **Python Backend** (`main.py`):
   - FastAPI server with CORS support for Svelte
   - Integration with Ollama using the `qwen2.5:14b` model
   - Three Google Maps API tools: `search_places`, `get_directions`, and `geocode_address`
   - Proper error handling and structured responses

2. **Svelte Frontend** (`App.svelte`):
   - Interactive chat interface with real-time messaging
   - Integrated Google Maps with markers and info windows
   - Responsive design that works on desktop and mobile
   - Visual loading states and typing indicators

3. **Setup Instructions**:
   - Complete installation and configuration guide
   - Environment setup for both backend and frontend
   - Troubleshooting tips and customization options

## How Tool Calling Works:

1. **User asks a question** like "Find pizza restaurants near Times Square"
2. **Ollama analyzes the query** and determines it needs to call the `search_places` tool
3. **Backend executes the Google Maps API call** with the extracted parameters
4. **Results are passed back to Ollama** to generate a natural language response
5. **Frontend displays the response** and updates the map with markers

## Example Queries to Try:

- "Find coffee shops in downtown Seattle"
- "Get driving directions from the Golden Gate Bridge to Fisherman's Wharf"
- "What are the coordinates of the Empire State Building?"
- "Show me gas stations between New York and Philadelphia"

The example demonstrates proper tool calling architecture with structured function definitions, parameter validation, and seamless integration between the LLM, APIs, and user interface. The code is production-ready with proper error handling, CORS configuration, and responsive design.

Would you like me to explain any specific part in more detail or help you customize it for your particular use case?
