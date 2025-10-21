# A2A Marketplace

A complete Agent-to-Agent (A2A) marketplace implementation with Python backend and Next.js frontend.

## Architecture

This project implements a complete app→client→server architecture:

- **App Layer**: Next.js web interface for user interactions
- **Client Layer**: TypeScript A2AClient service for JSON-RPC communication
- **Server Layer**: Python A2A agents handling task processing

## Features

- 🤖 **Multi-Agent Support**: TellTimeAgent, GreetingAgent, OrchestratorAgent
- 💬 **Real-time Chat**: Web interface for agent communication
- 📊 **Server Monitoring**: Live status monitoring of agents
- ⚙️ **Agent Management**: Discovery and configuration of agents
- 🔄 **Session Management**: Proper session handling with unique IDs

## Project Structure

```
marketplacewithpython/
├── a2abackend/          # Python A2A backend
│   ├── agents/          # Individual agent implementations
│   ├── client/          # A2A client library
│   ├── server/          # A2A server implementation
│   └── models/          # Data models and schemas
├── web/                 # Next.js frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── services/    # A2A client services
│   │   └── app/         # Next.js app router
└── README.md
```

## Quick Start

### Backend (Python)

1. Navigate to the backend directory:
   ```bash
   cd a2abackend
   ```

2. Install dependencies:
   ```bash
   pip install -e .
   ```

3. Start the agents:
   ```bash
   # Terminal 1 - TellTimeAgent
   python -m agents.tell_time_agent

   # Terminal 2 - GreetingAgent  
   python -m agents.greeting_agent

   # Terminal 3 - OrchestratorAgent
   python -m agents.host_agent
   ```

### Frontend (Next.js)

1. Navigate to the web directory:
   ```bash
   cd web
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## Usage

1. **Start the Python agents** (TellTimeAgent, GreetingAgent, etc.)
2. **Run the web app** - `npm run dev` in the `/web` directory
3. **Start chatting** - Messages are sent exactly like the Python CLI

The web interface works identically to running `python cmd.py` from the terminal, but with a beautiful UI and real-time monitoring capabilities!

## API Endpoints

- `POST /api/agent` - Send messages to A2A agents
- `GET /.well-known/agent.json` - Agent discovery endpoint

## Development

### Backend Development

The Python backend uses:
- **Starlette** for web framework
- **Pydantic** for data validation
- **JSON-RPC 2.0** for agent communication

### Frontend Development

The Next.js frontend uses:
- **React** for UI components
- **TypeScript** for type safety
- **Tailwind CSS** for styling

## License

MIT License