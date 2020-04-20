package discreteoptimization;

class Item {
    private int index;
    private int value;
    private int weight;
    private double valueToWeightRatio;
    private boolean isChosen;

    Item(int index, int value, int weight) {
        this.index = index;
        this.value = value;
        this.weight = weight;
        this.valueToWeightRatio = value * 1.0 / weight;
        this.isChosen = false;
    }

    private Item(int index, int value, int weight, boolean isChosen) {
        this(index, value, weight);
        this.setChosen(isChosen);
    }

    int getIndex() {
        return index;
    }

    int getValue() {
        return value;
    }

    int getWeight() {
        return weight;
    }

    double getValueToWeightRatio() {
        return valueToWeightRatio;
    }

    boolean getChosen() {
        return isChosen;
    }

    void setChosen(boolean chosen) {
        isChosen = chosen;
    }

    Item copy() {
        return new Item(index, value, weight, isChosen);
    }

}