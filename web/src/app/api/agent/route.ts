import { NextRequest, NextResponse } from 'next/server';

interface ConversationPart {
  type: string;
  text: string;
}

interface ConversationItem {
  role: string;
  parts?: ConversationPart[];
}

const A2A_BACKEND_URL = process.env.A2A_BACKEND_URL || 'http://localhost:10002';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { message, sessionId, agentUrl } = body;

    // Use the provided agent URL or default
    const targetUrl = agentUrl || A2A_BACKEND_URL;
    
    console.log('🎯 Target URL:', targetUrl);
    console.log('📝 Message:', message);
    console.log('🆔 Original Session ID:', sessionId);

    // Generate a unique task ID (similar to Python's uuid4().hex)
    const taskId = Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
    const requestId = Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
    
    // Always generate a unique session ID to prevent conflicts
    const uniqueSessionId = Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
    
    // Create the JSON-RPC payload exactly like the Python app does
    const payload = {
      jsonrpc: "2.0",
      id: requestId,
      method: "tasks/send",
      params: {
        id: taskId,
        sessionId: uniqueSessionId,
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

    console.log('🆔 Unique Session ID:', uniqueSessionId);
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
      console.error(`❌ A2A backend error: ${response.status} ${response.statusText}`);
      
      // Return a fallback response if backend is not available
      return NextResponse.json({
        success: true,
        response: `Backend not available (${response.status}). Please ensure the A2A backend is running on ${targetUrl}`,
        data: { error: `Backend responded with ${response.status}` }
      });
    }

    const result = await response.json();
    console.log('📥 Received response:', JSON.stringify(result, null, 2));
    
    // Extract the actual response text from the A2A result
    let responseText = 'No response received';
    let conversationHistory = [];
    
    if (result.result && result.result.history) {
      // Extract the latest agent response from history
      const history = result.result.history;
      const agentMessages = history.filter((item: ConversationItem) => item.role === 'agent');
      
      if (agentMessages.length > 0) {
        const latestAgentMessage = agentMessages[agentMessages.length - 1];
        if (latestAgentMessage.parts) {
          responseText = latestAgentMessage.parts
            .filter((part: ConversationPart) => part.type === 'text')
            .map((part: ConversationPart) => part.text)
            .join(' ');
        }
      }
      
      // Store the full conversation history
      conversationHistory = history;
    } else if (result.result && result.result.result) {
      // If it's a task result, extract the content
      const taskResult = result.result.result;
      if (taskResult.content && taskResult.content.parts) {
        responseText = taskResult.content.parts
          .filter((part: ConversationPart) => part.type === 'text')
          .map((part: ConversationPart) => part.text)
          .join(' ');
      }
    } else if (result.result && result.result.content) {
      // If it's direct content
      if (result.result.content.parts) {
        responseText = result.result.content.parts
          .filter((part: ConversationPart) => part.type === 'text')
          .map((part: ConversationPart) => part.text)
          .join(' ');
      }
    } else if (result.error) {
      responseText = `Error: ${result.error.message || 'Unknown error'}`;
    }
    
    return NextResponse.json({
      success: true,
      response: responseText,
      history: conversationHistory,
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
