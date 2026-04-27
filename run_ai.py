import traci
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler

print("Waking up the AI Supervisor...")

# 1. Setup the Scaler
# We need to scale our live data exactly how we scaled the training data.
# We do this by letting the scaler quickly peek at the historic dataset.
df = pd.read_csv('traffic_data.csv')
features = df[['North_Queue', 'East_Queue', 'Accident_Active']].values
scaler = MinMaxScaler(feature_range=(0, 1))
scaler.fit(features) 

# 2. Load the trained neural network
model = load_model('supervisor_lstm.keras')
print("AI Supervisor loaded and ready.")

# 3. Connect to SUMO
sumoCmd = ["sumo-gui", "-c", "network/sim_accident.sumocfg"]
traci.start(sumoCmd)
TLS_ID = "J16"

# The LSTM needs a "rolling memory" of the last 10 seconds to make a prediction
memory = []
step = 0

print("Starting live simulation under AI control...")

while step < 1000: # Running for 1000 seconds
    traci.simulationStep()
    
    # --- A. SENSE (Gather real-time data) ---
    north_q = traci.edge.getLastStepHaltingNumber("-E10")
    east_q = traci.edge.getLastStepHaltingNumber("-E12")
    accident = 1 if step >= 30 else 0 
    
    current_state = [north_q, east_q, accident]
    
    # Scale the live data so the neural network can understand it
    scaled_state = scaler.transform([current_state])[0]
    memory.append(scaled_state)
    
    # Keep only the most recent 10 seconds in memory
    if len(memory) > 10:
        memory.pop(0)
        
    # --- B. PREDICT & ACT ---
    # Once we have 10 seconds of data, the AI starts working
    if len(memory) == 10:
        # Format the memory for the LSTM (1 sample, 10 time steps, 3 features)
        input_data = np.array([memory])
        
        # The AI predicts the scaled future queue
        predicted_scaled_queue = model.predict(input_data, verbose=0)
        
        # Un-scale the prediction back into normal "number of cars"
        dummy = np.zeros((1, 3))
        dummy[0, 0] = predicted_scaled_queue[0][0]
        predicted_queue = scaler.inverse_transform(dummy)[0, 0]
        
        # Print an update every 5 seconds
        if step % 5 == 0:
            print(f"Time: {step:03d}s | Actual North Q: {north_q:02d} | AI Predicts: {predicted_queue:.1f} cars")
            
        # THE TRIGGER MECHANISM (As defined in your research blueprint!)
        # If the AI predicts the queue is going to blow past 10 cars...
        if predicted_queue > 10:
            print(f"   [Time: {step}s] AI predicts severe bottleneck. Forcing North green light.")
            # Override the light to Phase 2 (North/South Green)
            traci.trafficlight.setPhase(TLS_ID, 2)
            
    step += 1

traci.close()
print("Simulation complete.")