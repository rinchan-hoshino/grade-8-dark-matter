#!/usr/bin/env python3
"""Generate the three API-specific Grade 8 Dark Matter source trees."""
from __future__ import annotations

import json
import shutil
import struct
import textwrap
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DISPLAY_NAME = "Grade 8 Dark Matter"
ITEM_NAME_ZH_CN = "8型暗物质"
MOD_VERSION = "1.0.1"
DESCRIPTION = "Repairs any damageable item in an anvil with compact Grade 8 Dark Matter."

VERSIONS = {
    "1.21.1": {
        "java": 21,
        "loom": "1.14.7",
        "moddev": "2.0.137",
        "fabric_loader": "0.19.2",
        "fabric_api": "0.116.12+1.21.1",
        "neo": "21.1.228",
        "mc_range": "[1.21.1,1.22)",
        "neo_range": "[21.1.0,)",
        "pack": {"pack_format": 34, "description": f"{DISPLAY_NAME} resources"},
    },
    "26.1.2": {
        "java": 25,
        "loom": "1.17.20",
        "moddev": "2.0.141",
        "fabric_loader": "0.19.3",
        "fabric_api": "0.155.2+26.1.2",
        "neo": "26.1.2.99",
        "mc_range": "[26.1.2,26.1.3)",
        "neo_range": "[26.1.2.99,26.1.3)",
        "pack": {"description": f"{DISPLAY_NAME} resources", "min_format": [84, 0], "max_format": [101, 1]},
    },
    "26.2": {
        "java": 25,
        "loom": "1.17.20",
        "moddev": "2.0.144",
        "fabric_loader": "0.19.4",
        "fabric_api": "0.158.0+26.2",
        "neo": "26.2.0.69",
        "mc_range": "[26.2,26.3)",
        "neo_range": "[26.2.0,)",
        "pack": {"description": f"{DISPLAY_NAME} resources", "min_format": [88, 0], "max_format": [107, 1]},
    },
}


def put(path: Path, content: str | bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, str):
        path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")
    else:
        path.write_bytes(content)


def json_put(path: Path, value: object) -> None:
    put(path, json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def png(width: int, height: int, rgba: bytes) -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    rows = b"".join(b"\0" + rgba[y * width * 4:(y + 1) * width * 4] for y in range(height))
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(rows, 9)) + chunk(b"IEND", b"")


def item_art(scale: int = 1) -> bytes:
    # Original deterministic pixel art: a dark violet singularity with a bright accretion ring.
    palette = {
        " ": (0, 0, 0, 0), "d": (20, 9, 35, 255), "m": (51, 18, 76, 255),
        "v": (98, 38, 142, 255), "p": (180, 88, 220, 255), "h": (245, 190, 255, 255),
    }
    rows = [
        "                ", "      vvv       ", "    vvpppvv     ", "   vpmmmmmpv    ",
        "  vpmdddddmpv   ", " vpmdddddddmpv  ", " vpdddddddddph  ", "vpddddddddddpv  ",
        "hpddddddddddpv  ", " vpdddddddddpv  ", " vpmdddddddmpv  ", "  vpmmdddmmph   ",
        "   vvmmmmmpv    ", "    vvpppvv     ", "      hvv       ", "                ",
    ]
    pixels = [palette[c] for row in rows for c in row]
    width = 16 * scale
    out = bytearray()
    for y in range(16):
        expanded = b"".join(bytes(pixels[y * 16 + x]) * scale for x in range(16))
        for _ in range(scale):
            out.extend(expanded)
    return png(width, width, bytes(out))


POLICY = """
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
"""

POLICY_TEST = """
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
"""

MIXIN = """
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
"""

STATIC_TEST = """
package dev.rinchan.darkmatter;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import org.junit.jupiter.api.Test;

final class SourceContractTest {
    private static final Path ROOT = Path.of(System.getProperty("generation.root"));

    @Test
    void identityAndRepairContractsArePresent() throws IOException {
        String all = sourceText();
        assertTrue(all.contains("dev.rinchan.darkmatter"));
        assertTrue(all.contains("dark_matter"));
        assertTrue(all.contains("copywithcount(1)"));
        assertTrue(all.contains("cost.set(0)"));
        assertTrue(all.contains("repairitemcountcost = consumed"));
        assertFalse(all.contains("wmf" + "_"));
        assertFalse(all.contains("sky" + "steel"));
        assertFalse(all.contains("aether" + "ic"));
        assertFalse(all.contains("relic" + "s"));
    }

    @Test
    void metadataHasExactPublicIdentityAndNoOptionalHardDependencies() throws IOException {
        String fabric = Files.readString(ROOT.resolve("fabric/src/main/resources/fabric.mod.json"));
        String neo = Files.readString(ROOT.resolve("neoforge/src/main/templates/META-INF/neoforge.mods.toml"));
        String properties = Files.readString(ROOT.resolve("gradle.properties"));
        String english = Files.readString(ROOT.resolve("common/src/main/resources/assets/dark_matter/lang/en_us.json"));
        String chinese = Files.readString(ROOT.resolve("common/src/main/resources/assets/dark_matter/lang/zh_cn.json"));
        assertTrue(fabric.contains("\\\"id\\\": \\\"dark_matter\\\""));
        assertTrue(fabric.contains("\\\"version\\\": \\\"${version}\\\""));
        assertTrue(fabric.contains("\\\"name\\\": \\\"Grade 8 Dark Matter\\\""));
        assertTrue(fabric.contains("\\\"license\\\": \\\"MIT\\\""));
        assertTrue(fabric.contains("\\\"minecraft\\\": \\\"=${minecraft_version}\\\""));
        assertTrue(neo.contains("modId=\\\"dark_matter\\\""));
        assertTrue(neo.contains("version=\\\"${mod_version}\\\""));
        assertTrue(neo.contains("displayName=\\\"Grade 8 Dark Matter\\\""));
        assertTrue(english.contains("\\\"item.dark_matter.dark_matter\\\": \\\"Grade 8 Dark Matter\\\""));
        assertTrue(chinese.contains("\\\"item.dark_matter.dark_matter\\\": \\\"8型暗物质\\\""));
        assertTrue(properties.contains("mod_version=1.0.1"));
        assertTrue(properties.contains("minecraft_version=${minecraft_version}"));
        assertFalse(fabric.contains("\\\"create\\\":"));
        assertFalse(fabric.contains("\\\"botania\\\":"));
        assertFalse(neo.contains("modId=\\\"create\\\""));
        assertFalse(neo.contains("modId=\\\"botania\\\""));
    }

    @Test
    void optionalRecipesAreNativeConditionedPerLoader() throws IOException {
        for (String loader : List.of("fabric", "neoforge")) {
            Path recipes = ROOT.resolve(loader + "/src/main/resources/data/dark_matter/recipe");
            String create = Files.readString(recipes.resolve("create_heated_mixing.json"));
            String botania = Files.readString(recipes.resolve("botania_alchemy.json"));
            assertTrue(create.contains("\\\"type\\\": \\\"create:mixing\\\""));
            assertTrue(create.contains("\\\"heat_requirement\\\": \\\"heated\\\""));
            assertTrue(botania.contains("\\\"type\\\": \\\"botania:mana_infusion\\\""));
            assertTrue(botania.contains("\\\"mana\\\": 6000"));
            String conditionKey = loader.equals("fabric") ? "fabric:load_conditions" : "neoforge:conditions";
            assertTrue(create.contains(conditionKey));
            assertTrue(botania.contains(conditionKey));
        }
    }

    @Test
    void armorersAndToolsmithsSellOneForOneAtBothExtractedTiers() throws IOException {
        Path trades = ROOT.resolve("common/src/main/resources/data/dark_matter/villager_trade");
        if (Files.isDirectory(trades)) {
            String novice = Files.readString(trades.resolve("emerald_dark_matter_novice.json"));
            String journeyman = Files.readString(trades.resolve("emerald_dark_matter_journeyman.json"));
            for (String trade : List.of(novice, journeyman)) {
                assertTrue(trade.contains("\\\"id\\\": \\\"minecraft:emerald\\\""));
                assertTrue(trade.contains("\\\"id\\\": \\\"dark_matter:dark_matter\\\""));
                assertTrue(trade.contains("\\\"count\\\": 1.0"));
            }
            for (String profession : List.of("armorer", "toolsmith")) {
                for (String level : List.of("level_1", "level_3")) {
                    assertTrue(Files.isRegularFile(ROOT.resolve("common/src/main/resources/data/dark_matter/tags/villager_trade/" + profession + "/" + level + ".json")));
                }
            }
        } else {
            String all = sourceText();
            assertTrue(all.contains("villagerprofession.armorer"));
            assertTrue(all.contains("villagerprofession.toolsmith"));
            assertTrue(all.contains("itemsforemeralds(item, 1, 1"));
            assertTrue(all.contains("itemsforemeralds(dark_matter.get(), 1, 1"));
        }
    }

    private static String sourceText() throws IOException {
        StringBuilder text = new StringBuilder();
        try (var paths = Files.walk(ROOT)) {
            for (Path path : paths.filter(p -> p.toString().endsWith(".java")).toList()) {
                if (!path.toString().contains("/policy/src/test/")) text.append(Files.readString(path));
            }
        }
        return text.toString().toLowerCase();
    }
}
"""


def recipe(condition: str, kind: str) -> dict:
    if condition == "fabric":
        gate = {"fabric:load_conditions": [{"condition": "fabric:all_mods_loaded", "values": [kind]}]}
    else:
        gate = {"neoforge:conditions": [{"type": "neoforge:mod_loaded", "modid": kind}]}
    if kind == "create":
        body = {
            "type": "create:mixing",
            "heat_requirement": "heated",
            "ingredients": [
                {"item": "create:crushed_obsidian"},
                {"item": "minecraft:coal"},
                {"item": "minecraft:amethyst_shard"},
            ],
            "results": [{"count": 1, "id": "dark_matter:dark_matter"}],
        }
    else:
        body = {
            "type": "botania:mana_infusion",
            "catalyst": {"type": "botania:block", "block": "botania:alchemy_catalyst"},
            "input": {"item": "minecraft:obsidian"},
            "mana": 6000,
            "output": {"count": 1, "id": "dark_matter:dark_matter"},
        }
    return gate | body


def generate(version: str, cfg: dict) -> None:
    root = ROOT / "versions" / version
    wrapper_paths = ("gradlew", "gradlew.bat", "gradle/wrapper/gradle-wrapper.jar", "gradle/wrapper/gradle-wrapper.properties")
    wrapper_files = {name: (root / name).read_bytes() for name in wrapper_paths}
    if root.exists():
        shutil.rmtree(root)
    for name, content in wrapper_files.items():
        put(root / name, content)
    (root / "gradlew").chmod(0o755)

    put(root / "settings.gradle", f"""
        pluginManagement {{
            resolutionStrategy {{
                eachPlugin {{
                    if (requested.id.id == 'net.fabricmc.fabric-loom') {{
                        useModule("net.fabricmc:fabric-loom:${{requested.version}}")
                    }}
                }}
            }}
            repositories {{
                gradlePluginPortal()
                maven {{ url = 'https://maven.fabricmc.net/' }}
                maven {{ url = 'https://maven.neoforged.net/releases' }}
            }}
        }}
        rootProject.name = 'dark-matter-{version}'
        include 'policy', 'fabric', 'neoforge'
    """)
    loom_plugin = "fabric-loom" if version == "1.21.1" else "net.fabricmc.fabric-loom"
    put(root / "build.gradle", f"""
        plugins {{
            id '{loom_plugin}' version '{cfg['loom']}' apply false
            id 'net.neoforged.moddev' version '{cfg['moddev']}' apply false
        }}
        subprojects {{
            group = rootProject.mod_group_id
            version = rootProject.mod_version
            repositories {{
                mavenCentral()
                maven {{ url = 'https://maven.fabricmc.net/' }}
                maven {{ url = 'https://maven.neoforged.net/releases' }}
            }}
            plugins.withType(JavaPlugin).configureEach {{
                java.toolchain.languageVersion = JavaLanguageVersion.of(rootProject.java_version as int)
                tasks.withType(JavaCompile).configureEach {{ options.encoding = 'UTF-8' }}
            }}
        }}
    """)
    put(root / "gradle.properties", f"""
        org.gradle.jvmargs=-Xmx2G
        org.gradle.daemon=false
        org.gradle.parallel=true
        org.gradle.caching=true
        org.gradle.configuration-cache=true

        minecraft_version={version}
        minecraft_version_range={cfg['mc_range']}
        java_version={cfg['java']}
        fabric_loader_version={cfg['fabric_loader']}
        fabric_api_version={cfg['fabric_api']}
        neo_version={cfg['neo']}
        neo_version_range={cfg['neo_range']}
        loader_version_range={'[4,)' if version == '1.21.1' else '[3,)' if version == '26.1.2' else '[11,)'}

        mod_id=dark_matter
        mod_name={DISPLAY_NAME}
        mod_license=MIT
        mod_version={MOD_VERSION}
        mod_group_id=dev.rinchan
        mod_authors=RinChan
        mod_description={DESCRIPTION}
    """)

    put(root / "policy/build.gradle", """
        plugins { id 'java-library' }
        sourceSets.main.java {
            srcDir rootProject.file('common/src/main/java')
            include 'dev/rinchan/darkmatter/DarkMatterRepairPolicy.java'
        }
        sourceSets.test.java.srcDir rootProject.file('../../tools/test-fixtures/java')
        dependencies {
            testImplementation platform('org.junit:junit-bom:5.11.4')
            testImplementation 'org.junit.jupiter:junit-jupiter'
            testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
        }
        tasks.named('test', Test) {
            useJUnitPlatform()
            systemProperty 'generation.root', rootProject.projectDir.absolutePath
        }
    """)
    put(root / "policy/src/test/java/dev/rinchan/darkmatter/DarkMatterRepairPolicyTest.java", POLICY_TEST)
    put(root / "policy/src/test/java/dev/rinchan/darkmatter/SourceContractTest.java", STATIC_TEST.replace("${minecraft_version}", version))

    identifier = "ResourceLocation.fromNamespaceAndPath" if version == "1.21.1" else "Identifier.fromNamespaceAndPath"
    identifier_import = "net.minecraft.resources.ResourceLocation" if version == "1.21.1" else "net.minecraft.resources.Identifier"
    identifier_type = "ResourceLocation" if version == "1.21.1" else "Identifier"
    put(root / "common/src/main/java/dev/rinchan/darkmatter/DarkMatter.java", f"""
        package dev.rinchan.darkmatter;

        import java.util.Objects;
        import java.util.function.Supplier;
        import {identifier_import};
        import net.minecraft.world.item.Item;
        import net.minecraft.world.item.ItemStack;

        public final class DarkMatter {{
            public static final String MOD_ID = "dark_matter";
            public static final {identifier_type} ITEM_ID = {identifier}(MOD_ID, "dark_matter");
            private static Supplier<? extends Item> item;

            private DarkMatter() {{}}

            public static void initialize(Supplier<? extends Item> registeredItem) {{
                if (item != null) throw new IllegalStateException("Grade 8 Dark Matter already initialized");
                item = Objects.requireNonNull(registeredItem);
            }}

            public static boolean isDarkMatter(ItemStack stack) {{
                return item != null && stack.is(item.get());
            }}
        }}
    """)
    put(root / "common/src/main/java/dev/rinchan/darkmatter/DarkMatterRepairPolicy.java", POLICY)
    put(root / "common/src/main/java/dev/rinchan/darkmatter/mixin/AnvilMenuMixin.java", MIXIN)
    json_put(root / "common/src/main/resources/dark_matter.mixins.json", {
        "required": True, "minVersion": "0.8", "package": "dev.rinchan.darkmatter.mixin",
        "compatibilityLevel": "JAVA_21" if cfg["java"] == 21 else "JAVA_25",
        "mixins": ["AnvilMenuMixin"], "injectors": {"defaultRequire": 1},
    })
    json_put(root / "common/src/main/resources/pack.mcmeta", {"pack": cfg["pack"]})
    json_put(root / "common/src/main/resources/assets/dark_matter/lang/en_us.json", {"item.dark_matter.dark_matter": DISPLAY_NAME})
    json_put(root / "common/src/main/resources/assets/dark_matter/lang/zh_cn.json", {"item.dark_matter.dark_matter": ITEM_NAME_ZH_CN})
    json_put(root / "common/src/main/resources/assets/dark_matter/models/item/dark_matter.json", {"parent": "minecraft:item/generated", "textures": {"layer0": "dark_matter:item/dark_matter"}})
    if version != "1.21.1":
        json_put(root / "common/src/main/resources/assets/dark_matter/items/dark_matter.json", {"model": {"type": "minecraft:model", "model": "dark_matter:item/dark_matter"}})
    put(root / "common/src/main/resources/assets/dark_matter/textures/item/dark_matter.png", item_art())
    put(root / "common/src/main/resources/assets/dark_matter/icon.png", item_art(8))

    mappings = "mappings loom.officialMojangMappings()" if version == "1.21.1" else ""
    fabric_plugin = "fabric-loom" if version == "1.21.1" else "net.fabricmc.fabric-loom"
    fabric_dep = "modImplementation" if version == "1.21.1" else "implementation"
    put(root / "fabric/build.gradle", f"""
        plugins {{ id 'java-library'; id '{fabric_plugin}' }}
        def modVersion = rootProject.mod_version
        def licenseFile = rootProject.file('../../LICENSE')
        base {{ archivesName = "dark_matter-fabric-{version}" }}
        sourceSets.main.java.srcDir rootProject.file('common/src/main/java')
        sourceSets.main.resources.srcDir rootProject.file('common/src/main/resources')
        dependencies {{
            minecraft "com.mojang:minecraft:${{rootProject.minecraft_version}}"
            {mappings}
            {fabric_dep} "net.fabricmc:fabric-loader:${{rootProject.fabric_loader_version}}"
            {fabric_dep} "net.fabricmc.fabric-api:fabric-api:${{rootProject.fabric_api_version}}"
        }}
        processResources {{
            inputs.property 'version', modVersion
            filesMatching('fabric.mod.json') {{ expand(version: modVersion) }}
        }}
        tasks.withType(Jar).configureEach {{
            from(licenseFile) {{ into 'META-INF'; rename {{ 'LICENSE_dark_matter' }} }}
        }}
    """)
    trade_call = "registerTrades(item);" if version == "1.21.1" else ""
    fabric_entry = f"""
        package dev.rinchan.darkmatter.fabric;

        import dev.rinchan.darkmatter.DarkMatter;
        import net.fabricmc.api.ModInitializer;
        import net.minecraft.core.Registry;
        import net.minecraft.core.registries.BuiltInRegistries;
        import net.minecraft.world.item.Item;

        public final class DarkMatterFabric implements ModInitializer {{
            @Override
            public void onInitialize() {{
                Item item = Registry.register(BuiltInRegistries.ITEM, DarkMatter.ITEM_ID, new Item(new Item.Properties()));
                DarkMatter.initialize(() -> item);
                {trade_call}
            }}
    """
    if version == "1.21.1":
        fabric_entry += """
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
        """
    fabric_entry += "}\n"
    put(root / "fabric/src/main/java/dev/rinchan/darkmatter/fabric/DarkMatterFabric.java", fabric_entry)
    json_put(root / "fabric/src/main/resources/fabric.mod.json", {
        "schemaVersion": 1, "id": "dark_matter", "version": "${version}", "name": DISPLAY_NAME,
        "description": DESCRIPTION,
        "authors": ["RinChan"], "license": "MIT", "icon": "assets/dark_matter/icon.png", "environment": "*",
        "entrypoints": {"main": ["dev.rinchan.darkmatter.fabric.DarkMatterFabric"]},
        "mixins": ["dark_matter.mixins.json"],
        "depends": {"fabricloader": f">={cfg['fabric_loader']}", "minecraft": f"={version}", "java": f">={cfg['java']}", "fabric-api": "*"},
    })

    put(root / "neoforge/build.gradle", f"""
        plugins {{ id 'java-library'; id 'net.neoforged.moddev' }}
        def modVersion = rootProject.mod_version
        def minecraftVersionRange = rootProject.minecraft_version_range
        def neoVersionRange = rootProject.neo_version_range
        def loaderVersionRange = rootProject.loader_version_range
        def licenseFile = rootProject.file('../../LICENSE')
        base {{ archivesName = "dark_matter-neoforge-{version}" }}
        sourceSets.main.java.srcDir rootProject.file('common/src/main/java')
        sourceSets.main.resources.srcDir rootProject.file('common/src/main/resources')
        sourceSets.main.resources.srcDir tasks.register('generateModMetadata', ProcessResources) {{
            def properties = [mod_version: modVersion, minecraft_version_range: minecraftVersionRange,
                    neo_version_range: neoVersionRange, loader_version_range: loaderVersionRange]
            inputs.properties properties
            expand properties
            from 'src/main/templates'
            into layout.buildDirectory.dir('generated/sources/modMetadata')
        }}
        neoForge {{
            version = rootProject.neo_version
            mods {{ dark_matter {{ sourceSet(sourceSets.main) }} }}
        }}
        neoForge.ideSyncTask tasks.named('generateModMetadata')
        tasks.withType(Jar).configureEach {{
            from(licenseFile) {{ into 'META-INF'; rename {{ 'LICENSE_dark_matter' }} }}
        }}
    """)
    neo_entry = """
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
    """
    if version == "1.21.1":
        neo_entry += """
                net.neoforged.neoforge.common.NeoForge.EVENT_BUS.addListener(DarkMatterNeoForge::onVillagerTrades);
            }

            private static void onVillagerTrades(net.neoforged.neoforge.event.village.VillagerTradesEvent event) {
                if (event.getType() != net.minecraft.world.entity.npc.VillagerProfession.ARMORER
                        && event.getType() != net.minecraft.world.entity.npc.VillagerProfession.TOOLSMITH) return;
                event.getTrades().get(1).add(new net.minecraft.world.entity.npc.VillagerTrades.ItemsForEmeralds(DARK_MATTER.get(), 1, 1, 16, 2));
                event.getTrades().get(3).add(new net.minecraft.world.entity.npc.VillagerTrades.ItemsForEmeralds(DARK_MATTER.get(), 1, 1, 24, 10));
            }
        """
    else:
        neo_entry += """
            }
        """
    neo_entry += "}\n"
    put(root / "neoforge/src/main/java/dev/rinchan/darkmatter/neoforge/DarkMatterNeoForge.java", neo_entry)
    put(root / "neoforge/src/main/templates/META-INF/neoforge.mods.toml", f"""
        modLoader="javafml"
        loaderVersion="${{loader_version_range}}"
        license="MIT"
        [[mods]]
        modId="dark_matter"
        version="${{mod_version}}"
        displayName="{DISPLAY_NAME}"
        authors="RinChan"
        description='''{DESCRIPTION}'''
        logoFile="assets/dark_matter/icon.png"
        [[mixins]]
        config="dark_matter.mixins.json"
        [[dependencies.dark_matter]]
        modId="neoforge"
        type="required"
        versionRange="${{neo_version_range}}"
        ordering="NONE"
        side="BOTH"
        [[dependencies.dark_matter]]
        modId="minecraft"
        type="required"
        versionRange="${{minecraft_version_range}}"
        ordering="NONE"
        side="BOTH"
    """)

    for loader in ("fabric", "neoforge"):
        recipes = root / loader / "src/main/resources/data/dark_matter/recipe"
        json_put(recipes / "create_heated_mixing.json", recipe(loader, "create"))
        json_put(recipes / "botania_alchemy.json", recipe(loader, "botania"))

    if version != "1.21.1":
        trade_dir = root / "common/src/main/resources/data/dark_matter/villager_trade"
        json_put(trade_dir / "emerald_dark_matter_novice.json", {
            "wants": {"id": "minecraft:emerald", "count": 1.0}, "gives": {"id": "dark_matter:dark_matter"},
            "max_uses": 16.0, "xp": 2.0, "reputation_discount": 0.05,
        })
        json_put(trade_dir / "emerald_dark_matter_journeyman.json", {
            "wants": {"id": "minecraft:emerald", "count": 1.0}, "gives": {"id": "dark_matter:dark_matter"},
            "max_uses": 24.0, "xp": 10.0, "reputation_discount": 0.05,
        })
        for profession in ("armorer", "toolsmith"):
            for level, trade in (("level_1", "novice"), ("level_3", "journeyman")):
                json_put(root / f"common/src/main/resources/data/dark_matter/tags/villager_trade/{profession}/{level}.json", {
                    "replace": False, "values": [f"dark_matter:emerald_dark_matter_{trade}"]
                })


for game_version, config in VERSIONS.items():
    generate(game_version, config)
print("generated:", ", ".join(VERSIONS))
