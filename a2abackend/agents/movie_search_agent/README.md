# Movie Search Agent

A TypeScript-based A2A (Agent-to-Agent) movie search agent that integrates with the orchestrator to provide intelligent movie and actor search capabilities using The Movie Database (TMDB).

## Features

- **Movie Search**: Search for movies by title, genre, year, director, or other criteria
- **Actor Search**: Find actors and their filmography
- **Detailed Information**: Get comprehensive details about specific movies or people
- **Recommendations**: Provide personalized movie recommendations
- **Rich Responses**: Include movie posters, ratings, release years, and more

## Prerequisites

- Node.js 18+ 
- npm or yarn
- TMDB API key
- Google Gemini API key

## Installation

1. Clone the repository and navigate to the movie-search-agent directory:
```bash
cd /Users/niraj/Desktop/marketplacewithpython/movie-search-agent
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp env.example .env
```

4. Edit `.env` file with your API keys:
```env
GEMINI_API_KEY=your_gemini_api_key_here
TMDB_API_KEY=your_tmdb_api_key_here
PORT=10006
```

## Getting API Keys

### TMDB API Key
1. Go to [TMDB API](https://www.themoviedb.org/settings/api)
2. Create an account and request an API key
3. Copy the API key to your `.env` file

### Google Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create a new API key
3. Copy the API key to your `.env` file

## Usage

### Development Mode
```bash
npm run dev
```

### Production Mode
```bash
npm run build
npm start
```

### A2A Agent Mode
```bash
npm run a2a:movie-agent
```

The agent will start on `http://localhost:10006` by default.

## Agent Capabilities

### Movie Search
- Find movies by title, genre, year, or other criteria
- Get detailed movie information including cast, crew, ratings, and plot
- Search for movies by director or studio

### Actor Search
- Find actors and their filmography
- Get detailed information about specific actors
- Search for actors by movie or TV show

### Recommendations
- Get personalized movie recommendations
- Find movies similar to ones you like
- Get recommendations by genre, year, or rating

## Integration with Orchestrator

This agent is designed to work with the A2A orchestrator. The orchestrator can delegate movie-related queries to this agent, which will:

1. Process the user's movie/actor search request
2. Use TMDB API to find relevant information
3. Provide rich, detailed responses with movie posters, ratings, and more
4. Return structured data that can be used by other agents

## API Endpoints

- `GET /.well-known/agent-card.json` - Agent card information
- `POST /` - Main A2A communication endpoint

## Example Queries

- "Find action movies from 2023"
- "Search for movies starring Tom Cruise"
- "What are the top rated sci-fi movies?"
- "Find romantic comedies from the 90s"
- "What movies has Leonardo DiCaprio been in?"
- "Recommend movies similar to Inception"

## Architecture

The agent is built using:
- **TypeScript** for type safety
- **A2A SDK** for agent-to-agent communication
- **Genkit** for AI prompt management
- **Google Gemini** for natural language processing
- **TMDB API** for movie and actor data
- **Express.js** for HTTP server

## Error Handling

The agent includes comprehensive error handling for:
- API rate limits
- Network connectivity issues
- Invalid movie/actor IDs
- Missing API keys
- Malformed requests

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the A2A marketplace system and follows the same licensing terms.
