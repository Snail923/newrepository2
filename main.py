from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import time
import logging
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Drone Control API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
start_time = time.time()
sensor_data = {
    'mpu9250': {
        'accelerometer': {'x': 0.0, 'y': 0.0, 'z': 0.0},
        'gyroscope': {'x': 0.0, 'y': 0.0, 'z': 0.0},
        'magnetometer': {'x': 0.0, 'y': 0.0, 'z': 0.0},
        'temperature': 0.0,
        'calibrated': False,
        'status': 'idle'
    },
    'barometer': {
        'pressure': 0.0,
        'temperature': 0.0,
        'altitude': 0.0,
        'sea_level_pressure': 1013.25,
        'calibrated': False,
        'status': 'idle'
    },
    'gps': {
        'latitude': 0.0,
        'longitude': 0.0,
        'altitude': 0.0,
        'speed': 0.0,
        'satellites': 0,
        'hdop': 0.0,
        'status': 'no_fix',
        'calibrated': False
    },
    'system': {
        'uptime': 0.0,
        'cpu_temp': 0.0,
        'memory_usage': 0.0,
        'disk_usage': 0.0,
        'status': 'idle',
        'last_update': datetime.utcnow().isoformat()
    }
}

# Pydantic models
class SensorData(BaseModel):
    accelerometer: Dict[str, float]
    gyroscope: Dict[str, float]
    temperature: float
    calibrated: bool
    status: str

class BarometerData(BaseModel):
    pressure: float
    temperature: float
    altitude: float
    sea_level_pressure: float
    calibrated: bool
    status: str

class GPSData(BaseModel):
    latitude: float
    longitude: float
    altitude: float
    speed: float
    satellites: int
    hdop: float
    status: str
    calibrated: bool

class SystemData(BaseModel):
    uptime: float
    cpu_temp: float
    memory_usage: float
    disk_usage: float
    status: str
    last_update: str

# Helper functions
def update_system_metrics():
    """Update system metrics (simulated for now)"""
    sensor_data['system'].update({
        'uptime': round(time.time() - start_time, 1),
        'cpu_temp': 45.0,  # Simulated CPU temperature
        'memory_usage': 30.5,  # Simulated memory usage
        'disk_usage': 15.2,  # Simulated disk usage
        'status': 'running',
        'last_update': datetime.utcnow().isoformat()
    })

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Drone Control API is running"}

@app.get("/api/sensors")
async def get_all_sensors():
    try:
        update_system_metrics()
        return {
            "sensors": sensor_data,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting all sensors: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sensors/mpu9250")
async def update_mpu9250(data: Dict[str, Any]):
    try:
        sensor_data['mpu9250'].update({
            'accelerometer': data.get('accelerometer', sensor_data['mpu9250']['accelerometer']),
            'gyroscope': data.get('gyroscope', sensor_data['mpu9250']['gyroscope']),
            'temperature': data.get('temperature', sensor_data['mpu9250']['temperature']),
            'calibrated': data.get('calibrated', sensor_data['mpu9250']['calibrated']),
            'status': data.get('status', sensor_data['mpu9250']['status'])
        })
        return {"status": "success", "message": "MPU9250 data updated"}
    except Exception as e:
        logger.error(f"Error updating MPU9250 data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/stm32")
async def receive_stm32_data(request: Request):
    """Receive and process data from STM32"""
    try:
        data = await request.body()
        data_str = data.decode('utf-8').strip()
        logger.info(f"Received STM32 data: {data_str}")
        
        # Parse the sensor data format: <SENSOR_DATA|MPU|accel_x|accel_y|accel_z|gyro_x|gyro_y|gyro_z|BMP|pressure|temperature|altitude>
        if data_str.startswith('<SENSOR_DATA|') and data_str.endswith('>'):
            parts = data_str[1:-1].split('|')
            
            if len(parts) >= 11 and parts[0] == 'SENSOR_DATA' and parts[1] == 'MPU' and parts[8] == 'BMP':
                try:
                    # Update MPU9250 data
                    sensor_data['mpu9250'].update({
                        'accelerometer': {
                            'x': float(parts[2]),
                            'y': float(parts[3]),
                            'z': float(parts[4])
                        },
                        'gyroscope': {
                            'x': float(parts[5]),
                            'y': float(parts[6]),
                            'z': float(parts[7])
                        },
                        'calibrated': True,
                        'status': 'active'
                    })
                    
                    # Update Barometer data
                    sensor_data['barometer'].update({
                        'pressure': float(parts[9]),
                        'temperature': float(parts[10]),
                        'altitude': float(parts[11]) if len(parts) > 11 else 0.0,
                        'calibrated': True,
                        'status': 'active'
                    })
                    
                    return {"status": "success"}
                    
                except (ValueError, IndexError) as e:
                    logger.error(f"Error parsing STM32 data: {e}")
                    raise HTTPException(status_code=400, detail="Invalid data format")
        
        return {"status": "ignored", "message": "Unrecognized data format"}
        
    except Exception as e:
        logger.error(f"Error processing STM32 data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
