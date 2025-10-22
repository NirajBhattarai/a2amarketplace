import { NextResponse } from 'next/server';

const A2A_BACKEND_URL = process.env.A2A_BACKEND_URL || 'http://localhost:10002';

export async function GET() {
  try {
    // Try to connect to the A2A backend
    const response = await fetch(`${A2A_BACKEND_URL}/.well-known/agent.json`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (response.ok) {
      const agentInfo = await response.json();
      return NextResponse.json({
        status: 'healthy',
        backend: A2A_BACKEND_URL,
        agent: agentInfo,
        timestamp: new Date().toISOString()
      });
    } else {
      return NextResponse.json({
        status: 'unhealthy',
        backend: A2A_BACKEND_URL,
        error: `Backend responded with ${response.status}`,
        timestamp: new Date().toISOString()
      });
    }
  } catch (error) {
    return NextResponse.json({
      status: 'unhealthy',
      backend: A2A_BACKEND_URL,
      error: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString()
    });
  }
}
