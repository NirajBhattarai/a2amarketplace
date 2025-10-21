# A2A Web Frontend

A Next.js frontend application that provides a web interface for interacting with A2A (Agent-to-Agent) backend services.

## Features

- 🤖 **Multi-Agent Support**: Interact with TellTimeAgent, GreetingAgent, and OrchestratorAgent
- 💬 **Real-time Chat Interface**: Clean, modern chat UI for agent conversations
- 🔄 **Session Management**: Maintain conversation context across messages
- ⚡ **Quick Actions**: Pre-defined buttons for common queries
- 📱 **Responsive Design**: Works on desktop and mobile devices

## Getting Started

### Prerequisites

- Node.js 18+ 
- A2A backend running (see `../a2abackend/README.md`)

### Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

### Configuration

The frontend connects to the A2A backend via the `/api/agent` route. By default, it expects the backend to be running on `http://localhost:10002`.

To change the backend URL, set the environment variable:
```bash
NEXT_PUBLIC_A2A_BACKEND_URL=http://your-backend-url:port
```

## Usage

1. **Start the A2A Backend**: Follow the instructions in `../a2abackend/README.md` to start the orchestrator agent
2. **Open the Frontend**: Navigate to `http://localhost:3000`
3. **Start Chatting**: Type messages like:
   - "What time is it?" (calls TellTimeAgent)
   - "Greet me" (calls GreetingAgent)
   - "Hello" (routed by OrchestratorAgent)

## Architecture

```
Frontend (Next.js) → API Route → A2A Backend → Agents
```

- **Frontend**: React components with Tailwind CSS
- **API Route**: `/api/agent` handles communication with A2A backend
- **A2A Backend**: OrchestratorAgent routes requests to appropriate agents
- **Agents**: TellTimeAgent, GreetingAgent handle specific tasks

## Project Structure

```
web/
├── src/
│   ├── app/
│   │   ├── api/agent/route.ts    # API endpoint for A2A communication
│   │   └── page.tsx              # Main page component
│   ├── components/
│   │   └── AgentChat.tsx        # Chat interface component
│   └── config/
│       └── agent.ts               # Agent configuration
├── package.json
└── README.md
```

## Development

- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS
- **TypeScript**: Full type safety
- **API**: RESTful API routes for backend communication