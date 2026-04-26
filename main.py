import traci
import numpy as np
from tensorflow.keras.models import load_model
import subprocess # 👈 Used to run isolated programs!
import ast

def run_simulation():
    print("🧠 Loading AI Supervisor...")
    model = load_model('supervisor_lstm.keras')

    sumoCmd = ["sumo-gui", "-c", "network/sim_accident.sumocfg"]
    traci.start(sumoCmd)

    step = 0
    history_window = []
    ga_triggered = False 

    print("🚦 Simulation started. Waiting for baseline data...")

    while step < 1000:
        traci.simulationStep()
        
        north_q = traci.edge.getLastStepHaltingNumber("-E10")
        east_q = traci.edge.getLastStepHaltingNumber("-E12")
        accident_active = 1 if step >= 30 else 0
        
        current_state = [north_q / 100.0, east_q / 100.0, accident_active]
        history_window.append(current_state)
        
        if len(history_window) > 10:
            history_window.pop(0)
            
        if len(history_window) == 10 and step % 5 == 0 and not ga_triggered:
            ai_input = np.array([history_window])
            predicted_queue = int(model.predict(ai_input, verbose=0)[0][0] * 100)
            
            print(f"Time {step:03d}s | Actual Q: {north_q:02d} | AI Predicts: {predicted_queue:02d}")
            
            if predicted_queue > 15:
                print("\n🚨 SUPERVISOR ALERT: Massive anomaly predicted! 🚨")
                print("⏸️ Pausing Main Simulation. Waking up Parallel GA Islands...\n")
                
                # 🚀 THE FIX: Run Java and tell it where the TraaS library is
                subprocess.run(["java", "ParallelGA"])
                
                # 📖 Read the winning DNA from the text file it just generated
                with open("winning_dna.txt", "r") as f:
                    dna_string = f.read().strip()
                    winning_dna = ast.literal_eval(dna_string) # Turns the string back into a Python List
                
                print("\n✅ GA Complete. Best Solution Found:", winning_dna)
                print("▶️ Applying solution and resuming Main Simulation...\n")
                
                # Apply the winning DNA safely
                if winning_dna[0] > winning_dna[1]:
                    traci.trafficlight.setPhase("J16", 2) # Force North Green
                else:
                    traci.trafficlight.setPhase("J16", 0) # Force East/West Green
                
                ga_triggered = True 

        step += 1

    traci.close()

if __name__ == '__main__':
    run_simulation()