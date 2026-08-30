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

        net.neoforged.neoforge.common.NeoForge.EVENT_BUS.addListener(DarkMatterNeoForge::onVillagerTrades);
    }

    private static void onVillagerTrades(net.neoforged.neoforge.event.village.VillagerTradesEvent event) {
        if (event.getType() != net.minecraft.world.entity.npc.VillagerProfession.ARMORER
                && event.getType() != net.minecraft.world.entity.npc.VillagerProfession.TOOLSMITH) return;
        event.getTrades().get(1).add(new net.minecraft.world.entity.npc.VillagerTrades.ItemsForEmeralds(DARK_MATTER.get(), 1, 1, 16, 2));
        event.getTrades().get(3).add(new net.minecraft.world.entity.npc.VillagerTrades.ItemsForEmeralds(DARK_MATTER.get(), 1, 1, 24, 10));
    }
}
