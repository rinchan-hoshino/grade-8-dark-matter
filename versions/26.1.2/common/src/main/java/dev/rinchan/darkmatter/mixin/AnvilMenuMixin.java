package dev.rinchan.darkmatter.mixin;

import dev.rinchan.darkmatter.DarkMatter;
import dev.rinchan.darkmatter.DarkMatterRepairPolicy;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AnvilMenu;
import net.minecraft.world.inventory.DataSlot;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(AnvilMenu.class)
abstract class AnvilMenuMixin {
    @Shadow @Final private DataSlot cost;
    @Shadow private int repairItemCountCost;
    @Unique private boolean dark_matter$repair;

    @Inject(method = "createResult", at = @At("RETURN"))
    private void dark_matter$createRepairResult(CallbackInfo ci) {
        AnvilMenu menu = (AnvilMenu) (Object) this;
        ItemStack left = menu.getSlot(0).getItem();
        ItemStack right = menu.getSlot(1).getItem();
        dark_matter$repair = false;

        if (!DarkMatter.isDarkMatter(right) || !left.isDamageableItem() || left.getDamageValue() <= 0) return;

        int consumed = DarkMatterRepairPolicy.materialCost(left.getDamageValue(), right.getCount());
        if (consumed == 0) return;

        ItemStack output = left.copyWithCount(1);
        output.setDamageValue(DarkMatterRepairPolicy.repairedDamage(left.getDamageValue(), consumed));
        repairItemCountCost = consumed;
        cost.set(0);
        menu.getSlot(menu.getResultSlot()).set(output);
        dark_matter$repair = true;
    }

    @Inject(method = "mayPickup", at = @At("HEAD"), cancellable = true)
    private void dark_matter$allowFreeRepair(Player player, boolean hasStack, CallbackInfoReturnable<Boolean> cir) {
        if (dark_matter$repair) {
            AnvilMenu menu = (AnvilMenu) (Object) this;
            cir.setReturnValue(menu.getSlot(menu.getResultSlot()).hasItem());
        }
    }
}
