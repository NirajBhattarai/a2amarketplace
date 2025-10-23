#!/usr/bin/env python3
"""
Simulate IoT Carbon Sequestration Device Data
Publishes sensor data to MQTT broker for testing
"""

import json
import time
import random
import paho.mqtt.client as mqtt
from datetime import datetime

# MQTT Configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
TOPIC_PREFIX = "carbon_sequestration"

# Multiple companies simulation
COMPANIES = [
    {
        "name": "TechCorp",
        "device_id": "sim_device_001",
        "device_ip": "192.168.1.100",
        "device_mac": "AA:BB:CC:DD:EE:FF"
    },
    {
        "name": "GreenEnergy",
        "device_id": "sim_device_002", 
        "device_ip": "192.168.1.101",
        "device_mac": "BB:CC:DD:EE:FF:AA"
    },
    {
        "name": "EcoSolutions",
        "device_id": "sim_device_003",
        "device_ip": "192.168.1.102", 
        "device_mac": "CC:DD:EE:FF:AA:BB"
    }
]

# Sensor ranges
CO2_MIN = 300
CO2_MAX = 2000
HUMIDITY_MIN = 20
HUMIDITY_MAX = 80

def on_connect(client, userdata, flags, rc):
    """Callback for when the client connects to the broker"""
    if rc == 0:
        print("✅ Connected to MQTT broker")
    else:
        print(f"❌ Failed to connect to MQTT broker, return code {rc}")

def on_publish(client, userdata, mid):
    """Callback for when a message is published"""
    print(f"📤 Message {mid} published successfully")

def generate_sensor_data(company):
    """Generate realistic sensor data for a specific company"""
    co2 = random.randint(CO2_MIN, CO2_MAX)
    humidity = random.randint(HUMIDITY_MIN, HUMIDITY_MAX)
    
    # Calculate carbon credits and emissions
    carbon_credits = co2 * 0.5
    emissions = humidity * 0.2
    offset = carbon_credits >= emissions
    
    return {
        "ip": company["device_ip"],
        "mac": company["device_mac"],
        "avg_c": round(co2, 1),
        "max_c": co2,
        "min_c": co2,
        "avg_h": round(humidity, 1),
        "max_h": humidity,
        "min_h": humidity,
        "cr": round(carbon_credits, 1),
        "e": round(emissions, 1),
        "o": offset,
        "t": int(time.time() * 1000),
        "type": "sequester",
        "samples": 1
    }

def generate_alert_data(company):
    """Generate critical alert data for a specific company"""
    return {
        "ip": company["device_ip"],
        "mac": company["device_mac"],
        "alert_type": "HIGH_CO2",
        "message": "High CO2 levels detected - sequestration needed!",
        "co2": random.randint(1800, 2000),
        "credits": round(random.uniform(0.5, 2.0), 1),
        "t": int(time.time() * 1000),
        "type": "alert"
    }

def generate_heartbeat_data(company):
    """Generate heartbeat data for a specific company"""
    return {
        "ip": company["device_ip"],
        "mac": company["device_mac"],
        "status": "online",
        "uptime": int(time.time() * 1000),
        "rssi": random.randint(-80, -30),
        "t": int(time.time() * 1000),
        "type": "heartbeat"
    }

def main():
    """Main simulation loop"""
    print("🌱 Starting IoT Carbon Sequestration Device Simulation")
    print(f"📡 Connecting to MQTT broker: {MQTT_BROKER}:{MQTT_PORT}")
    
    # Create MQTT client
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_publish = on_publish
    
    try:
        # Connect to broker
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
        
        # Wait for connection
        time.sleep(2)
        
        print("🚀 Starting data simulation...")
        print(f"🏢 Simulating {len(COMPANIES)} companies: {', '.join([c['name'] for c in COMPANIES])}")
        print("📊 Publishing sensor data every 15 seconds")
        print("💓 Publishing heartbeat every 5 minutes")
        print("🚨 Publishing alerts when conditions are critical")
        print("Press Ctrl+C to stop")
        
        last_sensor_publish = 0
        last_heartbeat = 0
        last_alert = 0
        
        sensor_interval = 15  # seconds
        heartbeat_interval = 300  # 5 minutes
        alert_interval = 60  # 1 minute
        
        while True:
            current_time = time.time()
            
            # Publish sensor data for all companies
            if current_time - last_sensor_publish >= sensor_interval:
                for company in COMPANIES:
                    sensor_data = generate_sensor_data(company)
                    topic = f"{TOPIC_PREFIX}/{company['name']}/sensor_data"
                    client.publish(topic, json.dumps(sensor_data))
                    print(f"📊 [{company['name']}] Published sensor data: CO2={sensor_data['avg_c']}, Humidity={sensor_data['avg_h']}, Credits={sensor_data['cr']}")
                last_sensor_publish = current_time
            
            # Publish heartbeat for all companies
            if current_time - last_heartbeat >= heartbeat_interval:
                for company in COMPANIES:
                    heartbeat_data = generate_heartbeat_data(company)
                    topic = f"{TOPIC_PREFIX}/{company['name']}/heartbeat"
                    client.publish(topic, json.dumps(heartbeat_data))
                    print(f"💓 [{company['name']}] Published heartbeat: Status={heartbeat_data['status']}, RSSI={heartbeat_data['rssi']}")
                last_heartbeat = current_time
            
            # Publish alerts occasionally for random companies
            if current_time - last_alert >= alert_interval and random.random() < 0.3:  # 30% chance
                company = random.choice(COMPANIES)
                alert_data = generate_alert_data(company)
                topic = f"{TOPIC_PREFIX}/{company['name']}/alerts"
                client.publish(topic, json.dumps(alert_data))
                print(f"🚨 [{company['name']}] Published alert: {alert_data['alert_type']} - {alert_data['message']}")
                last_alert = current_time
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping simulation...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.loop_stop()
        client.disconnect()
        print("✅ Simulation stopped")

if __name__ == "__main__":
    main()
