import random
import multiprocessing
import traci
import string
import sumolib

# --- GA PARAMETERS ---
POPULATION_SIZE = 10   
ISLANDS = 4            
EPOCHS = 2             
GENS_PER_EPOCH = 3     
MUTATION_RATE = 0.1    

def create_random_solution():
    return [random.randint(10, 60), random.randint(10, 60), random.randint(0, 1)]

def calculate_fitness(solution):
    ns_green, ew_green, partition = solution
    
    conn_label = "sim_" + "".join(random.choices(string.ascii_letters, k=8))
    sumoCmd = ["sumo", "-c", "network/sim_accident.sumocfg", "--no-step-log", "true", "--no-warnings", "true"]
    
    safe_port = sumolib.miscutils.getFreeSocketPort()
    traci.start(sumoCmd, label=conn_label, port=safe_port)
    
    conn = traci.getConnection(conn_label)
    
    for _ in range(30):
        conn.simulationStep()
        
    if ns_green > ew_green:
        conn.trafficlight.setPhase("J16", 2) 
    else:
        conn.trafficlight.setPhase("J16", 0) 
        
    for _ in range(60):
        conn.simulationStep()
        
    cars_trapped = conn.edge.getLastStepHaltingNumber("-E10")
    conn.close()
    
    return -cars_trapped

def crossover(parent1, parent2):
    return [parent1[0], parent2[1], parent2[2]]

def mutate(solution):
    if random.random() < MUTATION_RATE:
        gene = random.randint(0, 2)
        if gene == 0: solution[0] = random.randint(10, 60)
        elif gene == 1: solution[1] = random.randint(10, 60)
        else: solution[2] = 1 if solution[2] == 0 else 0
    return solution

def evolve_island(population):
    for _ in range(GENS_PER_EPOCH):
        population = sorted(population, key=calculate_fitness, reverse=True)
        next_generation = population[:POPULATION_SIZE // 2]
        
        while len(next_generation) < POPULATION_SIZE:
            p1 = random.choice(population[:5])
            p2 = random.choice(population[:5])
            next_generation.append(mutate(crossover(p1, p2)))
            
        population = next_generation
    return sorted(population, key=calculate_fitness, reverse=True)

# Wrapper function to run parallel evolution.
def run_evolution():
    print("INITIALIZING ISLAND MODEL PARALLEL GA")
    
    islands = [[create_random_solution() for _ in range(POPULATION_SIZE)] for _ in range(ISLANDS)]
    global_best = None
    
    with multiprocessing.Pool(processes=ISLANDS) as pool:
        for epoch in range(EPOCHS):
            print(f"\n--- Epoch {epoch + 1}: Evolving {ISLANDS} Islands Independently ---")
            
            islands = pool.map(evolve_island, islands)
            
            print("   -> Migration Phase: Shipping elite DNA across the ocean...")
            for i in range(ISLANDS):
                elite_dna = islands[i][0] 
                next_island = (i + 1) % ISLANDS
                islands[next_island][-1] = elite_dna 
            
            global_best = max([island[0] for island in islands], key=calculate_fitness)
            print(f"   -> Global Best so far: {global_best} | Trapped Cars: {-calculate_fitness(global_best)}")

    print("\nPARALLEL EVOLUTION COMPLETE")
    with open("winning_dna.txt", "w") as f:
        f.write(str(global_best))
    return global_best

if __name__ == "__main__":
    run_evolution()