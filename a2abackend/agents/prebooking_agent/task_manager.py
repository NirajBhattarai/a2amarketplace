"""
Task Manager for Prebooking Agent
Handles JSON-RPC requests for carbon credit prebooking functionality
"""

import logging
from server.task_manager import InMemoryTaskManager
from models.request import SendTaskRequest, SendTaskResponse
from models.task import Message, Task, TextPart, TaskStatus, TaskState
from .agent import PrebookingAgent

logger = logging.getLogger(__name__)

class PrebookingTaskManager(InMemoryTaskManager):
    """
    Task Manager for Prebooking Agent
    Handles A2A JSON-RPC requests for carbon credit prebooking
    """
    
    def __init__(self, iot_agent_url: str = "http://localhost:10006", payment_agent_url: str = "http://localhost:10005"):
        super().__init__()
        self.prebooking_agent = PrebookingAgent(
            payment_agent_url=payment_agent_url,
            iot_agent_url=iot_agent_url
        )
        logger.info("🔮 PrebookingTaskManager initialized")

    def _get_user_query(self, request: SendTaskRequest) -> str:
        """
        Get the user's text input from the request object.
        
        Args:
            request: A SendTaskRequest object
            
        Returns:
            str: The actual text the user asked
        """
        return request.params.message.parts[0].text

    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        """
        Handle incoming prebooking tasks
        
        Args:
            request: SendTaskRequest containing the task
            
        Returns:
            SendTaskResponse with the result
        """
        logger.info(f"🔮 Processing prebooking task: {request.params.id}")
        
        try:
            # Step 1: Save the task using the base class helper
            task = await self.upsert_task(request.params)
            
            # Step 2: Get what the user asked
            query = self._get_user_query(request)
            
            # Step 3: Process the request through the agent
            result_text = await self.prebooking_agent.invoke(query, request.params.sessionId)
            
            # Step 4: Turn the agent's response into a Message object
            agent_message = Message(
                role="agent",
                parts=[TextPart(text=result_text)]
            )
            
            # Step 5: Update the task state and add the message to history
            async with self.lock:
                task.status = TaskStatus(state=TaskState.COMPLETED)
                task.history.append(agent_message)
            
            logger.info(f"✅ Prebooking task {request.params.id} completed successfully")
            
            # Step 6: Return a structured response back to the A2A client
            return SendTaskResponse(id=request.id, result=task)
            
        except Exception as e:
            logger.error(f"❌ Error processing prebooking task {request.params.id}: {e}")
            
            # Handle Gemini API errors
            if "503" in str(e) or "overloaded" in str(e).lower():
                error_message = self.prebooking_agent._handle_gemini_error(e)
            else:
                error_message = f"An error occurred while processing your prebooking request: {str(e)}"
            
            # Create error message
            agent_message = Message(
                role="agent",
                parts=[TextPart(text=error_message)]
            )
            
            # Update task with error
            async with self.lock:
                task.status = TaskStatus(state=TaskState.COMPLETED)
                task.history.append(agent_message)
            
            return SendTaskResponse(id=request.id, result=task)
