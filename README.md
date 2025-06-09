# Maps LLM Tool Calling API 🗺️🤖

A FastAPI-based application that combines Large Language Models with OpenStreetMap data to provide intelligent location-based services. This project demonstrates LLM tool calling capabilities for maps and navigation without requiring paid API keys.

## Features

- 🧠 **LLM Integration**: Uses Ollama for local LLM inference with tool calling
- 🗺️ **Free Maps Data**: Leverages OpenStreetMap via Nominatim API (no API keys required)
- 🔍 **Place Search**: Find restaurants, hotels, gas stations, and other points of interest
- 🧭 **Directions**: Get basic routing information between locations
- 📍 **Geocoding**: Convert addresses to coordinates and vice versa
- 🌐 **REST API**: Clean FastAPI interface with automatic documentation
- 📊 **Detailed Logging**: Comprehensive logging for debugging and monitoring

## Architecture

```
User Query → FastAPI → Ollama LLM → Tool Selection → OpenStreetMap APIs → Response
```

The system uses function calling to let the LLM decide when to use mapping tools based on user queries.

## Prerequisites

- Python 3.8+
- [Ollama](https://ollama.ai/) installed and running
- Qwen2.5:14b model (or modify `OLLAMA_MODEL` in code)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/prayanks/tool-calling-google-maps-tutorial.git
   cd tool-calling-google-maps-tutorial
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install fastapi uvicorn ollama requests pydantic
   ```

4. **Install and setup Ollama**
   ```bash
   # Install Ollama (visit https://ollama.ai for platform-specific instructions)
   # Pull the required model
   ollama pull qwen2.5:14b
   ```

## Usage

1. **Start the API server**
   ```bash
   python main.py
   ```
   The server will start on `http://localhost:8000`

2. **Check health status**
   ```bash
   curl http://localhost:8000/health
   ```

3. **Make a chat request**
   ```bash
   curl -X POST "http://localhost:8000/chat" \
        -H "Content-Type: application/json" \
        -d '{
          "message": "Find pizza restaurants in New York City",
          "conversation_history": []
        }'
   ```

## API Endpoints

### POST `/chat`
Main chat endpoint that processes natural language queries.

**Request Body:**
```json
{
  "message": "Find coffee shops near Central Park",
  "conversation_history": [
    {"role": "user", "content": "Previous message"},
    {"role": "assistant", "content": "Previous response"}
  ]
}
```

**Response:**
```json
{
  "response": "I found several coffee shops near Central Park...",
  "tool_calls": [
    {
      "function": "search_places",
      "arguments": {"query": "coffee shops", "location": "Central Park NYC"},
      "result": {"status": "success", "places": [...]}
    }
  ],
  "map_data": {
    "status": "success",
    "places": [...]
  }
}
```

### GET `/health`
Health check endpoint showing service status.

### GET `/`
Basic status endpoint.

## Available Tools

The LLM can automatically choose from these tools based on user queries:

### 1. `search_places`
- **Purpose**: Find places like restaurants, hotels, attractions
- **Parameters**: 
  - `query` (required): What to search for
  - `location` (optional): Where to search

### 2. `get_directions`
- **Purpose**: Get basic directions and distance between locations
- **Parameters**:
  - `origin` (required): Starting location
  - `destination` (required): End location
  - `mode` (optional): "driving", "walking", or "bicycling"

### 3. `geocode_address`
- **Purpose**: Convert addresses to coordinates
- **Parameters**:
  - `address` (required): Address to geocode

## Example Queries

The LLM can handle natural language queries like:

- "Find Italian restaurants in Rome"
- "How far is it from Paris to London?"
- "What's the address of the Eiffel Tower?"
- "Show me gas stations near Times Square"
- "Get directions from my hotel to the airport"

## Configuration

Key configuration options in `main.py`:

```python
OLLAMA_MODEL = "qwen2.5:14b"  # Change model here
CORS_ORIGINS = ["http://localhost:5173"]  # Add your frontend URL
```

## Data Sources

- **OpenStreetMap**: Free, open-source map data
- **Nominatim**: Free geocoding service (no API key required)
- **Local LLM**: Ollama provides privacy-focused local inference

## Logging

The application creates detailed logs in:
- Console output (DEBUG level)
- `app.log` file

## Limitations

- Basic routing calculations (no turn-by-turn directions)
- Rate limits apply to OpenStreetMap services
- Requires local Ollama installation
- Internet connection needed for map data

## Development

### Project Structure
```
├── main.py              # Main FastAPI application
├── app.log             # Application logs
├── README.md           # This file
└── requirements.txt    # Python dependencies (create with pip freeze)
```

### Adding New Tools

1. Define the function in `main.py`
2. Add to `tools` array with proper schema
3. Add to `available_functions` dictionary
4. The LLM will automatically learn to use it!

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Your chosen license]

## Troubleshooting

### Common Issues

**Ollama Connection Failed**
- Ensure Ollama is running: `ollama serve`
- Check model is available: `ollama list`
- Verify model name matches `OLLAMA_MODEL`

**OpenStreetMap API Errors**
- Check internet connection
- Verify User-Agent header is set
- Respect rate limits (1 request/second recommended)

**Tool Calling Not Working**
- Ensure your Ollama model supports function calling
- Check tool definitions are properly formatted
- Review logs for parsing errors

## Related Projects

- [Ollama](https://ollama.ai/) - Local LLM inference
- [OpenStreetMap](https://www.openstreetmap.org/) - Open map data
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework

---

Built with ❤️ using free and open-source technologies