import traci

# 1. Define the command to start SUMO. 
# We are loading the accident scenario so we can measure the bottleneck.
sumoCmd = ["sumo-gui", "-c", "network/sim_accident.sumocfg"]

# 2. Start the connection! This will automatically pop open the SUMO window.
traci.start(sumoCmd)

step = 0
# 3. Run a loop to step through the simulation one second at a time
while step < 1000:
    traci.simulationStep() # This moves the simulation forward by 1 second
    
    # 4. Every 10 seconds, check the queue length on the North road (-E10)
    if step % 10 == 0:
        # "Halting Number" means cars that are stopped or moving less than 0.1 m/s
        queue_length = traci.edge.getLastStepHaltingNumber("-E10")
        
        if step < 30:
            print(f"Time: {step:03d}s | Status: Normal Flow      | North Queue: {queue_length}")
        elif step == 30:
            print(f"Time: {step:03d}s | 💥 ACCIDENT OCCURRED! 💥")
        else:
            print(f"Time: {step:03d}s | Status: Bottleneck       | North Queue: {queue_length}")
            
    step += 1

# 5. Close the connection when done
traci.close()