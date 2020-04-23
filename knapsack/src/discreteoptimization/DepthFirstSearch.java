package discreteoptimization;

import java.util.Arrays;
import java.util.List;

public class DepthFirstSearch {
    private int position = 0;
    private double optimisticValueOfCurrentPath;
    private boolean[] chosenOfCurrentPath;
    private boolean[] chosenOfBestPath;
    private int valueOfCurrentPath = 0;
    private int valueOfBestPath = 0;
    private List<Item> items;
    private int capacity;
    private int weightOfSmallestItem;

    public DepthFirstSearch(List<Item> items, int capacity, double optimisticValueOfCurrentPath,
                            int weightOfSmallestItem) {
        this.optimisticValueOfCurrentPath = optimisticValueOfCurrentPath;
        this.items = items;
        this.capacity = capacity;
        this.chosenOfCurrentPath = new boolean[items.size()];
        Arrays.fill(this.chosenOfCurrentPath, Boolean.FALSE);
        this.chosenOfBestPath = this.chosenOfCurrentPath.clone();
        this.weightOfSmallestItem = weightOfSmallestItem;
//        System.out.println("weight of smallest item " + weightOfSmallestItem);
    }

    public void run() {

        exploreDeep();
    }

    public boolean[] getChosenOfBestPath() {
        return chosenOfBestPath;
    }

    public int getValueOfBestPath() {
        return valueOfBestPath;
    }

    private void exploreDeep() {
        if(position<0) {
//            numberOfTimesPosition0WasVisited++;
//            if(numberOfTimesPosition0WasVisited >= 3) {
                return;
//            }
        }
        if(position>=items.size()) {
//            System.out.println("End node reached.");
            compareToAndUpdateBestPath();
//            System.out.println("backing up one step at position " + position);
            position--;
//            System.out.println("New position is " + position);
            if(chosenOfCurrentPath[position]) {
                unpackItem();
                position++;
                exploreDeep();
            } else {
                optimisticValueOfCurrentPath += items.get(position).getValue();
                goBackToLastChosenItem();
//                System.out.println("Position is " + position + " after backing up to last chosen item.");
//                printChosenVector(chosenOfCurrentPath);
                unpackItem();
                position++;
                exploreDeep();
            }
        } else if(position<0) {
            return;
        } else if (Double.max(valueOfCurrentPath, optimisticValueOfCurrentPath) > valueOfBestPath) {
            if(items.get(position).getWeight() < capacity) {
                packItem();
                position++;
                exploreDeep();
            } else if (capacity < weightOfSmallestItem) {
                dismissTheRestOfTheItems();
                compareToAndUpdateBestPath();
                goBackToLastChosenItem();
                unpackItem();
                if(position<0) return;
                position++;
                exploreDeep();
            } else {
//                System.out.println("Leaving item " + position + " behind.");
                dismissItem();
                position++;
                exploreDeep();
            }
        } else {
            goBackToLastChosenItem();
            if(position<0) return;
            unpackItem();
            position++;
            exploreDeep();
        }
    }

    private void compareToAndUpdateBestPath() {
        if(valueOfCurrentPath > valueOfBestPath) {
//                System.out.println("New best path found with Value " + valueOfCurrentPath);
            valueOfBestPath = valueOfCurrentPath;
            chosenOfBestPath = chosenOfCurrentPath.clone();
        }
    }

    private void dismissTheRestOfTheItems() {
        for(int i=position; i<items.size(); i++) {
            chosenOfCurrentPath[i] = false;
        }
    }

    private void dismissItem() {
        chosenOfCurrentPath[position] = false;
        optimisticValueOfCurrentPath -= items.get(position).getValue();
    }

    private void packItem() {
        if(!chosenOfCurrentPath[position]) {
//            System.out.println("Packing item " + position + " into the knapsack");
            chosenOfCurrentPath[position] = true;
            valueOfCurrentPath += items.get(position).getValue();
            capacity -= items.get(position).getWeight();
        } else {
//            System.out.println("Item " + position + "is already packed, packing is not necessary.");
        }
    }

    private void unpackItem() {
        if(chosenOfCurrentPath[position]) {
            chosenOfCurrentPath[position] = false;
//            System.out.println("Unpacking item " + position);
            valueOfCurrentPath -= items.get(position).getValue();
            optimisticValueOfCurrentPath -= items.get(position).getValue();
            capacity += items.get(position).getWeight();
        } else {
//            System.out.println("Item " + position + " was not packed, so unpacking is not necessary.");
        }
    }
    private void printChosenVector(boolean[] chosen) {
        for(boolean b : chosen) {
            System.out.print(b + " ");
            System.out.println("");
        }
    }
    private void goBackToLastChosenItem() {
        position--;
        if(position<0) {
            return;
        }
//        System.out.println("Going back one node to position " + position);
        if(chosenOfCurrentPath[position]) {
            return;
        } else {
            optimisticValueOfCurrentPath += items.get(position).getValue();
            goBackToLastChosenItem();
        }
    }
}
