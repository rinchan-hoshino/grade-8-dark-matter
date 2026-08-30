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
        registerTrades(item);
    }

    private static void registerTrades(Item item) {
        net.fabricmc.fabric.api.object.builder.v1.trade.TradeOfferHelper.registerVillagerOffers(
                net.minecraft.world.entity.npc.VillagerProfession.ARMORER, 1,
                offers -> offers.add(new net.minecraft.world.entity.npc.VillagerTrades.ItemsForEmeralds(item, 1, 1, 16, 2)));
        net.fabricmc.fabric.api.object.builder.v1.trade.TradeOfferHelper.registerVillagerOffers(
                net.minecraft.world.entity.npc.VillagerProfession.ARMORER, 3,
                offers -> offers.add(new net.minecraft.world.entity.npc.VillagerTrades.ItemsForEmeralds(item, 1, 1, 24, 10)));
        net.fabricmc.fabric.api.object.builder.v1.trade.TradeOfferHelper.registerVillagerOffers(
                net.minecraft.world.entity.npc.VillagerProfession.TOOLSMITH, 1,
                offers -> offers.add(new net.minecraft.world.entity.npc.VillagerTrades.ItemsForEmeralds(item, 1, 1, 16, 2)));
        net.fabricmc.fabric.api.object.builder.v1.trade.TradeOfferHelper.registerVillagerOffers(
                net.minecraft.world.entity.npc.VillagerProfession.TOOLSMITH, 3,
                offers -> offers.add(new net.minecraft.world.entity.npc.VillagerTrades.ItemsForEmeralds(item, 1, 1, 24, 10)));
    }
}
