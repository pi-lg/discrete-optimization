package discreteoptimization;

import java.util.List;

public class KnapSackResult {
    public int totalValue;
    public int totalWeight;
    public boolean[] chosen;

    public KnapSackResult(int totalValue, int totalWeight, boolean[] chosen) {
        this.totalValue = totalValue;
        this.totalWeight = totalWeight;
        this.chosen = chosen;
    }
}
