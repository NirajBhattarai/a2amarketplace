import express from "express";
import { v4 as uuidv4 } from 'uuid';
import dotenv from 'dotenv';
import { searchMovies, searchPeople, getMovieDetails, getPersonDetails } from "./tools.js";

// Load environment variables
dotenv.config();

// Simple movie search agent without A2A SDK dependencies
const app = express();
app.use(express.json());

// Hardcoded movie data for testing
const HARDCODED_MOVIES = [
  {
    id: 1,
    title: "The Matrix",
    overview: "A computer hacker learns about the true nature of reality and his role in the war against its controllers.",
    release_date: "1999-03-30",
    vote_average: 8.7,
    genre_ids: [28, 878], // Action, Sci-Fi
    poster_path: "/f89U3ADr1oiB6s1GRAx8lxwemfX.jpg"
  },
  {
    id: 2,
    title: "John Wick",
    overview: "An ex-hit-man comes out of retirement to track down the gangsters that took everything from him.",
    release_date: "2014-10-24",
    vote_average: 7.4,
    genre_ids: [28, 53], // Action, Thriller
    poster_path: "/fZPSd91yGE9fCcCe6OoQr6E3Bev.jpg"
  },
  {
    id: 3,
    title: "Mad Max: Fury Road",
    overview: "In a post-apocalyptic wasteland, Max teams up with a mysterious woman to escape from a tyrannical warlord.",
    release_date: "2015-05-15",
    vote_average: 7.6,
    genre_ids: [28, 12, 878], // Action, Adventure, Sci-Fi
    poster_path: "/hA2ple9q4qnwxp3hKVNhroips2u.jpg"
  },
  {
    id: 4,
    title: "Mission: Impossible - Fallout",
    overview: "Ethan Hunt and his IMF team must stop a global catastrophe after a mission goes wrong.",
    release_date: "2018-07-27",
    vote_average: 7.4,
    genre_ids: [28, 53], // Action, Thriller
    poster_path: "/AkJQpZp9WoNdj7pLYSj1L0RcMMN.jpg"
  },
  {
    id: 5,
    title: "Fast & Furious 7",
    overview: "Deckard Shaw seeks revenge against Dominic Toretto and his family for his brother's death.",
    release_date: "2015-04-03",
    vote_average: 7.2,
    genre_ids: [28, 80], // Action, Crime
    poster_path: "/dCgm7efXDmiACGdDvzzGQF3A0Dq.jpg"
  }
];

// Simple movie search function
function searchMoviesSimple(query: string) {
  const filteredMovies = HARDCODED_MOVIES.filter(movie =>
    movie.title.toLowerCase().includes(query.toLowerCase()) ||
    movie.overview.toLowerCase().includes(query.toLowerCase())
  );
  
  return filteredMovies.length > 0 ? filteredMovies : HARDCODED_MOVIES;
}

// A2A-compatible JSON-RPC endpoint
app.post('/', async (req, res) => {
  try {
    const { jsonrpc, id, method, params } = req.body;
    
    if (jsonrpc !== '2.0' || method !== 'tasks/send') {
      return res.status(400).json({
        jsonrpc: '2.0',
        id,
        error: { code: -32601, message: 'Method not found' }
      });
    }
    
    const { id: taskId, sessionId, message } = params;
    const userMessage = message.parts[0].text;
    
    console.log(`[MovieSearchAgent] Processing: "${userMessage}"`);
    
    // Simple movie search logic
    let response = "I can help you find movies! ";
    
    if (userMessage.toLowerCase().includes('action')) {
      const actionMovies = searchMoviesSimple('action');
      response += `Here are some great action movies: ${actionMovies.map(m => m.title).join(', ')}.`;
    } else if (userMessage.toLowerCase().includes('sci-fi') || userMessage.toLowerCase().includes('science fiction')) {
      const sciFiMovies = HARDCODED_MOVIES.filter(m => m.genre_ids.includes(878));
      response += `Here are some sci-fi movies: ${sciFiMovies.map(m => m.title).join(', ')}.`;
    } else if (userMessage.toLowerCase().includes('recommend') || userMessage.toLowerCase().includes('suggest')) {
      response += `I recommend: The Matrix (8.7/10), John Wick (7.4/10), and Mad Max: Fury Road (7.6/10).`;
    } else {
      const movies = searchMoviesSimple(userMessage);
      response += `Here are some movies: ${movies.slice(0, 3).map(m => m.title).join(', ')}.`;
    }
    
    // Create a proper Task object response
    const taskResponse = {
      id: taskId,
      status: {
        state: "completed",
        timestamp: new Date().toISOString()
      },
      history: [
        {
          role: "user",
          parts: [{ type: "text", text: userMessage }]
        },
        {
          role: "agent", 
          parts: [{ type: "text", text: response }]
        }
      ]
    };

    res.json({
      jsonrpc: '2.0',
      id,
      result: taskResponse
    });
  } catch (error) {
    console.error('Error handling request:', error);
    res.status(500).json({
      jsonrpc: '2.0',
      id: req.body.id,
      error: { code: -32603, message: 'Internal error' }
    });
  }
});

// Agent card endpoint
app.get('/.well-known/agent-card.json', (req, res) => {
  res.json({
    name: "Movie Search Agent",
    description: "An intelligent movie search agent that can find movies, actors, and provide recommendations using hardcoded movie database.",
    url: "http://localhost:10006/",
    provider: {
      organization: "Marketplace with Python",
      url: "https://github.com/NirajBhattarai/a2amarketplace"
    },
    version: "1.0.0",
    protocolVersion: "1.0.0",
    capabilities: {
      streaming: true,
      pushNotifications: false,
      stateTransitionHistory: true
    },
    defaultInputModes: ["text"],
    defaultOutputModes: ["text", "task-status"],
    skills: [
      {
        id: "movie_search",
        name: "Movie Search",
        description: "Search for movies by title, genre, year, or other criteria",
        tags: ["movies", "search", "entertainment"],
        examples: [
          "Find action movies from 2023",
          "Search for movies starring Tom Cruise",
          "What are the top rated sci-fi movies?",
          "Find romantic comedies from the 90s",
          "Search for movies directed by Christopher Nolan"
        ],
        inputModes: ["text"],
        outputModes: ["text", "task-status"]
      },
      {
        id: "actor_search",
        name: "Actor Search",
        description: "Search for actors and their filmography",
        tags: ["actors", "people", "filmography"],
        examples: [
          "What movies has Leonardo DiCaprio been in?",
          "Find actors who starred in Marvel movies",
          "Search for actors born in the 80s",
          "What is the filmography of Meryl Streep?"
        ],
        inputModes: ["text"],
        outputModes: ["text", "task-status"]
      },
      {
        id: "movie_recommendations",
        name: "Movie Recommendations",
        description: "Get personalized movie recommendations",
        tags: ["recommendations", "movies", "suggestions"],
        examples: [
          "Recommend movies similar to Inception",
          "What are good family movies?",
          "Suggest horror movies for Halloween",
          "Find movies like The Matrix"
        ],
        inputModes: ["text"],
        outputModes: ["text", "task-status"]
      }
    ],
    supportsAuthenticatedExtendedCard: false
  });
});

// Start the server
const PORT = process.env.PORT || 10006;
app.listen(PORT, () => {
  console.log(`[MovieSearchAgent] Server started on http://localhost:${PORT}`);
  console.log(`[MovieSearchAgent] Agent Card: http://localhost:${PORT}/.well-known/agent-card.json`);
  console.log('[MovieSearchAgent] Press Ctrl+C to stop the server');
});
