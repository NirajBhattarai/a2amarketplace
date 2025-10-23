# =============================================================================
# agents/iot_carbon_agent/agent.py
# =============================================================================
# 🎯 Purpose:
# IoT Carbon Sequestration Agent that listens to MQTT from IoT devices,
# predicts carbon credit generation in real-time, and helps companies prepare
# for carbon credit needs without any database storage.
# =============================================================================

import logging
import asyncio
import json
import paho.mqtt.client as mqtt
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import deque
import threading
import time

from dotenv import load_dotenv

load_dotenv()

# Google ADK imports
from google.adk.agents.llm_agent import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.genai import types
from google.adk.tools.function_tool import FunctionTool

# Create a module-level logger
logger = logging.getLogger(__name__)


class IoTCarbonAgent:
    """
    🌱 IoT Carbon Sequestration Agent that:
    - Listens to MQTT from IoT devices in real-time
    - Predicts carbon credit generation without database storage
    - Helps companies prepare for carbon credit needs
    - Provides real-time analysis and forecasting
    """

    # Declare which content types this agent accepts by default
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self, mqtt_broker: str = "localhost", mqtt_port: int = 1883):
        """
        🏗️ Constructor: build the internal LLM agent, runner, and MQTT listener.
        """
        # MQTT configuration
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.mqtt_client = None
        self.mqtt_connected = False
        
        # Real-time data storage (in-memory only, no database)
        self.device_data = {}  # device_mac -> latest data
        self.recent_readings = deque(maxlen=100)  # Keep last 100 readings
        self.prediction_cache = {}  # Cache for predictions
        
        # MQTT topics
        self.sensor_topic = "carbon_credit/sensor_data"
        self.commands_topic = "carbon_credit/commands"
        
        # Build the LLM with its tools and system instruction
        self.agent = self._build_agent()

        # A fixed user_id to group all IoT carbon calls into one session
        self.user_id = "iot_carbon_user"

        # Runner wires together: agent logic, sessions, memory, artifacts
        self.runner = Runner(
            app_name=self.agent.name,
            agent=self.agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )

        # Start MQTT listening in background
        self._start_mqtt_listener()

    def _build_agent(self) -> LlmAgent:
        """
        🔧 Build the Gemini-based LlmAgent with IoT carbon tools and instructions.
        """
        # System instruction for IoT carbon sequestration
        system_instruction = """
        You are an IoT Carbon Sequestration Agent. You listen to real-time MQTT data 
        from IoT devices that measure CO2 and humidity levels for carbon sequestration.
        
        Your capabilities:
        - Listen to real-time MQTT data from IoT devices
        - Predict carbon credit generation based on current sensor data
        - Help companies prepare for carbon credit needs
        - Provide real-time analysis without database storage
        - Forecast carbon credit generation for planning purposes
        
        Available tools:
        - get_live_sensor_data(): Get current sensor data from all IoT devices
        - predict_carbon_credits(): Predict carbon credit generation
        - get_device_status(): Get status of all IoT devices
        - analyze_sequestration_trends(): Analyze carbon sequestration trends
        - get_company_preparation_advice(): Get advice for companies preparing for carbon credits
        
        Focus on real-time analysis and prediction to help companies prepare for 
        their carbon credit needs based on actual IoT device performance.
        """

        # Build tools for IoT carbon sequestration
        tools = [
            FunctionTool(self.get_live_sensor_data),
            FunctionTool(self.predict_carbon_credits),
            FunctionTool(self.get_device_status),
            FunctionTool(self.analyze_sequestration_trends),
            FunctionTool(self.get_company_preparation_advice),
        ]

        return LlmAgent(
            model="gemini-2.5-flash",
            name="iot_carbon_agent",
            description="Real-time IoT carbon sequestration monitoring and prediction",
            instruction=system_instruction,
            tools=tools,
        )

    def _start_mqtt_listener(self):
        """
        🚀 Start MQTT listener in background thread
        """
        try:
            self.mqtt_client = mqtt.Client()
            self.mqtt_client.on_connect = self._on_mqtt_connect
            self.mqtt_client.on_message = self._on_mqtt_message
            self.mqtt_client.on_disconnect = self._on_mqtt_disconnect
            
            # Connect to MQTT broker
            self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, 60)
            self.mqtt_client.loop_start()
            
            logger.info(f"🌱 IoT Carbon Agent started MQTT listener on {self.mqtt_broker}:{self.mqtt_port}")
            
        except Exception as e:
            logger.error(f"❌ Failed to start MQTT listener: {e}")

    def _on_mqtt_connect(self, client, userdata, flags, rc):
        """Callback for MQTT connection"""
        if rc == 0:
            logger.info("✅ Connected to MQTT broker")
            self.mqtt_connected = True
            # Subscribe to sensor data topic
            client.subscribe(self.sensor_topic)
            client.subscribe(self.commands_topic)
            logger.info(f"📡 Subscribed to topics: {self.sensor_topic}, {self.commands_topic}")
        else:
            logger.error(f"❌ MQTT connection failed with code {rc}")
            self.mqtt_connected = False

    def _on_mqtt_message(self, client, userdata, msg):
        """Callback for MQTT messages"""
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode('utf-8'))
            
            logger.info(f"📨 Received MQTT message on {topic}")
            
            if topic == self.sensor_topic:
                self._process_sensor_data(payload)
                
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to decode MQTT message: {e}")
        except Exception as e:
            logger.error(f"❌ Error processing MQTT message: {e}")

    def _on_mqtt_disconnect(self, client, userdata, rc):
        """Callback for MQTT disconnection"""
        logger.warning("⚠️ MQTT disconnected")
        self.mqtt_connected = False

    def _process_sensor_data(self, data: Dict[str, Any]):
        """
        Process IoT sensor data and update in-memory storage
        """
        try:
            # Extract device information
            device_mac = data.get('mac', 'unknown')
            device_ip = data.get('ip', 'unknown')
            
            # Extract sensor readings
            avg_co2 = float(data.get('avg_c', 0))
            avg_humidity = float(data.get('avg_h', 0))
            carbon_credits = float(data.get('cr', 0))
            emissions = float(data.get('e', 0))
            offset = data.get('o', 'false').lower() == 'true'
            timestamp = data.get('t', int(time.time() * 1000))
            samples = int(data.get('samples', 1))
            
            # Convert timestamp to datetime
            sensor_time = datetime.fromtimestamp(timestamp / 1000)
            
            # Store device data (in-memory only)
            self.device_data[device_mac] = {
                "device_ip": device_ip,
                "device_mac": device_mac,
                "avg_co2": avg_co2,
                "avg_humidity": avg_humidity,
                "carbon_credits": carbon_credits,
                "emissions": emissions,
                "offset": offset,
                "sensor_time": sensor_time,
                "samples": samples,
                "last_update": datetime.now()
            }
            
            # Store in recent readings queue
            self.recent_readings.append({
                "device_mac": device_mac,
                "device_ip": device_ip,
                "avg_co2": avg_co2,
                "avg_humidity": avg_humidity,
                "carbon_credits": carbon_credits,
                "emissions": emissions,
                "offset": offset,
                "sensor_time": sensor_time,
                "samples": samples
            })
            
            # Clear prediction cache when new data arrives
            self.prediction_cache.clear()
            
            logger.info(f"🌱 Updated data for device {device_mac}: {carbon_credits} credits")
            
        except Exception as e:
            logger.error(f"❌ Error processing sensor data: {e}")

    async def get_live_sensor_data(self) -> Dict[str, Any]:
        """
        📊 Get current live sensor data from all IoT devices
        """
        try:
            if not self.device_data:
                return {
                    "status": "no_data",
                    "message": "No IoT devices currently sending data",
                    "mqtt_connected": self.mqtt_connected
                }
            
            # Calculate totals
            total_credits = sum(device["carbon_credits"] for device in self.device_data.values())
            total_emissions = sum(device["emissions"] for device in self.device_data.values())
            active_devices = len(self.device_data)
            
            # Get device details
            devices = []
            for device_mac, data in self.device_data.items():
                devices.append({
                    "device_mac": device_mac,
                    "device_ip": data["device_ip"],
                    "carbon_credits": data["carbon_credits"],
                    "emissions": data["emissions"],
                    "offset": data["offset"],
                    "avg_co2": data["avg_co2"],
                    "avg_humidity": data["avg_humidity"],
                    "last_update": data["last_update"].isoformat(),
                    "sensor_time": data["sensor_time"].isoformat()
                })
            
            return {
                "status": "success",
                "mqtt_connected": self.mqtt_connected,
                "summary": {
                    "active_devices": active_devices,
                    "total_credits": round(total_credits, 2),
                    "total_emissions": round(total_emissions, 2),
                    "net_sequestration": round(total_credits - total_emissions, 2),
                    "overall_offset": total_credits >= total_emissions
                },
                "devices": devices,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting live sensor data: {e}")
            return {"error": f"Failed to get live sensor data: {str(e)}"}

    async def predict_carbon_credits(self, hours: int = 24) -> Dict[str, Any]:
        """
        🔮 Predict carbon credit generation for the next N hours
        """
        try:
            if not self.device_data:
                return {
                    "error": "No IoT devices data available for prediction",
                    "mqtt_connected": self.mqtt_connected
                }
            
            # Calculate current generation rate
            current_credits = sum(device["carbon_credits"] for device in self.device_data.values())
            current_emissions = sum(device["emissions"] for device in self.device_data.values())
            
            # Estimate hourly generation rate
            # Assuming data comes every 15 seconds, calculate rate per hour
            readings_per_hour = 240  # 15 seconds * 4 * 60 minutes
            hourly_credits = current_credits * readings_per_hour
            hourly_emissions = current_emissions * readings_per_hour
            
            # Predict for requested hours
            predicted_credits = hourly_credits * hours
            predicted_emissions = hourly_emissions * hours
            net_sequestration = predicted_credits - predicted_emissions
            
            # Calculate confidence based on data freshness
            now = datetime.now()
            max_age = max((now - device["last_update"]).total_seconds() for device in self.device_data.values())
            confidence = max(0, 1 - (max_age / 3600))  # Confidence decreases with data age
            
            # Generate hourly breakdown
            hourly_breakdown = []
            for hour in range(1, hours + 1):
                hourly_breakdown.append({
                    "hour": hour,
                    "predicted_credits": round(hourly_credits, 2),
                    "predicted_emissions": round(hourly_emissions, 2),
                    "net_sequestration": round(hourly_credits - hourly_emissions, 2)
                })
            
            return {
                "prediction_period": f"{hours} hours",
                "current_data": {
                    "active_devices": len(self.device_data),
                    "current_credits": round(current_credits, 2),
                    "current_emissions": round(current_emissions, 2)
                },
                "predictions": {
                    "total_credits": round(predicted_credits, 2),
                    "total_emissions": round(predicted_emissions, 2),
                    "net_sequestration": round(net_sequestration, 2),
                    "hourly_rate": round(hourly_credits, 2)
                },
                "confidence": {
                    "level": round(confidence, 2),
                    "data_freshness": f"{max_age:.1f} seconds ago",
                    "reliability": "high" if confidence > 0.8 else "medium" if confidence > 0.5 else "low"
                },
                "hourly_breakdown": hourly_breakdown,
                "recommendations": [
                    f"Expected to generate {round(predicted_credits, 0)} credits in {hours} hours",
                    f"Net carbon sequestration: {round(net_sequestration, 0)} credits",
                    "Monitor device performance for accuracy" if confidence < 0.8 else "High confidence prediction"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error predicting carbon credits: {e}")
            return {"error": f"Failed to predict carbon credits: {str(e)}"}

    async def get_device_status(self) -> Dict[str, Any]:
        """
        📱 Get status of all IoT devices
        """
        try:
            if not self.device_data:
                return {
                    "status": "no_devices",
                    "message": "No IoT devices currently active",
                    "mqtt_connected": self.mqtt_connected
                }
            
            devices = []
            now = datetime.now()
            
            for device_mac, data in self.device_data.items():
                # Calculate device status
                age_seconds = (now - data["last_update"]).total_seconds()
                if age_seconds < 60:
                    status = "active"
                elif age_seconds < 300:  # 5 minutes
                    status = "stale"
                else:
                    status = "inactive"
                
                devices.append({
                    "device_mac": device_mac,
                    "device_ip": data["device_ip"],
                    "status": status,
                    "last_update": data["last_update"].isoformat(),
                    "age_seconds": round(age_seconds, 1),
                    "carbon_credits": data["carbon_credits"],
                    "emissions": data["emissions"],
                    "offset": data["offset"],
                    "avg_co2": data["avg_co2"],
                    "avg_humidity": data["avg_humidity"]
                })
            
            # Calculate overall status
            active_count = sum(1 for device in devices if device["status"] == "active")
            total_count = len(devices)
            
            return {
                "overall_status": {
                    "total_devices": total_count,
                    "active_devices": active_count,
                    "stale_devices": sum(1 for device in devices if device["status"] == "stale"),
                    "inactive_devices": sum(1 for device in devices if device["status"] == "inactive"),
                    "mqtt_connected": self.mqtt_connected
                },
                "devices": devices,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting device status: {e}")
            return {"error": f"Failed to get device status: {str(e)}"}

    async def analyze_sequestration_trends(self) -> Dict[str, Any]:
        """
        📈 Analyze carbon sequestration trends from recent data
        """
        try:
            if len(self.recent_readings) < 2:
                return {
                    "error": "Insufficient data for trend analysis",
                    "readings_count": len(self.recent_readings)
                }
            
            # Convert deque to list for analysis
            readings = list(self.recent_readings)
            
            # Calculate trends
            credits_trend = []
            emissions_trend = []
            co2_trend = []
            humidity_trend = []
            
            for reading in readings:
                credits_trend.append(reading["carbon_credits"])
                emissions_trend.append(reading["emissions"])
                co2_trend.append(reading["avg_co2"])
                humidity_trend.append(reading["avg_humidity"])
            
            # Calculate averages and trends
            avg_credits = sum(credits_trend) / len(credits_trend)
            avg_emissions = sum(emissions_trend) / len(emissions_trend)
            avg_co2 = sum(co2_trend) / len(co2_trend)
            avg_humidity = sum(humidity_trend) / len(humidity_trend)
            
            # Simple trend analysis (increasing/decreasing)
            if len(credits_trend) >= 5:
                recent_credits = credits_trend[-5:]
                older_credits = credits_trend[-10:-5] if len(credits_trend) >= 10 else credits_trend[:-5]
                
                recent_avg = sum(recent_credits) / len(recent_credits)
                older_avg = sum(older_credits) / len(older_credits) if older_credits else recent_avg
                
                if recent_avg > older_avg * 1.1:
                    trend_direction = "increasing"
                elif recent_avg < older_avg * 0.9:
                    trend_direction = "decreasing"
                else:
                    trend_direction = "stable"
            else:
                trend_direction = "insufficient_data"
            
            return {
                "analysis_period": {
                    "readings_analyzed": len(readings),
                    "time_span": f"{(readings[-1]['sensor_time'] - readings[0]['sensor_time']).total_seconds():.0f} seconds"
                },
                "trends": {
                    "credits_trend": trend_direction,
                    "avg_credits_per_reading": round(avg_credits, 2),
                    "avg_emissions_per_reading": round(avg_emissions, 2),
                    "net_sequestration": round(avg_credits - avg_emissions, 2)
                },
                "environmental_factors": {
                    "avg_co2": round(avg_co2, 1),
                    "avg_humidity": round(avg_humidity, 1),
                    "co2_range": f"{min(co2_trend):.0f} - {max(co2_trend):.0f}",
                    "humidity_range": f"{min(humidity_trend):.0f} - {max(humidity_trend):.0f}"
                },
                "recommendations": [
                    f"Carbon sequestration trend: {trend_direction}",
                    f"Average net sequestration: {round(avg_credits - avg_emissions, 1)} credits per reading",
                    "Monitor CO2 levels for optimal sequestration" if avg_co2 < 400 else "CO2 levels are good for sequestration",
                    "Consider device maintenance" if trend_direction == "decreasing" else "Devices performing well"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sequestration trends: {e}")
            return {"error": f"Failed to analyze trends: {str(e)}"}

    async def get_company_preparation_advice(self) -> Dict[str, Any]:
        """
        💼 Get advice for companies preparing for carbon credit needs
        """
        try:
            # Get current data
            live_data = await self.get_live_sensor_data()
            if "error" in live_data:
                return live_data
            
            # Get predictions
            prediction = await self.predict_carbon_credits(24)  # 24-hour prediction
            if "error" in prediction:
                return prediction
            
            # Calculate preparation advice
            current_credits = live_data["summary"]["total_credits"]
            predicted_credits = prediction["predictions"]["total_credits"]
            net_sequestration = prediction["predictions"]["net_sequestration"]
            
            # Determine preparation level
            if net_sequestration > 0:
                if net_sequestration > predicted_credits * 0.5:
                    preparation_level = "excellent"
                    advice = "Strong carbon sequestration - consider selling excess credits"
                else:
                    preparation_level = "good"
                    advice = "Good carbon sequestration - monitor for optimization opportunities"
            else:
                preparation_level = "needs_attention"
                advice = "Insufficient carbon sequestration - consider additional measures"
            
            # Generate specific recommendations
            recommendations = []
            
            if net_sequestration > 0:
                recommendations.extend([
                    f"✅ Carbon sequestration is working: {round(net_sequestration, 1)} credits net",
                    f"📈 Expected 24h generation: {round(predicted_credits, 0)} credits",
                    "💡 Consider carbon credit marketplace for excess credits",
                    "🔍 Monitor device performance for optimization"
                ])
            else:
                recommendations.extend([
                    "⚠️ Carbon sequestration needs improvement",
                    "🔧 Check device calibration and maintenance",
                    "🌱 Consider additional sequestration measures",
                    "📊 Monitor CO2 and humidity levels for optimization"
                ])
            
            return {
                "preparation_assessment": {
                    "level": preparation_level,
                    "net_sequestration": round(net_sequestration, 2),
                    "current_credits": round(current_credits, 2),
                    "predicted_credits_24h": round(predicted_credits, 2)
                },
                "advice": advice,
                "recommendations": recommendations,
                "next_steps": [
                    "Monitor real-time performance",
                    "Track carbon credit generation trends",
                    "Prepare for carbon credit marketplace participation",
                    "Optimize device performance based on data"
                ],
                "marketplace_readiness": {
                    "ready_for_selling": net_sequestration > predicted_credits * 0.3,
                    "ready_for_buying": net_sequestration < predicted_credits * 0.1,
                    "monitoring_needed": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting company preparation advice: {e}")
            return {"error": f"Failed to get preparation advice: {str(e)}"}

    async def invoke(self, query: str, session_id: str) -> str:
        """
        🔄 Public: send a user query through the IoT carbon agent pipeline
        """
        # 1) Try to fetch an existing session
        session = await self.runner.session_service.get_session(
            app_name=self.agent.name,
            user_id=self.user_id,
            session_id=session_id,
        )

        # 2) If not found, create a new session with empty state
        if session is None:
            session = await self.runner.session_service.create_session(
                app_name=self.agent.name,
                user_id=self.user_id,
                session_id=session_id,
                state={},
            )

        # 3) Wrap the user's text in a Gemini Content object
        content = types.Content(
            role="user",
            parts=[types.Part.from_text(text=query)]
        )

        # 🚀 Run the agent using the Runner and collect the last event
        last_event = None
        async for event in self.runner.run_async(
            user_id=self.user_id,
            session_id=session.id,
            new_message=content
        ):
            last_event = event

        # 🧹 Fallback: return empty string if something went wrong
        if not last_event or not last_event.content or not last_event.content.parts:
            return ""

        # 📤 Extract and join all text responses into one string
        return "\n".join([p.text for p in last_event.content.parts if p.text])
