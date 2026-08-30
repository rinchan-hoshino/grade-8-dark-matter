package dev.rinchan.darkmatter;

import java.util.Objects;
import java.util.function.Supplier;
import net.minecraft.resources.Identifier;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;

public final class DarkMatter {
    public static final String MOD_ID = "dark_matter";
    public static final Identifier ITEM_ID = Identifier.fromNamespaceAndPath(MOD_ID, "dark_matter");
    private static Supplier<? extends Item> item;

    private DarkMatter() {}

    public static void initialize(Supplier<? extends Item> registeredItem) {
        if (item != null) throw new IllegalStateException("Dark Matter already initialized");
        item = Objects.requireNonNull(registeredItem);
    }

    public static boolean isDarkMatter(ItemStack stack) {
        return item != null && stack.is(item.get());
    }
}
