from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json
from typing import List, Dict, Any, Optional
import ollama
import urllib.parse
import logging
import traceback
import sys

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)

# Create logger for this module
logger = logging.getLogger(__name__)

app = FastAPI(title="Maps LLM Tool Calling API - OpenStreetMap")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_MODEL = "qwen2.5:14b"

class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[Dict[str, str]]] = []

class ChatResponse(BaseModel):
    response: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    map_data: Optional[Dict[str, Any]] = None

# OpenStreetMap API functions (all free, no API key needed!)
def search_places(query: str, location: str = "") -> Dict[str, Any]:
    """Search for places using Nominatim (OpenStreetMap)"""
    try:
        logger.info(f"Searching places: query='{query}', location='{location}'")
        
        # Combine query and location
        search_query = f"{query} {location}".strip()
        logger.debug(f"Combined search query: '{search_query}'")
        
        # Use Nominatim API (free OpenStreetMap geocoding)
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": search_query,
            "format": "json",
            "limit": 5,
            "addressdetails": 1,
            "extratags": 1
        }
        
        headers = {
            "User-Agent": "MapsAI/1.0"  # Required by Nominatim
        }
        
        logger.debug(f"Making request to Nominatim: {url} with params: {params}")
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()  # Raise exception for bad status codes
        
        data = response.json()
        logger.debug(f"Nominatim response: {len(data)} results")
        
        places = []
        for item in data:
            place = {
                "name": item.get("display_name", "").split(",")[0],
                "address": item.get("display_name"),
                "coordinates": {
                    "lat": float(item.get("lat", 0)),
                    "lng": float(item.get("lon", 0))
                },
                "type": item.get("type", ""),
                "importance": item.get("importance", 0)
            }
            places.append(place)
            logger.debug(f"Processed place: {place['name']} at {place['coordinates']}")
        
        result = {"status": "success", "places": places}
        logger.info(f"Search completed successfully: {len(places)} places found")
        return result
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error in search_places: {str(e)}")
        return {"status": "error", "message": f"Network error: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error in search_places: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {"status": "error", "message": str(e)}

def get_directions(origin: str, destination: str, mode: str = "driving") -> Dict[str, Any]:
    """Get directions using OpenRouteService (free with registration)"""
    try:
        logger.info(f"Getting directions: {origin} -> {destination} ({mode})")
        
        # First geocode the addresses
        logger.debug("Geocoding origin address")
        origin_coords = geocode_address(origin)
        logger.debug("Geocoding destination address")
        dest_coords = geocode_address(destination)
        
        if origin_coords["status"] != "success" or dest_coords["status"] != "success":
            error_msg = "Could not find one or both locations"
            logger.warning(f"Geocoding failed: {error_msg}")
            return {"status": "error", "message": error_msg}
        
        # For simplicity, we'll return basic info without detailed routing
        # You can integrate with OpenRouteService API for detailed routing
        origin_coord = origin_coords["coordinates"]
        dest_coord = dest_coords["coordinates"]
        
        logger.debug(f"Origin coords: {origin_coord}")
        logger.debug(f"Destination coords: {dest_coord}")
        
        # Calculate rough distance (this is simplified)
        import math
        
        def haversine_distance(lat1, lon1, lat2, lon2):
            R = 6371  # Earth's radius in kilometers
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = (math.sin(dlat/2)**2 + 
                 math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
                 math.sin(dlon/2)**2)
            c = 2 * math.asin(math.sqrt(a))
            return R * c
        
        distance_km = haversine_distance(
            origin_coord["lat"], origin_coord["lng"],
            dest_coord["lat"], dest_coord["lng"]
        )
        
        logger.debug(f"Calculated distance: {distance_km} km")
        
        # Rough time estimates based on mode
        time_estimates = {
            "driving": distance_km / 50,  # ~50 km/h average
            "walking": distance_km / 5,   # ~5 km/h
            "bicycling": distance_km / 15, # ~15 km/h
        }
        
        estimated_hours = time_estimates.get(mode, distance_km / 50)
        logger.debug(f"Estimated time: {estimated_hours} hours")
        
        result = {
            "status": "success",
            "distance": f"{distance_km:.1f} km",
            "duration": f"{estimated_hours*60:.0f} minutes" if estimated_hours < 1 else f"{estimated_hours:.1f} hours",
            "start_address": origin,
            "end_address": destination,
            "coordinates": {
                "origin": origin_coord,
                "destination": dest_coord
            },
            "mode": mode
        }
        
        logger.info(f"Directions calculated successfully: {result['distance']}, {result['duration']}")
        return result
    
    except Exception as e:
        logger.error(f"Error in get_directions: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {"status": "error", "message": str(e)}

def geocode_address(address: str) -> Dict[str, Any]:
    """Convert address to coordinates using Nominatim"""
    try:
        logger.info(f"Geocoding address: '{address}'")
        
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": address,
            "format": "json",
            "limit": 1,
            "addressdetails": 1
        }
        
        headers = {
            "User-Agent": "MapsAI/1.0"
        }
        
        logger.debug(f"Making geocoding request to: {url}")
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        logger.debug(f"Geocoding response: {len(data)} results")
        
        if data:
            result_data = data[0]
            result = {
                "status": "success",
                "address": result_data.get("display_name"),
                "coordinates": {
                    "lat": float(result_data.get("lat", 0)),
                    "lng": float(result_data.get("lon", 0))
                }
            }
            logger.info(f"Geocoding successful: {result['coordinates']}")
            return result
        else:
            logger.warning(f"No geocoding results found for: {address}")
            return {"status": "error", "message": "Address not found"}
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error in geocode_address: {str(e)}")
        return {"status": "error", "message": f"Network error: {str(e)}"}
    except Exception as e:
        logger.error(f"Error in geocode_address: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {"status": "error", "message": str(e)}

def find_nearby_places(lat: float, lng: float, place_type: str, radius_km: float = 5) -> Dict[str, Any]:
    """Find places near coordinates using Overpass API"""
    try:
        logger.info(f"Finding nearby places: {place_type} near {lat},{lng} within {radius_km}km")
        
        # Overpass API query for nearby places
        # This is more complex but very powerful - simplified version here
        
        # For simplicity, we'll use a basic search around coordinates
        search_query = f"{place_type} near {lat},{lng}"
        return search_places(search_query)
    
    except Exception as e:
        logger.error(f"Error in find_nearby_places: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {"status": "error", "message": str(e)}

# Tool definitions
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_places",
            "description": "Search for places like restaurants, hotels, attractions, etc. using OpenStreetMap data",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "What to search for (e.g., 'pizza restaurants', 'gas stations', 'hotels')"
                    },
                    "location": {
                        "type": "string",
                        "description": "Location to search in (city, address, etc.)"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_directions",
            "description": "Get basic directions and distance between two locations",
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {
                        "type": "string",
                        "description": "Starting location (address or place name)"
                    },
                    "destination": {
                        "type": "string",
                        "description": "Destination location (address or place name)"
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["driving", "walking", "bicycling"],
                        "description": "Transportation mode"
                    }
                },
                "required": ["origin", "destination"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "geocode_address",
            "description": "Convert an address to coordinates (latitude/longitude)",
            "parameters": {
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "Address to convert to coordinates"
                    }
                },
                "required": ["address"]
            }
        }
    }
]

available_functions = {
    "search_places": search_places,
    "get_directions": get_directions,
    "geocode_address": geocode_address
}

def check_ollama_connection():
    """Helper function to safely check Ollama connection and models"""
    try:
        logger.debug("Checking Ollama connection...")
        models_response = ollama.list()
        logger.debug(f"Ollama models response: {models_response}")
        
        # Handle different possible response structures
        if isinstance(models_response, dict):
            if 'models' in models_response:
                models = models_response['models']
            else:
                models = models_response
        else:
            models = models_response
        
        # Extract model names safely
        model_names = []
        for model in models:
            if isinstance(model, dict):
                # Try different possible keys for model name
                name = model.get('name') or model.get('model') or model.get('id') or str(model)
                model_names.append(name)
            else:
                model_names.append(str(model))
        
        logger.debug(f"Available Ollama models: {model_names}")
        return True, model_names
        
    except Exception as e:
        logger.error(f"Error checking Ollama connection: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False, str(e)

@app.post("/chat", response_model=ChatResponse)
async def chat_with_llm(request: ChatRequest):
    try:
        logger.info(f"Received chat request: '{request.message[:100]}...' with {len(request.conversation_history)} history messages")
        
        messages = []
        
        # Build conversation history
        for i, msg in enumerate(request.conversation_history):
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
            logger.debug(f"History message {i}: {msg['role']} - {msg['content'][:50]}...")
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": request.message
        })
        
        logger.debug(f"Sending {len(messages)} messages to Ollama model: {OLLAMA_MODEL}")
        logger.debug(f"Available tools: {[tool['function']['name'] for tool in tools]}")
        
        # Check if Ollama is accessible
        ollama_ok, ollama_info = check_ollama_connection()
        if not ollama_ok:
            logger.error(f"Cannot connect to Ollama: {ollama_info}")
            raise HTTPException(status_code=503, detail=f"Ollama service unavailable: {ollama_info}")
        
        # Make the initial chat request to Ollama
        logger.debug("Making initial chat request to Ollama...")
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=messages,
            tools=tools
        )
        
        logger.debug(f"Ollama response received: {type(response)}")
        logger.debug(f"Response type: {type(response)}")
        
        assistant_message = response.message
        logger.debug(f"Assistant message: {assistant_message}")
        
        tool_calls_made = []
        map_data = None
        
        # Check if the model wants to use tools
        if assistant_message.get('tool_calls'):
            logger.info(f"Model requested {len(assistant_message['tool_calls'])} tool calls")
            
            for i, tool_call in enumerate(assistant_message['tool_calls']):
                logger.debug(f"Processing tool call {i+1}: {tool_call}")
                
                function_name = tool_call['function']['name']
                arguments = tool_call['function']['arguments']
                
                logger.info(f"Executing tool: {function_name} with args: {arguments}")
                
                if function_name in available_functions:
                    try:
                        function_result = available_functions[function_name](**arguments)
                        logger.debug(f"Tool {function_name} result: {function_result}")
                        
                        tool_calls_made.append({
                            "function": function_name,
                            "arguments": arguments,
                            "result": function_result
                        })
                        
                        # Store map data from successful tool calls
                        if function_result.get("status") == "success":
                            map_data = function_result
                            logger.debug("Map data updated from tool result")
                        
                    except Exception as e:
                        logger.error(f"Error executing tool {function_name}: {str(e)}")
                        logger.error(f"Traceback: {traceback.format_exc()}")
                        
                        tool_calls_made.append({
                            "function": function_name,
                            "arguments": arguments,
                            "result": {"status": "error", "message": str(e)}
                        })
                else:
                    logger.error(f"Unknown function requested: {function_name}")
                    tool_calls_made.append({
                        "function": function_name,
                        "arguments": arguments,
                        "result": {"status": "error", "message": f"Unknown function: {function_name}"}
                    })
            
            # Add assistant message and tool results back to conversation
            messages.append(assistant_message)
            
            for i, tool_call in enumerate(assistant_message['tool_calls']):
                tool_result_message = {
                    "role": "tool",
                    "content": json.dumps(tool_calls_made[i]["result"])
                }
                messages.append(tool_result_message)
                logger.debug(f"Added tool result message: {tool_result_message}")
            
            # Get final response from Ollama with tool results
            logger.debug("Getting final response from Ollama with tool results...")
            final_response = ollama.chat(
                model=OLLAMA_MODEL,
                messages=messages
            )
            
            response_text = final_response.message.content
            logger.info(f"Final response generated: {response_text[:100]}...")
        else:
            # No tools needed, use direct response
            response_text = getattr(assistant_message, 'content', '')
            logger.info(f"Direct response (no tools): {response_text[:100]}...")
        
        result = ChatResponse(
            response=response_text,
            tool_calls=tool_calls_made if tool_calls_made else None,
            map_data=map_data
        )
        
        logger.info(f"Chat request completed successfully. Tools used: {len(tool_calls_made)}, Map data: {map_data is not None}")
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "OpenStreetMap LLM Tool Calling API is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint with detailed status"""
    try:
        # Check Ollama connection
        ollama_ok, ollama_info = check_ollama_connection()
        if ollama_ok:
            # Check if the specific model is available
            if isinstance(ollama_info, list) and any(OLLAMA_MODEL in str(model) for model in ollama_info):
                ollama_status = "ready"
            else:
                ollama_status = f"model {OLLAMA_MODEL} not found in: {ollama_info}"
        else:
            ollama_status = f"error: {ollama_info}"
        
        # Check external API
        nominatim_status = "unknown"
        try:
            response = requests.get("https://nominatim.openstreetmap.org/search?q=test&format=json&limit=1", 
                                  headers={"User-Agent": "MapsAI/1.0"}, timeout=5)
            nominatim_status = "ready" if response.status_code == 200 else f"error: {response.status_code}"
        except Exception as e:
            nominatim_status = f"error: {str(e)}"
        
        return {
            "status": "running",
            "ollama": ollama_status,
            "nominatim": nominatim_status,
            "model": OLLAMA_MODEL,
            "available_models": ollama_info if ollama_ok else None
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting Maps AI API with model: {OLLAMA_MODEL}")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")