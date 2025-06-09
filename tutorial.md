# Building an AI Maps Assistant with Tool Calling: A Complete Guide Using OpenStreetMap and Ollama

Tool calling is one of the most powerful features of modern AI assistants, allowing them to interact with external APIs and perform real-world actions. In this comprehensive tutorial, we'll build a Maps AI Assistant that can search for places, get directions, and geocode addresses using completely free OpenStreetMap APIs.

## What You'll Learn

By the end of this tutorial, you'll understand:
- How tool calling works with Large Language Models
- How to implement function calling with Ollama
- Building a FastAPI backend with tool definitions
- Creating an interactive frontend with SvelteKit and Leaflet maps
- Using free OpenStreetMap APIs (no API keys required!)

## Architecture Overview

Our application follows this flow:

```
User Query → SvelteKit Frontend → FastAPI Backend → Ollama LLM
                                        ↓
                                 Tool Definitions
                                        ↓
                              OpenStreetMap APIs
                              (Nominatim, OSM tiles)
                                        ↓
                                Structured Results
                                        ↓
                              Natural Language Response
                                        ↓
                              Updated Map Visualization
```

## Prerequisites

Before we start, make sure you have:
- Python 3.8+ installed
- Node.js 16+ installed
- Ollama installed with a compatible model
- Basic knowledge of Python, JavaScript, and REST APIs

## Understanding Tool Calling

Tool calling allows AI models to execute predefined functions during conversations. Instead of just generating text, the model can:

1. **Analyze user queries** to determine if external tools are needed
2. **Call specific functions** with appropriate parameters
3. **Process the results** and incorporate them into natural responses
4. **Maintain conversation context** while using tools

This makes AI assistants much more powerful and practical for real-world applications.

## Backend Implementation Deep Dive

### Core Tool Calling Setup

The heart of our backend is the tool definition system. Let's examine how it works:

```python
# Tool definitions tell the LLM what functions are available
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_places",
            "description": "Search for places like restaurants, hotels, attractions, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "What to search for (e.g., 'pizza restaurants')"
                    },
                    "location": {
                        "type": "string", 
                        "description": "Location to search in (city, address, etc.)"
                    }
                },
                "required": ["query"]
            }
        }
    }
]
```

**Key Points:**
- Each tool has a clear **name** and **description**
- **Parameters** are defined with JSON Schema for type safety
- **Required fields** ensure the LLM provides necessary information
- Descriptions help the LLM understand when and how to use each tool

### OpenStreetMap Integration

One of the biggest advantages of our implementation is using completely free APIs:

```python
def search_places(query: str, location: str = "") -> Dict[str, Any]:
    """Search for places using Nominatim (OpenStreetMap)"""
    search_query = f"{query} {location}".strip()
    
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": search_query,
        "format": "json",
        "limit": 5,
        "addressdetails": 1,
        "extratags": 1
    }
    
    headers = {"User-Agent": "MapsAI/1.0"}  # Required by Nominatim
```

**Why OpenStreetMap?**
- **No API keys required** - works immediately
- **No usage limits** for development
- **Global coverage** with detailed data
- **Privacy-focused** - no tracking
- **Community-driven** with frequent updates

### The Tool Execution Flow

Here's how the backend processes tool calls:

1. **Receive user message** and conversation history
2. **Send to Ollama** with tool definitions
3. **Check if tools were called** by the LLM
4. **Execute the functions** and collect results
5. **Send results back to Ollama** for natural language processing
6. **Return final response** with tool metadata

```python
# The LLM decides to call tools
if assistant_message.get('tool_calls'):
    for tool_call in assistant_message['tool_calls']:
        function_name = tool_call['function']['name']
        arguments = tool_call['function']['arguments']
        
        # Execute the actual function
        if function_name in available_functions:
            function_result = available_functions[function_name](**arguments)
            
        # Store results for the LLM to process
        tool_calls_made.append({
            "function": function_name,
            "arguments": arguments,
            "result": function_result
        })
```

## Frontend Implementation Explained

### Modern SvelteKit Architecture

Our frontend uses SvelteKit with modern Svelte 5 patterns:

```javascript
let messages = [];
let userInput = '';
let isLoading = false;
let map;
let markers = [];
```

**State Management:**
- **Reactive variables** automatically update the UI
- **Conversation history** maintained in memory
- **Loading states** provide user feedback
- **Map state** synchronized with chat responses

### Interactive Map Integration

We use Leaflet.js with OpenStreetMap tiles for mapping:

```javascript
function initMap() {
    map = L.map(mapContainer).setView([37.7749, -122.4194], 12);
    
    // Free OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(map);
}
```

**Map Features:**
- **Dynamic marker placement** based on AI responses
- **Custom marker colors** for different types (start/end points)
- **Interactive popups** with detailed information
- **Automatic bounds fitting** to show all relevant locations
- **Route visualization** with polylines

### Real-time Communication

The frontend communicates with the backend via REST API:

```javascript
async function sendMessage() {
    const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            message: userMessage,
            conversation_history: messages.slice(0, -1)
        })
    });
    
    const data = await response.json();
    
    // Update chat and map based on response
    messages = [...messages, { role: 'assistant', content: data.response }];
    
    if (data.map_data && data.map_data.status === 'success') {
        updateMapWithResults(data.map_data);
    }
}
```

## Available Tools Explained

### 1. Place Search (`search_places`)

**Purpose:** Find restaurants, hotels, attractions, etc.
**Uses:** Nominatim geocoding API
**Example:** "Find pizza restaurants in New York"

The function:
- Combines query and location into a search string
- Calls Nominatim API with proper parameters
- Parses results into standardized format
- Returns coordinates and metadata for map display

### 2. Directions (`get_directions`)

**Purpose:** Calculate routes and travel information
**Uses:** Haversine distance formula
**Example:** "Get directions from Paris to London"

The implementation:
- Geocodes both origin and destination
- Calculates straight-line distance using haversine formula
- Estimates travel time based on transportation mode
- Returns structured data for map visualization

### 3. Address Geocoding (`geocode_address`)

**Purpose:** Convert addresses to coordinates
**Uses:** Nominatim geocoding API
**Example:** "Where is the Eiffel Tower?"

The process:
- Sends address query to Nominatim
- Receives detailed location information
- Extracts coordinates and formatted address
- Returns data suitable for single-point mapping

## Setting Up the Development Environment

### Backend Setup

1. **Install dependencies:**
```bash
pip install fastapi uvicorn ollama requests python-multipart
```

2. **Install and configure Ollama:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull qwen2.5:14b
```

3. **Run the backend:**
```bash
python main.py
```

### Frontend Setup

1. **Create SvelteKit project:**
```bash
npx sv create maps-ai-frontend
cd maps-ai-frontend
npm install
```

2. **Replace `src/routes/+page.svelte`** with the provided code

3. **Start development server:**
```bash
npm run dev
```

## Key Features and Benefits

### Cost-Effective Solution
- **$0 API costs** - completely free to run
- **No rate limiting** for development
- **No vendor lock-in** - you control your data
- **Scalable** without increasing API bills

### Technical Advantages
- **Real-time tool calling** with immediate feedback
- **Interactive map updates** synchronized with AI responses
- **Conversation context** maintained across tool calls
- **Error handling** for robust user experience
- **Responsive design** works on desktop and mobile

### User Experience
- **Natural language interface** - no need to learn commands
- **Visual feedback** with loading indicators and animations
- **Example queries** to help users get started
- **Real-time map updates** showing search results instantly

## Example Interactions

Here are some queries you can try:

**Place Search:**
- "Find coffee shops in Seattle"
- "Show me restaurants near Times Square"
- "Where can I find gas stations in downtown Chicago?"

**Directions:**
- "Get directions from Central Park to Brooklyn Bridge"
- "How far is it from London to Manchester by car?"
- "Walking directions from my hotel to the Louvre"

**Geocoding:**
- "What's the exact location of the White House?"
- "Show me where Stanford University is located"
- "Find the coordinates of Tokyo Tower"

## Advanced Customization

### Adding New Tools

To add a new tool, follow these steps:

1. **Define the function:**
```python
def weather_lookup(city: str) -> Dict[str, Any]:
    # Implementation using a weather API
    return {"status": "success", "weather": data}
```

2. **Add tool definition:**
```python
{
    "type": "function",
    "function": {
        "name": "weather_lookup",
        "description": "Get current weather for a city",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"}
            },
            "required": ["city"]
        }
    }
}
```

3. **Register the function:**
```python
available_functions["weather_lookup"] = weather_lookup
```

### Extending the Frontend

You can enhance the frontend by:
- **Adding new map layers** (satellite, terrain)
- **Implementing route optimization** for multiple stops
- **Adding voice input** using Web Speech API
- **Creating export functionality** for saving results
- **Integrating with other mapping services**

## Performance and Best Practices

### Rate Limiting Considerations
- **Nominatim**: 1 request per second for development
- **Production**: Consider running your own Nominatim instance
- **Caching**: Store frequently used geocoding results

### Error Handling
- **Network failures**: Graceful degradation with retry logic
- **Invalid locations**: Clear error messages to users
- **Tool failures**: Fallback to text-only responses
- **Rate limits**: Queue requests and inform users

### Security Considerations
- **Input validation**: Sanitize all user inputs
- **CORS configuration**: Limit to specific domains in production
- **Rate limiting**: Implement request throttling
- **API monitoring**: Track usage and errors

## Troubleshooting Common Issues

### Backend Issues
- **"Model not found"**: Ensure Ollama is running and model is pulled
- **Tool calling not working**: Verify your model supports function calling
- **Nominatim errors**: Check rate limits and User-Agent header

### Frontend Issues
- **CORS errors**: Verify backend CORS configuration matches frontend URL
- **Map not loading**: Check browser console for tile loading errors
- **Markers not appearing**: Ensure coordinate data is properly formatted

### Integration Issues
- **Tools not being called**: Check tool descriptions and parameter definitions
- **Map not updating**: Verify the map data processing logic
- **Conversation context lost**: Ensure message history is properly maintained

## Conclusion

This tutorial demonstrates the power of combining modern AI models with tool calling capabilities. By using free OpenStreetMap APIs and open-source tools like Ollama, you can build sophisticated AI assistants without any API costs.

The architecture we've built is highly extensible - you can easily add new tools for weather, transit, reviews, or any other functionality your users need. The combination of natural language processing with real-world data makes for compelling user experiences that feel truly intelligent.

**Next Steps:**
- Experiment with different AI models and compare their tool calling abilities
- Add more sophisticated routing using OpenRouteService API
- Implement user authentication and conversation persistence
- Deploy to production with proper scaling and monitoring
- Explore other free APIs to extend functionality

The future of AI applications lies in their ability to interact with the real world through tools and APIs. This foundation gives you everything you need to build the next generation of intelligent, location-aware applications.