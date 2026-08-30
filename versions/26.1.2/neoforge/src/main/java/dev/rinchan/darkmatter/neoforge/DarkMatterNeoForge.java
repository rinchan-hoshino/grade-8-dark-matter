package dev.rinchan.darkmatter.neoforge;

import dev.rinchan.darkmatter.DarkMatter;
import net.minecraft.world.item.Item;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

@Mod(DarkMatter.MOD_ID)
public final class DarkMatterNeoForge {
    private static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(DarkMatter.MOD_ID);
    private static final DeferredItem<Item> DARK_MATTER = ITEMS.register("dark_matter", () -> new Item(new Item.Properties()));

    public DarkMatterNeoForge(IEventBus modBus) {
        ITEMS.register(modBus);
        DarkMatter.initialize(DARK_MATTER);

    }
}
