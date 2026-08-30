package dev.rinchan.darkmatter;

public final class DarkMatterRepairPolicy {
    public static final int DURABILITY_PER_UNIT = 64;

    private DarkMatterRepairPolicy() {}

    public static int materialCost(int damage, int availableUnits) {
        if (damage <= 0 || availableUnits <= 0) return 0;
        long required = ((long) damage + DURABILITY_PER_UNIT - 1L) / DURABILITY_PER_UNIT;
        return (int) Math.min(required, availableUnits);
    }

    public static int repairedDamage(int damage, int consumedUnits) {
        if (damage <= 0 || consumedUnits <= 0) return Math.max(0, damage);
        long repaired = (long) consumedUnits * DURABILITY_PER_UNIT;
        return (int) Math.max(0L, (long) damage - repaired);
    }
}
