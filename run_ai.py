import traci
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
import xml.etree.ElementTree as ET
import os # <-- ADDED IMPORT

def calculate_simulation_metrics(tripinfo_file="network/tripinfo_output.xml", cycle_time=90, sim_time=3600):
    """
    Extracts Average Delay Time (D) and Number of Stops per Cycle (NS) 
    from SUMO's tripinfo output.
    """
    if not os.path.exists(tripinfo_file):
        print(f"Error: {tripinfo_file} not found. Did the simulation finish?")
        return None, None

    tree = ET.parse(tripinfo_file)
    root = tree.getroot()

    total_waiting_time = 0.0
    total_stops = 0
    vehicle_count = 0

    # Parse every vehicle's trip data
    for trip in root.findall('tripinfo'):
        total_waiting_time += float(trip.get('waitingTime'))
        total_stops += int(trip.get('waitingCount'))
        vehicle_count += 1

    if vehicle_count == 0:
        return 0.0, 0.0

    # D: Average Delay Time (seconds)
    average_delay_time = total_waiting_time / vehicle_count
    
    # NS: Number of vehicles suffering stops per cycle
    total_cycles = sim_time / cycle_time
    stops_per_cycle = total_stops / total_cycles

    print(f"--- Simulation Results ---")
    print(f"Total Vehicles Processed: {vehicle_count}")
    print(f"Average Delay Time (D): {average_delay_time:.2f} seconds")
    print(f"Stops Per Cycle (NS): {stops_per_cycle:.2f} stops")

    return average_delay_time, stops_per_cycle

print("Waking up the AI Supervisor...")

# 1. Setup the Scaler
df = pd.read_csv('traffic_data.csv')
features = df[['North_Queue', 'East_Queue', 'Accident_Active']].values
scaler = MinMaxScaler(feature_range=(0, 1))
scaler.fit(features) 

# 2. Load the trained neural network
model = load_model('supervisor_lstm.keras')
print("AI Supervisor loaded and ready.")

# 3. Connect to SUMO
# Make sure to run this using the standard sumocfg for Baseline tests, and accident for accident tests.
sumoCmd = ["sumo", "-c", "network/sim_accident.sumocfg"] # Changed sumo-gui to sumo
traci.start(sumoCmd)
TLS_ID = "J16"

memory = []
step = 0

print("Starting live simulation under AI control...")

# CHANGED: Loop now runs for the full 3600 seconds to match config
while step < 3600: 
    traci.simulationStep()
    
    # --- A. SENSE ---
    north_q = traci.edge.getLastStepHaltingNumber("-E10")
    east_q = traci.edge.getLastStepHaltingNumber("-E12")
    accident = 1 if step >= 30 else 0 
    
    current_state = [north_q, east_q, accident]
    
    scaled_state = scaler.transform([current_state])[0]
    memory.append(scaled_state)
    
    if len(memory) > 10:
        memory.pop(0)
        
    # --- B. PREDICT & ACT ---
    if len(memory) == 10:
        input_data = np.array([memory])
        
        predicted_scaled_queue = model.predict(input_data, verbose=0)
        
        dummy = np.zeros((1, 3))
        dummy[0, 0] = predicted_scaled_queue[0][0]
        predicted_queue = scaler.inverse_transform(dummy)[0, 0]
        
        if step % 5 == 0:
            print(f"Time: {step:03d}s | Actual North Q: {north_q:02d} | AI Predicts: {predicted_queue:.1f} cars")
            
        if predicted_queue > 10:
            print(f"   [Time: {step}s] AI predicts severe bottleneck. Forcing North green light.")
            traci.trafficlight.setPhase(TLS_ID, 2)
            
    step += 1

traci.close()
d_metric, ns_metric = calculate_simulation_metrics()
print("Simulation complete.")