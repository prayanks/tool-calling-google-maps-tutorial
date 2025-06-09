# Maps AI Assistant with Ollama Tool Calling (OpenStreetMap)

This example demonstrates how to implement tool calling with LLMs using Ollama, **OpenStreetMap APIs** (completely free!), Python FastAPI backend, and Svelte frontend.

## Prerequisites

1. **Ollama installed** with Qwen model:
   ```bash
   # Install Ollama
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Pull the Qwen model (adjust name as needed)
   ollama pull qwen2.5:14b
   ```

2. **No API Keys Required!** 🎉
   - This implementation uses **OpenStreetMap** and **Nominatim** APIs
   - All APIs used are completely **free** and require **no registration**
   - No Google Maps API key needed!

3. **Python 3.8+** and **Node.js 16+**

## Backend Setup

1. **Install Python dependencies**:
   ```bash
   pip install fastapi uvicorn ollama requests python-multipart
   ```

2. **No environment variables needed** - all APIs are free!

3. **Run the backend**:
   ```bash
   python main.py
   ```
   The API will be available at `http://localhost:8000`

## Frontend Setup

1. **Create a new Svelte project**:
   ```bash
   # Using the new Svelte CLI
   npx sv create maps-ai-frontend
   cd maps-ai-frontend
   npm install
   ```

2. **Replace the contents of `src/routes/+page.svelte`** with the provided Svelte code. Note that `npx sv create` creates a **SvelteKit** project, so the main page is at `src/routes/+page.svelte` (not `src/App.svelte`). Simply copy and paste the entire App.svelte code - it works perfectly in SvelteKit with no modifications needed! The component includes:
   - Modern Svelte 5 syntax and reactivity
   - Enhanced UI with better styling and animations
   - Improved error handling and loading states
   - **OpenStreetMap integration** (instead of Google Maps)
   - Responsive design for mobile and desktop

3. **No API key configuration needed!** The frontend will work with OpenStreetMap's free tile servers.

4. **Run the frontend**:
   ```bash
   npm run dev
   ```
   The app will be available at `http://localhost:5173`

## How It Works

### 1. Tool Calling Flow

1. **User sends a message** through the Svelte frontend
2. **Backend receives the message** and passes it to Ollama with tool definitions
3. **Ollama determines if tools are needed** and makes function calls
4. **Backend executes the tools** (OpenStreetMap API calls)
5. **Results are passed back to Ollama** for a natural language response
6. **Frontend displays the response** and updates the map

### 2. Available Tools (OpenStreetMap-based)

- **`search_places`**: Find restaurants, hotels, gas stations, etc. using **Nominatim** (OpenStreetMap geocoding)
- **`get_directions`**: Get basic directions and distance calculations between locations
- **`geocode_address`**: Convert addresses to coordinates using **Nominatim**

### 3. APIs Used (All Free!)

- **Nominatim API**: OpenStreetMap's geocoding service
  - Place search and address geocoding
  - No API key required
  - Rate limited but generous for development
- **OpenStreetMap Tiles**: For map display
  - Free map tiles
  - No registration required
- **Distance Calculations**: Done server-side using haversine formula

### 4. Example Queries

Try these example queries:

- "Find pizza restaurants near Times Square"
- "Get directions from Central Park to Brooklyn Bridge"
- "What's the address of the Statue of Liberty?"
- "Find coffee shops in Paris"
- "Show me the distance from London to Manchester"

## Key Features

### Backend Features:
- **FastAPI** for REST API with automatic OpenAPI docs
- **Ollama integration** with proper tool calling support
- **OpenStreetMap integration** with **no API costs**
- **CORS support** for cross-origin requests
- **Structured responses** with tool call metadata
- **Built-in distance calculations** using haversine formula

### Frontend Features (Updated):
- **Modern Svelte 5 architecture** with improved reactivity
- **Real-time chat interface** with enhanced typing indicators
- **Interactive OpenStreetMap** with custom markers and info windows
- **Responsive design** optimized for mobile and desktop  
- **Enhanced visual feedback** for loading states and errors
- **Auto-updating map** based on AI responses with smooth animations
- **Improved accessibility** with proper ARIA labels and keyboard navigation
- **No API key management** - works out of the box!

## Tool Calling Architecture

```
User Query → Svelte Frontend → FastAPI Backend → Ollama LLM
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

## Customization

### Adding New Tools

1. **Define the function** in the backend:
   ```python
   def new_tool_function(param1: str, param2: int) -> Dict[str, Any]:
       # Your implementation using free APIs
       return {"status": "success", "data": result}
   ```

2. **Add tool definition**:
   ```python
   {
       "type": "function",
       "function": {
           "name": "new_tool_function",
           "description": "Description of what this tool does",
           "parameters": {
               "type": "object",
               "properties": {
                   "param1": {"type": "string", "description": "Parameter description"},
                   "param2": {"type": "integer", "description": "Parameter description"}
               },
               "required": ["param1"]
           }
       }
   }
   ```

3. **Register the function**:
   ```python
   available_functions["new_tool_function"] = new_tool_function
   ```

### Extending with More Free APIs

- **OpenRouteService**: For detailed routing (free tier available)
- **Overpass API**: For complex OpenStreetMap queries
- **Weather APIs**: Many have free tiers
- **Public Transit APIs**: Many cities provide free APIs

### Extending the Frontend

- **Add new map features**: Drawing routes, custom markers, clustering
- **Implement voice input**: Using Web Speech API
- **Add export functionality**: Save conversations or map data
- **Create custom UI components**: For different types of results
- **Enhance accessibility**: Screen reader support, keyboard shortcuts

## Advantages of This Implementation

### Cost Benefits:
- **$0 API costs** - completely free to run
- **No rate limiting worries** for development
- **No credit card required** to get started
- **Scale without API bills**

### Technical Benefits:
- **OpenStreetMap data** is often more detailed than commercial alternatives
- **No vendor lock-in** - you control your data
- **Community-driven** updates and improvements
- **Privacy-friendly** - no tracking by commercial map providers

## Troubleshooting

### Common Issues:

1. **"Model not found"**: Ensure Ollama is running and the model is pulled
2. **CORS errors**: Check that the frontend URL matches the CORS configuration
3. **Nominatim errors**: Respect rate limits (1 request per second for development)
4. **Tool calling not working**: Ensure your Ollama model supports function calling
5. **Svelte CLI errors**: Use `npx sv create` instead of `npm create svelte`
6. **Map not loading**: Check browser console for OpenStreetMap tile loading errors

### Debug Commands:

```bash
# Check if Ollama is running
ollama list

# Test the backend directly
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Find restaurants near me"}'

# Test Nominatim directly
curl "https://nominatim.openstreetmap.org/search?q=pizza+new+york&format=json&limit=3"

# Check frontend console for errors
# Open browser dev tools → Console tab

# Verify Svelte version
npx sv --version
```

### Rate Limiting (Nominatim):
- **Development**: 1 request per second
- **Production**: Consider running your own Nominatim instance
- **Alternative**: Use commercial geocoding for high-volume applications

## Performance Tips

1. **Respect rate limits**: Add delays between API calls if needed
2. **Cache geocoding results**: Store coordinates for frequently used addresses
3. **Optimize map rendering**: Use marker clustering for many results
4. **Stream responses**: For better user experience with long responses
5. **Error boundaries**: Implement proper error handling throughout
6. **Code splitting**: Lazy load components for faster initial load

## What's New in This OpenStreetMap Version

### Key Differences from Google Maps Version:
- **No API keys required** - works immediately
- **Free forever** - no usage limits or billing
- **OpenStreetMap integration** instead of Google Maps
- **Nominatim geocoding** for address/place search
- **Built-in distance calculations** using haversine formula
- **Privacy-focused** - no tracking or data collection

### Setup Advantages:
- **Instant setup** - no account creation or API key management
- **No billing concerns** - perfect for learning and prototyping
- **Open source ecosystem** - community-supported tools and data
- **Global coverage** - works worldwide without regional restrictions

This example provides a solid foundation for building location-aware AI assistants with **zero API costs** and modern tool calling capabilities!