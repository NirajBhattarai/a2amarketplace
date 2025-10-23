# =============================================================================
# agents/iot_carbon_agent/task_manager.py
# =============================================================================
# 🎯 Purpose:
# TaskManager for IoT Carbon Agent that handles A2A JSON-RPC requests
# for real-time IoT carbon sequestration monitoring and prediction.
# =============================================================================

import logging
from typing import Optional
from google.adk.server.task_manager import InMemoryTaskManager
from google.adk.models.request import SendTaskRequest, SendTaskResponse
from google.adk.models.task import Message, TextPart, TaskStatus, TaskState
from .agent import IoTCarbonAgent

# Create a module-level logger
logger = logging.getLogger(__name__)


class IoTCarbonTaskManager(InMemoryTaskManager):
    """
    🌱 TaskManager for IoT Carbon Agent that handles A2A JSON-RPC requests
    for real-time IoT carbon sequestration monitoring and prediction.
    """

    def __init__(self, agent: IoTCarbonAgent):
        """
        🏗️ Constructor: initialize with IoT carbon agent
        """
        super().__init__()       # Initialize base in-memory storage
        self.agent = agent       # Store our IoT carbon agent logic

    def _get_user_text(self, request: SendTaskRequest) -> str:
        """
        Helper: extract the user's raw input text from the request object.
        """
        return request.params.message.parts[0].text

    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        """
        Handle a new IoT carbon sequestration task:

        1. Store the incoming user message in memory (or update existing task)
        2. Extract the user's text for processing
        3. Call IoTCarbonAgent.invoke() to process the IoT carbon request
        4. Wrap that response string in a Message/TextPart
        5. Update the Task status to COMPLETED and append the reply
        6. Return a SendTaskResponse containing the updated Task

        Args:
            request (SendTaskRequest): The JSON-RPC request with TaskSendParams

        Returns:
            SendTaskResponse: A JSON-RPC response with the completed Task
        """
        # Log receipt of a new task along with its ID
        logger.info(f"IoTCarbonTaskManager received task {request.params.id}")

        # Step 1: Save or update the task in memory.
        # upsert_task() will create a new Task if it doesn't exist,
        # or append the incoming user message to existing history.
        task = await self.upsert_task(request.params)

        # Step 2: Extract the actual text the user sent
        user_text = self._get_user_text(request)

        # Step 3: Call the IoTCarbonAgent to process the IoT carbon request.
        # Since IoTCarbonAgent.invoke() is an async function,
        # await it to get the returned string.
        iot_carbon_response = await self.agent.invoke(
            user_text,
            request.params.sessionId
        )

        # Step 4: Wrap the response string in a TextPart, then in a Message
        reply_message = Message(
            role="agent",               # Mark this as an "agent" response
            parts=[TextPart(text=iot_carbon_response)]  # The agent's reply text
        )

        # Step 5: Update the task status to COMPLETED and append our reply
        # Use the lock to avoid race conditions with other coroutines.
        async with self.lock:
            # Mark the task as done
            task.status = TaskStatus(state=TaskState.COMPLETED)
            # Add the agent's reply to the task's history
            task.history.append(reply_message)

        # Step 6: Return a SendTaskResponse, containing the JSON-RPC id
        # (mirroring the request.id) and the updated Task model.
        return SendTaskResponse(id=request.id, result=task)
