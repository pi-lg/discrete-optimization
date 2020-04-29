package discreteoptimization;

import java.util.*;
import java.util.stream.Collectors;

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
    private Comparator<Item> compareByValueDensityHighestFirst = Comparator.comparing(Item::getValueToWeightRatio).reversed();
    private Comparator<Item> compareByWeightLowestFirst = Comparator.comparing(Item::getWeight);
    private Comparator<Item> compareByValueHighestFirst = Comparator.comparing(Item::getWeight).reversed();

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
        Collections.sort(items, compareByValueDensityHighestFirst);
    }

    public KnapSackResult run() {
        Collections.sort(items, compareByValueDensityHighestFirst);
        if(items.size()<=2) {
            return solveBruteForce();
        } else if(searchType==SearchType.DEPTH_FIRST) {
            DepthFirstSearch depthFirstSearch = new DepthFirstSearch(
                    items, knapSackCapacity, weightOfSmallestItem
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
//            Collections.sort(items, compareByWeightLowestFirst);
//            ArrayList<Item> stillFittingItems = new ArrayList<>();
//            int capacityLeft = knapSackCapacity - totalWeight;
//            for(Item item: items) {
//                if(!item.getChosen() && item.getWeight() <= capacityLeft) {
//                    stillFittingItems.add(item);
//                }
//            }
//            Collections.sort(stillFittingItems, compareByValueHighestFirst);
//            for(Item item: stillFittingItems) {
//                if(item.getWeight() <= capacityLeft) {
//                    item.setChosen(true);
//                    capacityLeft -= item.getWeight();
//                    totalValue += item.getValue();
//                    totalWeight += item.getWeight();
//                }
//            }
//
//            System.out.println("Value of best path: " + valueOfBestPath + ", totalValue: " + totalValue + ", capacity left: " + (knapSackCapacity - totalWeight));
            return new KnapSackResult(totalValue, totalWeight);
        } else {
            return new KnapSackResult(0, 0);
        }
    }

    private KnapSackResult solveBruteForce() {
        Set<Integer> bestCombination = new HashSet<>();
        int valueOfBestCombination = 0;
        int weightOfBestCombination = Integer.MAX_VALUE;
        for(Set<Integer> itemCombination: findAllPossibleCombinationsOfItemIndices(items.size())) {
            List<Item> filteredItems = items.stream()
                    .filter(item -> itemCombination.contains(item.getIndex()))
                    .collect(Collectors.toList());
            int weight = filteredItems.stream().mapToInt(Item::getWeight).sum();
            if(weight <= knapSackCapacity) {
                int value = filteredItems.stream().mapToInt(Item::getValue).sum();
                if(value > valueOfBestCombination) {
                    bestCombination = itemCombination;
                    valueOfBestCombination = value;
                    weightOfBestCombination = weight;
                }
            }
        }
        for(Item item: items) {
            item.setChosen(bestCombination.contains(item.getIndex()));
        }

        return new KnapSackResult(valueOfBestCombination, weightOfBestCombination);
    }

    public static ArrayList<Set<Integer>> findAllPossibleCombinationsOfItemIndices(int numItems) {
        ArrayList<Set<Integer>> possibleCombinations = new ArrayList<>(2 ^ numItems);
        possibleCombinations.add(new HashSet<>());
        Set<Integer> copy = new HashSet(possibleCombinations.get(0));
        copy.add(0);
        possibleCombinations.add(copy);
        for(int i=1; i<numItems; i++) {
            ArrayList<Set<Integer>> additionalItemSets = new ArrayList<>();
            for(Set<Integer> set: possibleCombinations) {
                copy = new HashSet<>(set);
                copy.add(i);
                additionalItemSets.add(copy);
            }
            possibleCombinations.addAll(additionalItemSets);
        }
        return possibleCombinations;
    }

//    private void fillUpWithHighestValueItem

}
