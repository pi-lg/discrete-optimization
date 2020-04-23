package discreteoptimization;

import java.util.*;

public class BranchAndBound {
    public enum SearchType {
        DEPTH_FIRST, BEST_FIRST, LEAST_DISCREPANCY, ALL
    }

    private SearchType searchType;
    private List<Item> items;
    private int knapSackCapacity;

    private int totalValue = 0;
    private int totalWeight = 0;
    private int weightOfSmallestItem;
    private double valueOfBestPath = 0;
    private boolean[] chosenOfBestPath;

//    private Comparator<Item> initialOrder = Comparator.comparing(Item::getIndex);
    private Comparator<Item> compareByValueDensity = Comparator.comparing(Item::getValueToWeightRatio).reversed();

    public BranchAndBound(SearchType searchType, List<Item> items, int knapSackCapacity) {
        this.searchType = searchType;
        this.items = items;
        this.weightOfSmallestItem = Integer.MAX_VALUE;
        int itemWeight;
        for(Item item: items) {
            itemWeight = item.getWeight();
            if(itemWeight < this.weightOfSmallestItem) {
                this.weightOfSmallestItem = itemWeight;
            }
        }
        this.knapSackCapacity = knapSackCapacity;
        this.chosenOfBestPath = new boolean[items.size()];
        Collections.sort(items, compareByValueDensity);
    }

    public KnapSackResult run() {
        Collections.sort(items, compareByValueDensity);
        if(searchType==SearchType.DEPTH_FIRST) {
            DepthFirstSearch depthFirstSearch = new DepthFirstSearch(
                    items, knapSackCapacity, findInitialOptimisticValue(), weightOfSmallestItem
            );
            depthFirstSearch.run();
            valueOfBestPath = depthFirstSearch.getValueOfBestPath();
            chosenOfBestPath = depthFirstSearch.getChosenOfBestPath();

            for(int i=0; i<items.size(); i++) {
                items.get(i).setChosen(chosenOfBestPath[i]);
                if(chosenOfBestPath[i]) {
                    totalValue += items.get(i).getValue();
                    totalWeight += items.get(i).getWeight();
                }
            }
//            System.out.println("Value of best path: " + valueOfBestPath + ", totalValue: " + totalValue + ", capacity left: " + (knapSackCapacity - totalWeight));
            return new KnapSackResult(totalValue, totalWeight, chosenOfBestPath);
        }
        return new KnapSackResult(0, 0, new boolean[items.size()]);
    }

    private double findInitialOptimisticValue() {
        int weight = 0;
        double value = 0;
        for(Item item: this.items) {
            if(weight + item.getWeight() < knapSackCapacity) {
                value += item.getValue();
                weight += item.getWeight();
            } else {
                int residualWeight = knapSackCapacity - weight;
                value += residualWeight * 1.0 / item.getWeight() * item.getValue();
                break;
            }
        }
        return value;
    }

}
