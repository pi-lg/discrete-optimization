package discreteoptimization;

import java.util.Arrays;
import java.util.Collections;
import java.util.Comparator;
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
    private int weightOfCurrentPath = 0;
    private int weightOfSmallestItem;

    public DepthFirstSearch(List<Item> items, int capacity,
                            int weightOfSmallestItem) {
        this.items = items;
        this.capacity = capacity;
        this.chosenOfCurrentPath = new boolean[items.size()];
        Arrays.fill(this.chosenOfCurrentPath, Boolean.FALSE);
        this.chosenOfBestPath = this.chosenOfCurrentPath.clone();
        this.weightOfSmallestItem = weightOfSmallestItem;
//        System.out.println("weight of smallest item " + weightOfSmallestItem);
    }

    public void run() {
//        System.out.println("Capacity of knapsack: " + capacity);
//        System.out.println("number of items = " + items.size());
//        System.out.println("weightOfSmallestItem = " + weightOfSmallestItem);
//        Comparator<Item> compareByWeight = Comparator.comparing(Item::getWeight);
        Comparator<Item> compareByValueWeightRatio = Comparator.comparing(Item::getValueToWeightRatio).reversed();
//        Collections.sort(items, compareByWeight);
//        for(int i=0; i<5; i++) {
//            System.out.println("weight of lightest item" + (i + 1) + " is " + items.get(i).getWeight());
//        }
//        System.out.println("items.size() = " + items.size());
        Collections.sort(items, compareByValueWeightRatio);
        updateOptimisticValue();
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
                exploreDeep();
            } else {
                goBackToLastChosenItem();
//                System.out.println("Position is " + position + " after backing up to last chosen item.");
//                printChosenVector(chosenOfCurrentPath);
                unpackItem();
                exploreDeep();
            }
        } else if(position<0) {
            return;
        } else if (Double.max(valueOfCurrentPath, optimisticValueOfCurrentPath) > valueOfBestPath) {
            if(items.get(position).getWeight() <= capacity) {
                packItem();
                while(position<items.size()-1 && items.get(position).getWeight() <= capacity) {
                    packItem();
                }
                exploreDeep();
            } else if (capacity < weightOfSmallestItem) {
                dismissTheRestOfTheItems();
                compareToAndUpdateBestPath();
                goBackToLastChosenItem();
                unpackItem();
//                if(position<0) return;
                exploreDeep();
            } else {
//                System.out.println("Leaving item " + position + " behind.");
//                System.out.println("Capacity left: " + capacity + ", item weight: " + items.get(position).getWeight() + ", item value; " + items.get(position).getValue() + ", optimistic path value before dismissal: " + optimisticValueOfCurrentPath);
                dismissItem();
//                System.out.println("Optimistic path value after dismissal: " + optimisticValueOfCurrentPath);
//                System.out.println("value of best path: " + valueOfBestPath);
//                System.out.println("weight of smallest item: " + weightOfSmallestItem);
                while(position<items.size()-1 && items.get(position).getWeight() > capacity) {
                    dismissItem();
                }
                exploreDeep();
            }
        } else {
            goBackToLastChosenItem();
            if(position<0) return;
            unpackItem();
            exploreDeep();
        }
    }

    private void updateOptimisticValue() {
        int optimisticCapacity = capacity;
        int optimisticPosition = position;
        optimisticValueOfCurrentPath = valueOfCurrentPath;
        while(optimisticPosition < items.size() && items.get(optimisticPosition).getWeight() < optimisticCapacity) {
            optimisticValueOfCurrentPath += items.get(optimisticPosition).getValue();
            optimisticCapacity -= items.get(optimisticPosition).getWeight();
            optimisticPosition++;
        }
        if(optimisticPosition < items.size()) {
            optimisticValueOfCurrentPath += items.get(optimisticPosition).getValueToWeightRatio() * optimisticCapacity;
        }
    }

    private void compareToAndUpdateBestPath() {
        if(valueOfCurrentPath > valueOfBestPath) {
//            System.out.println("New best path found with Value " + valueOfCurrentPath);
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
        position++;
        updateOptimisticValue();
    }

    private void packItem() {
        if(!chosenOfCurrentPath[position]) {
//            System.out.println("Packing item " + position + " into the knapsack");
            chosenOfCurrentPath[position] = true;
            valueOfCurrentPath += items.get(position).getValue();
            weightOfCurrentPath += items.get(position).getWeight();
            capacity -= items.get(position).getWeight();
            position++;
        } else {
//            System.out.println("Item " + position + "is already packed, packing is not necessary.");
        }
    }

    private void unpackItem() {
        if(chosenOfCurrentPath[position]) {
            chosenOfCurrentPath[position] = false;
//            System.out.println("Unpacking item " + position);
            valueOfCurrentPath -= items.get(position).getValue();
            weightOfCurrentPath -= items.get(position).getWeight();
            capacity += items.get(position).getWeight();
//            System.out.println("Unpacked item " + position);
            position++;
            updateOptimisticValue();
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
        while(position >= 0 && !chosenOfCurrentPath[position]) {
            position--;
        }
//        if(position<0) {
//            return;
//        }
////        System.out.println("Going back one node to position " + position);
//        if(chosenOfCurrentPath[position]) {
//            return;
//        } else {
//            goBackToLastChosenItem();
//        }
    }
}
