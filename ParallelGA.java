import java.io.FileWriter;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Random;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

public class ParallelGA {

    // --- GA PARAMETERS ---
    static final int POPULATION_SIZE = 20; 
    static final int NUM_ISLANDS = 4;      // 4 CPU Cores
    static final int EPOCHS = 5;           // Can be higher now because it's so fast!
    static final int GENS_PER_EPOCH = 10;
    static final double MUTATION_RATE = 0.1;
    static final Random rand = new Random();

    static class Chromosome implements Comparable<Chromosome> {
        int nsGreen, ewGreen, partition, fitness;

        public Chromosome(int ns, int ew, int part) {
            this.nsGreen = ns;
            this.ewGreen = ew;
            this.partition = part;
            calculateFitness();
        }

        // 🚨 THE MACROSCOPIC HEURISTIC (Lightning Fast Math) 🚨
        public void calculateFitness() {
            // We want maximum North/South Green time, minimum East/West Green time
            // and we heavily reward deploying the movable partition (1)
            this.fitness = this.nsGreen - this.ewGreen + (50 * this.partition);
        }

        public void mutate() {
            if (rand.nextDouble() < MUTATION_RATE) {
                int gene = rand.nextInt(3);
                if (gene == 0) this.nsGreen = rand.nextInt(51) + 10;
                else if (gene == 1) this.ewGreen = rand.nextInt(51) + 10;
                else this.partition = this.partition == 0 ? 1 : 0;
            }
            calculateFitness();
        }

        @Override
        public int compareTo(Chromosome other) {
            return Integer.compare(other.fitness, this.fitness);
        }

        @Override
        public String toString() {
            return "[" + nsGreen + ", " + ewGreen + ", " + partition + "]";
        }
    }

    static class IslandTask implements Callable<List<Chromosome>> {
        List<Chromosome> population;
        public IslandTask(List<Chromosome> initialPop) { this.population = new ArrayList<>(initialPop); }
        
        @Override
        public List<Chromosome> call() {
            for (int g = 0; g < GENS_PER_EPOCH; g++) {
                Collections.sort(population);
                List<Chromosome> nextGen = new ArrayList<>(population.subList(0, POPULATION_SIZE / 2));
                while (nextGen.size() < POPULATION_SIZE) {
                    Chromosome p1 = population.get(rand.nextInt(5));
                    Chromosome p2 = population.get(rand.nextInt(5));
                    Chromosome child = new Chromosome(p1.nsGreen, p2.ewGreen, p2.partition);
                    child.mutate();
                    nextGen.add(child);
                }
                population = nextGen;
            }
            Collections.sort(population);
            return population;
        }
    }

    public static void main(String[] args) {
        System.out.println("--- INITIALIZING JAVA PARALLEL ISLAND MODEL ---");
        List<List<Chromosome>> islands = new ArrayList<>();
        for (int i = 0; i < NUM_ISLANDS; i++) {
            List<Chromosome> pop = new ArrayList<>();
            for (int j = 0; j < POPULATION_SIZE; j++) {
                pop.add(new Chromosome(rand.nextInt(51) + 10, rand.nextInt(51) + 10, rand.nextInt(2)));
            }
            islands.add(pop);
        }

        ExecutorService executor = Executors.newFixedThreadPool(NUM_ISLANDS);
        Chromosome globalBest = null;

        try {
            for (int epoch = 0; epoch < EPOCHS; epoch++) {
                List<Future<List<Chromosome>>> futures = new ArrayList<>();
                for (List<Chromosome> islandPop : islands) {
                    futures.add(executor.submit(new IslandTask(islandPop)));
                }
                for (int i = 0; i < NUM_ISLANDS; i++) {
                    islands.set(i, futures.get(i).get());
                }
                
                // Migration
                for (int i = 0; i < NUM_ISLANDS; i++) {
                    Chromosome elite = islands.get(i).get(0);
                    int nextIsland = (i + 1) % NUM_ISLANDS;
                    islands.get(nextIsland).set(POPULATION_SIZE - 1, elite);
                }
                
                // Find Best
                globalBest = islands.get(0).get(0);
                for (List<Chromosome> pop : islands) {
                    if (pop.get(0).fitness > globalBest.fitness) {
                        globalBest = pop.get(0);
                    }
                }
                System.out.println("   -> Epoch " + (epoch+1) + " | Global Best so far: " + globalBest + " | Score: " + globalBest.fitness);
            }

            System.out.println("\n--- EVOLUTION COMPLETE. SAVING DNA TO TEXT FILE ---");
            FileWriter writer = new FileWriter("winning_dna.txt");
            writer.write(globalBest.toString());
            writer.close();

        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            executor.shutdown();
        }
    }
}