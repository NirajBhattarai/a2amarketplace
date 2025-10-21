import { NextRequest, NextResponse } from 'next/server';

const A2A_BACKEND_URL = process.env.A2A_BACKEND_URL || 'http://localhost:10002';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { message, sessionId, agentUrl } = body;

    // Use the provided agent URL or default
    const targetUrl = agentUrl || A2A_BACKEND_URL;

    // Generate a unique task ID (similar to Python's uuid4().hex)
    const taskId = Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
    const requestId = Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
    
    // Create the JSON-RPC payload exactly like the Python app does
    const payload = {
      jsonrpc: "2.0",
      id: requestId,
      method: "tasks/send",
      params: {
        id: taskId,
        sessionId: sessionId || Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15),
        message: {
          role: "user",
          parts: [
            {
              type: "text",
              text: message
            }
          ]
        }
      }
    };

    console.log('📤 Sending JSON-RPC request to:', targetUrl);
    console.log('Payload:', JSON.stringify(payload, null, 2));

    // Send request to A2A backend
    const response = await fetch(`${targetUrl}/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(`A2A backend responded with status: ${response.status}`);
    }

    const result = await response.json();
    console.log('📥 Received response:', JSON.stringify(result, null, 2));
    
    return NextResponse.json({
      success: true,
      data: result
    });

  } catch (error) {
    console.error('Error calling A2A backend:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: error instanceof Error ? error.message : 'Unknown error' 
      },
      { status: 500 }
    );
  }
}
