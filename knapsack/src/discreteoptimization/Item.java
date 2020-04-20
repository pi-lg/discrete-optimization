package discreteoptimization;

public class Item {
    private int index;
    private int value;
    private int weight;
    private double valueToWeightRatio;
    private boolean isChosen;

    public Item(int index, int value, int weight) {
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

    public int getIndex() {
        return index;
    }

    public int getValue() {
        return value;
    }

    public int getWeight() {
        return weight;
    }

    public double getValueToWeightRatio() {
        return valueToWeightRatio;
    }

    public Boolean getChosen() {
        return isChosen;
    }

    public void setChosen(Boolean chosen) {
        isChosen = chosen;
    }

    public Item copy() {
        return new Item(index, value, weight, isChosen);
    }

}