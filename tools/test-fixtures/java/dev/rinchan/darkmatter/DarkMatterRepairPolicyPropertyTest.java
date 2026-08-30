package dev.rinchan.darkmatter;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.Test;

final class DarkMatterRepairPolicyPropertyTest {
    @Test
    void materialCostAndRepairMatchLongReferenceAcrossBoundaries() {
        int[] damages = {
            Integer.MIN_VALUE, -1, 0, 1, 63, 64, 65, 127, 128, 129, 500,
            Integer.MAX_VALUE - 63, Integer.MAX_VALUE
        };
        int[] units = {Integer.MIN_VALUE, -1, 0, 1, 2, 7, 8, 33_554_432, Integer.MAX_VALUE};

        for (int damage : damages) {
            for (int available : units) {
                int expectedCost = referenceCost(damage, available);
                int actualCost = DarkMatterRepairPolicy.materialCost(damage, available);
                assertEquals(expectedCost, actualCost, () ->
                    "materialCost damage=" + damage + ", available=" + available
                );
                assertEquals(
                    referenceDamage(damage, actualCost),
                    DarkMatterRepairPolicy.repairedDamage(damage, actualCost),
                    () -> "repairedDamage damage=" + damage + ", consumed=" + actualCost
                );
                assertTrue(actualCost >= 0 && actualCost <= Math.max(0, available));
            }
        }
    }

    @Test
    void onePointPastAUnitBoundaryCannotUseFloorDivision() {
        assertEquals(2, DarkMatterRepairPolicy.materialCost(65, 8));
        assertEquals(1, DarkMatterRepairPolicy.repairedDamage(65, 1));
    }

    private static int referenceCost(int damage, int available) {
        if (damage <= 0 || available <= 0) {
            return 0;
        }
        long required = ((long) damage + 63L) / 64L;
        return (int) Math.min(required, (long) available);
    }

    private static int referenceDamage(int damage, int consumed) {
        if (damage <= 0) {
            return 0;
        }
        return (int) Math.max(0L, (long) damage - (long) Math.max(0, consumed) * 64L);
    }
}
