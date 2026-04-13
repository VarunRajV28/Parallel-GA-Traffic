import traci
import csv # We need this to write our dataset!

# Define the command to start SUMO
sumoCmd = ["sumo-gui", "-c", "network/sim_accident.sumocfg"]
TLS_ID = "J16"

# 1. Create and open a new CSV file to record our data
with open('traffic_data.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    # Write the column headers
    writer.writerow(["Time_Step", "North_Queue", "East_Queue", "Accident_Active"])

    # Start the simulation
    traci.start(sumoCmd)
    step = 0
    
    print("🚦 Simulation running. Recording data to traffic_data.csv...")

    # Run the loop
    while step < 3600: # Let's run it for a full hour of simulation time
        traci.simulationStep()
        
        # Check queues every second
        north_queue = traci.edge.getLastStepHaltingNumber("-E10")
        east_queue = traci.edge.getLastStepHaltingNumber("-E12")
        
        # Determine if the accident has happened yet (at step 30)
        accident_active = 1 if step >= 30 else 0
        
        # Write this exact second of data into the CSV
        writer.writerow([step, north_queue, east_queue, accident_active])
        
        # Print an update to the console every 100 steps so we know it's working
        if step % 100 == 0:
            print(f"Recorded Step {step:04d} | North Q: {north_queue:02d} | East Q: {east_queue:02d}")
                
        step += 1

    traci.close()
    print("✅ Simulation complete! Data saved to traffic_data.csv")