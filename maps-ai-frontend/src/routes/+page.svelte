<!-- +page.svelte (SvelteKit version) -->
<script>
  import { onMount } from 'svelte';
  
  let messages = [];
  let userInput = '';
  let isLoading = false;
  let mapContainer;
  let map;
  let markers = [];
  
  onMount(() => {
    loadLeaflet();
  });
  
  async function loadLeaflet() {
    // Load Leaflet CSS
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
    document.head.appendChild(link);
    
    // Load Leaflet JS
    const script = document.createElement('script');
    script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
    script.onload = () => {
      initMap();
    };
    document.head.appendChild(script);
  }
  
  function initMap() {
    // Initialize map with San Francisco as default center
    map = L.map(mapContainer).setView([37.7749, -122.4194], 12);
    
    // Add OpenStreetMap tiles (completely free!)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 19
    }).addTo(map);
    
    // Optional: Add a different tile style (also free)
    // L.tileLayer('https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png', {
    //   attribution: '© OpenStreetMap contributors, Tiles courtesy of Humanitarian OpenStreetMap Team'
    // }).addTo(map);
  }
  
  function clearMarkers() {
    markers.forEach(marker => map.removeLayer(marker));
    markers = [];
  }
  
  function addMarkers(places) {
    clearMarkers();
    
    if (!places || places.length === 0) return;
    
    const group = new L.featureGroup();
    
    places.forEach((place, index) => {
      if (place.coordinates) {
        const marker = L.marker([place.coordinates.lat, place.coordinates.lng])
          .bindPopup(`
            <div class="popup-content">
              <h3>${place.name}</h3>
              <p>${place.address}</p>
              ${place.type ? `<p><strong>Type:</strong> ${place.type}</p>` : ''}
            </div>
          `);
        
        marker.addTo(map);
        markers.push(marker);
        group.addLayer(marker);
      }
    });
    
    if (group.getLayers().length > 0) {
      map.fitBounds(group.getBounds(), { padding: [20, 20] });
    }
  }
  
  function showDirections(directionsData) {
    clearMarkers();
    
    if (directionsData.coordinates) {
      const { origin, destination } = directionsData.coordinates;
      
      // Add start marker (green)
      const startMarker = L.marker([origin.lat, origin.lng], {
        icon: L.icon({
          iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
          shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
          iconSize: [25, 41],
          iconAnchor: [12, 41],
          popupAnchor: [1, -34],
          shadowSize: [41, 41]
        })
      }).bindPopup(`
        <div class="popup-content">
          <h3>Start</h3>
          <p>${directionsData.start_address}</p>
        </div>
      `);
      
      // Add end marker (red)
      const endMarker = L.marker([destination.lat, destination.lng], {
        icon: L.icon({
          iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
          shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
          iconSize: [25, 41],
          iconAnchor: [12, 41],
          popupAnchor: [1, -34],
          shadowSize: [41, 41]
        })
      }).bindPopup(`
        <div class="popup-content">
          <h3>Destination</h3>
          <p>${directionsData.end_address}</p>
          <p><strong>Distance:</strong> ${directionsData.distance}</p>
          <p><strong>Duration:</strong> ${directionsData.duration}</p>
        </div>
      `);
      
      startMarker.addTo(map);
      endMarker.addTo(map);
      markers.push(startMarker, endMarker);
      
      // Draw a simple line between points
      const polyline = L.polyline([
        [origin.lat, origin.lng],
        [destination.lat, destination.lng]
      ], {
        color: '#007bff',
        weight: 4,
        opacity: 0.7
      }).addTo(map);
      
      markers.push(polyline);
      
      // Fit map to show both markers
      const group = new L.featureGroup([startMarker, endMarker]);
      map.fitBounds(group.getBounds(), { padding: [20, 20] });
    }
  }
  
  function showSingleLocation(data) {
    clearMarkers();
    
    if (data.coordinates) {
      const marker = L.marker([data.coordinates.lat, data.coordinates.lng])
        .bindPopup(`
          <div class="popup-content">
            <h3>Location Found</h3>
            <p>${data.address}</p>
          </div>
        `);
      
      marker.addTo(map);
      markers.push(marker);
      
      map.setView([data.coordinates.lat, data.coordinates.lng], 15);
    }
  }
  
  async function sendMessage() {
    if (!userInput.trim() || isLoading) return;
    
    const userMessage = userInput.trim();
    userInput = '';
    
    messages = [...messages, { role: 'user', content: userMessage }];
    isLoading = true;
    
    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          conversation_history: messages.slice(0, -1)
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      messages = [...messages, { role: 'assistant', content: data.response }];
      
      // Handle map data
      if (data.map_data && data.map_data.status === 'success') {
        if (data.map_data.places) {
          addMarkers(data.map_data.places);
        } else if (data.map_data.coordinates && data.map_data.coordinates.origin) {
          // This is directions data
          showDirections(data.map_data);
        } else if (data.map_data.coordinates) {
          // This is single location data
          showSingleLocation(data.map_data);
        }
      }
      
      if (data.tool_calls) {
        console.log('Tool calls made:', data.tool_calls);
      }
      
    } catch (error) {
      console.error('Error:', error);
      messages = [...messages, { 
        role: 'assistant', 
        content: 'Sorry, there was an error processing your request.' 
      }];
    } finally {
      isLoading = false;
    }
  }
  
  function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  }
</script>

<svelte:head>
  <title>Maps AI Assistant - OpenStreetMap</title>
</svelte:head>

<main class="app">
  <div class="container">
    <h1>🗺️ Maps AI Assistant</h1>
    <p class="subtitle">Powered by OpenStreetMap - No API keys required!</p>
    
    <div class="content">
      <!-- Chat Section -->
      <div class="chat-section">
        <div class="chat-messages">
          {#each messages as message}
            <div class="message {message.role}">
              <div class="message-content">
                {@html message.content.replace(/\n/g, '<br>')}
              </div>
            </div>
          {/each}
          
          {#if isLoading}
            <div class="message assistant">
              <div class="message-content loading">
                <div class="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                Searching...
              </div>
            </div>
          {/if}
        </div>
        
        <div class="input-area">
          <textarea
            bind:value={userInput}
            on:keydown={handleKeyPress}
            placeholder="Try: 'Find coffee shops in Seattle' or 'Directions from Paris to London'"
            rows="3"
            disabled={isLoading}
          ></textarea>
          <button on:click={sendMessage} disabled={isLoading || !userInput.trim()}>
            Send
          </button>
        </div>
        
        <div class="example-queries">
          <p><strong>Try these examples:</strong></p>
          <button class="example-btn" on:click={() => userInput = 'Find restaurants in New York City'}>
            🍕 Find restaurants in NYC
          </button>
          <button class="example-btn" on:click={() => userInput = 'Get directions from London to Paris'}>
            🚗 London to Paris directions
          </button>
          <button class="example-btn" on:click={() => userInput = 'Where is the Eiffel Tower?'}>
            📍 Find Eiffel Tower
          </button>
        </div>
      </div>
      
      <!-- Map Section -->
      <div class="map-section">
        <div bind:this={mapContainer} class="map-container"></div>
        <div class="map-attribution">
          <small>Map data © <a href="https://openstreetmap.org" target="_blank">OpenStreetMap</a> contributors</small>
        </div>
      </div>
    </div>
  </div>
</main>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
  }
  
  .app {
    min-height: 100vh;
    padding: 20px;
  }
  
  .container {
    max-width: 1400px;
    margin: 0 auto;
  }
  
  h1 {
    text-align: center;
    color: white;
    margin-bottom: 10px;
    font-size: 2.5rem;
    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
  }
  
  .subtitle {
    text-align: center;
    color: rgba(255,255,255,0.9);
    margin-bottom: 30px;
    font-size: 1.1rem;
  }
  
  .content {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    height: calc(100vh - 180px);
  }
  
  .chat-section {
    display: flex;
    flex-direction: column;
    background: white;
    border-radius: 12px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(10px);
    overflow: hidden;
  }
  
  .chat-messages {
    flex: 1;
    padding: 20px;
    overflow-y: auto;
    max-height: calc(100vh - 350px);
  }
  
  .message {
    margin-bottom: 16px;
  }
  
  .message-content {
    padding: 12px 16px;
    border-radius: 18px;
    max-width: 80%;
    line-height: 1.4;
  }
  
  .message.user .message-content {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    margin-left: auto;
  }
  
  .message.assistant .message-content {
    background: #f8f9fa;
    color: #2c3e50;
    border: 1px solid #e9ecef;
  }
  
  .loading {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  .typing-indicator {
    display: flex;
    gap: 3px;
  }
  
  .typing-indicator span {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #667eea;
    animation: typing 1.4s infinite ease-in-out;
  }
  
  .typing-indicator span:nth-child(2) {
    animation-delay: 0.2s;
  }
  
  .typing-indicator span:nth-child(3) {
    animation-delay: 0.4s;
  }
  
  @keyframes typing {
    0%, 60%, 100% {
      transform: translateY(0);
    }
    30% {
      transform: translateY(-10px);
    }
  }
  
  .input-area {
    padding: 20px;
    border-top: 1px solid #e9ecef;
    display: flex;
    gap: 12px;
  }
  
  textarea {
    flex: 1;
    padding: 12px;
    border: 2px solid #e9ecef;
    border-radius: 8px;
    resize: none;
    font-family: inherit;
    font-size: 14px;
    transition: border-color 0.2s;
  }
  
  textarea:focus {
    outline: none;
    border-color: #667eea;
  }
  
  button {
    padding: 12px 24px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 500;
    transition: transform 0.2s;
  }
  
  button:hover:not(:disabled) {
    transform: translateY(-1px);
  }
  
  button:disabled {
    background: #6c757d;
    cursor: not-allowed;
    transform: none;
  }
  
  .example-queries {
    padding: 0 20px 20px;
    border-top: 1px solid #e9ecef;
  }
  
  .example-queries p {
    margin: 0 0 12px 0;
    font-size: 14px;
    color: #6c757d;
  }
  
  .example-btn {
    display: block;
    width: 100%;
    margin-bottom: 8px;
    padding: 8px 12px;
    background: #f8f9fa;
    color: #495057;
    border: 1px solid #dee2e6;
    border-radius: 6px;
    font-size: 13px;
    text-align: left;
    cursor: pointer;
    transition: background-color 0.2s;
  }
  
  .example-btn:hover {
    background: #e9ecef;
    transform: none;
  }
  
  .map-section {
    background: white;
    border-radius: 12px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    overflow: hidden;
    position: relative;
  }
  
  .map-container {
    width: 100%;
    height: calc(100% - 30px);
    min-height: 500px;
  }
  
  .map-attribution {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: rgba(255,255,255,0.9);
    padding: 5px 10px;
    text-align: center;
  }
  
  .map-attribution a {
    color: #667eea;
    text-decoration: none;
  }
  
  :global(.leaflet-popup-content) {
    font-family: inherit;
    margin: 8px 12px;
  }
  
  :global(.popup-content h3) {
    margin: 0 0 8px 0;
    color: #2c3e50;
    font-size: 16px;
  }
  
  :global(.popup-content p) {
    margin: 4px 0;
    color: #6c757d;
    font-size: 14px;
  }
  
  @media (max-width: 768px) {
    .content {
      grid-template-columns: 1fr;
      grid-template-rows: 1fr 400px;
    }
    
    h1 {
      font-size: 2rem;
    }
    
    .subtitle {
      font-size: 1rem;
    }
  }
</style>