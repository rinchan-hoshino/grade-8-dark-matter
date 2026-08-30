package dev.rinchan.darkmatter.fabric;

    import dev.rinchan.darkmatter.DarkMatter;
    import net.fabricmc.api.ModInitializer;
    import net.minecraft.core.Registry;
    import net.minecraft.core.registries.BuiltInRegistries;
    import net.minecraft.world.item.Item;

    public final class DarkMatterFabric implements ModInitializer {
        @Override
        public void onInitialize() {
            Item item = Registry.register(BuiltInRegistries.ITEM, DarkMatter.ITEM_ID, new Item(new Item.Properties()));
            DarkMatter.initialize(() -> item);

        }
}
