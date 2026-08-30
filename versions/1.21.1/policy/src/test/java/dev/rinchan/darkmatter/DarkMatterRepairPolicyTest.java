package dev.rinchan.darkmatter;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

final class DarkMatterRepairPolicyTest {
    @Test
    void consumesOnlyUnitsNeededAndAvailable() {
        assertEquals(1, DarkMatterRepairPolicy.materialCost(64, 8));
        assertEquals(2, DarkMatterRepairPolicy.materialCost(65, 8));
        assertEquals(2, DarkMatterRepairPolicy.materialCost(500, 2));
    }

    @Test
    void repairsSixtyFourDurabilityPerConsumedUnit() {
        assertEquals(0, DarkMatterRepairPolicy.repairedDamage(64, 1));
        assertEquals(1, DarkMatterRepairPolicy.repairedDamage(65, 1));
        assertEquals(372, DarkMatterRepairPolicy.repairedDamage(500, 2));
    }

    @Test
    void rejectsEmptyInputsAndDoesNotOverflow() {
        assertEquals(0, DarkMatterRepairPolicy.materialCost(0, 8));
        assertEquals(0, DarkMatterRepairPolicy.materialCost(10, 0));
        assertEquals(0, DarkMatterRepairPolicy.repairedDamage(-4, 1));
        assertEquals(0, DarkMatterRepairPolicy.repairedDamage(Integer.MAX_VALUE, Integer.MAX_VALUE));
    }
}
