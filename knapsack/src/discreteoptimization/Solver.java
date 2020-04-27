package discreteoptimization;

import java.io.*;
import java.sql.Array;
import java.util.*;

/**
 * The class <code>Solver</code> is an implementation of a greedy algorithm to solve the knapsack problem.
 *
 */
public class Solver {
    
    /**
     * The main class
     */
    public static void main(String[] args) {
        try {
            solve(args);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
    
    /**
     * Read the instance, solve it, and print the solution in the standard output
     */
    public static void solve(String[] args) throws IOException {
        String fileName = null;
        
        // get the temp file name
        for(String arg : args){
            if(arg.startsWith("-file=")){
                fileName = arg.substring(6);
            } 
        }
        if(fileName == null)
            return;
        
        // read the lines out of the file
        List<String> lines = new ArrayList<String>();

        BufferedReader input = new BufferedReader(new FileReader(fileName));
        try {
            String line = null;
            while (( line = input.readLine()) != null){
                lines.add(line);
            }
        }
        finally {
            input.close();
        }
        
        
        // parse the data in the file
        String[] firstLine = lines.get(0).split("\\s+");
        int num_items = Integer.parseInt(firstLine[0]);
        int capacity = Integer.parseInt(firstLine[1]);

        int[] values = new int[num_items];
        int[] weights = new int[num_items];

        ArrayList<Item> items = new ArrayList<>();
        for(int i=1; i < num_items+1; i++){
            String line = lines.get(i);
            String[] parts = line.split("\\s+");
            items.add(new Item(i - 1, Integer.parseInt(parts[0]), Integer.parseInt(parts[1])));
            values[i-1] = Integer.parseInt(parts[0]);
            weights[i-1] = Integer.parseInt(parts[1]);
        }
        Comparator<Item> initialOrder = Comparator.comparing(Item::getIndex);
        Comparator<Item> compareByValueDensity = Comparator.comparing(Item::getValueToWeightRatio);
        Collections.sort(items, compareByValueDensity.reversed());
        int value = 0;
        int weight = 0;
        int[] taken = new int[num_items];

        for(Item item: items){
            if(weight + item.getWeight() <= capacity){
                item.setChosen(true);
                value += item.getValue();
//                System.out.println("Value to weight ratio: " + item.getValueToWeightRatio());
                weight += item.getWeight();
            } else {
                break;
            }
        }

        // prepare the solution in the specified output format
//        System.out.println("greedy algorithm:");
//        System.out.println(value+" 0");
//        Collections.sort(items, initialOrder);
//        for(Item item: items){
//            System.out.print(Integer.toString(item.getChosen() ? 1 : 0)+" ");
//        }
//        System.out.println("");
        BranchAndBound branchAndBound = new BranchAndBound(BranchAndBound.SearchType.DEPTH_FIRST, items, capacity);
        KnapSackResult resultBranchAndBound = branchAndBound.run();
//        System.out.println("resultBranchAndBound.totalWeight = " + resultBranchAndBound.totalWeight);
//        System.out.println("resultBranchAndBound.totalValue = " + resultBranchAndBound.totalValue);
//        Comparator<Item> compareByWeight = Comparator.comparing(Item::getWeight);
//        Collections.sort(items, compareByWeight);
//        System.out.println("items.get(0).getChosen() = " + items.get(0).getChosen());
//        System.out.println("items.get(0).getValue() = " + items.get(0).getValue());
//        System.out.println("branch and bound");
        System.out.println(resultBranchAndBound.totalValue+" 0");
        Collections.sort(items, initialOrder);
        for(Item item: items){
            System.out.print(Integer.toString(item.getChosen() ? 1 : 0)+" ");
        }
        System.out.println("");
    }
}