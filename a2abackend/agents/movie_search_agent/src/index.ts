import express from "express";
import { v4 as uuidv4 } from 'uuid';
import dotenv from 'dotenv';
import { searchMovies, searchPeople, getMovieDetails, getPersonDetails } from "./tools.js";

// Load environment variables
dotenv.config();

// Agent Card definition
const movieSearchAgentCard = {
  name: "Movie Search Agent",
  description: "A movie search agent that can find movies, actors, and provide recommendations using a hardcoded movie database",
  version: "1.0.0",
  protocolVersion: "1.0.0",
  capabilities: [
    "movie_search",
    "actor_search", 
    "movie_recommendations",
    "movie_details"
  ],
  endpoints: {
    tasks: "/"
  }
};

// 4. Create Express app with A2A-compatible endpoints
const expressApp = express();

// Middleware
expressApp.use(express.json());

// A2A-compatible JSON-RPC endpoint
expressApp.post('/', async (req, res) => {
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

    // Generate response based on user input
    let response = "I can help you find movies! Here are some great action movies: The Matrix, John Wick, Mad Max: Fury Road, Mission: Impossible - Fallout, Fast & Furious 7.";

    if (userMessage.toLowerCase().includes("action movies")) {
      response = "I can help you find movies! Here are some great action movies: The Matrix, John Wick, Mad Max: Fury Road, Mission: Impossible - Fallout, Fast & Furious 7.";
    } else if (userMessage.toLowerCase().includes("comedy")) {
      response = "Looking for comedies? Try: Superbad, The Hangover, Bridesmaids, Anchorman, Dumb and Dumber.";
    } else if (userMessage.toLowerCase().includes("sci-fi")) {
      response = "Sci-fi recommendations: Blade Runner 2049, Arrival, Interstellar, Dune, Ex Machina.";
    } else if (userMessage.toLowerCase().includes("actor")) {
      response = "I can search for actors, but for now, I'll give you a general movie list.";
    } else if (userMessage.toLowerCase().includes("recommend")) {
      response = "Based on your preferences, I recommend: The Matrix, Inception, Blade Runner 2049, Interstellar, and Mad Max: Fury Road.";
    }

    // Create a proper Task object response that matches the orchestrator's expectations
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
expressApp.get('/.well-known/agent-card.json', (req, res) => {
  res.json(movieSearchAgentCard);
});

// 5. Start the server
const PORT = process.env.PORT || 10006;
expressApp.listen(PORT, () => {
  console.log(`[MovieSearchAgent] Server started on http://localhost:${PORT}`);
  console.log(`[MovieSearchAgent] Agent Card: http://localhost:${PORT}/.well-known/agent-card.json`);
  console.log('[MovieSearchAgent] Press Ctrl+C to stop the server');
});