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
        assertTrue(fabric.contains("\"id\": \"dark_matter\""));
        assertTrue(fabric.contains("\"version\": \"${version}\""));
        assertTrue(fabric.contains("\"name\": \"Grade 8 Dark Matter\""));
        assertTrue(fabric.contains("\"license\": \"MIT\""));
        assertTrue(fabric.contains("\"minecraft\": \"=26.1.2\""));
        assertTrue(neo.contains("modId=\"dark_matter\""));
        assertTrue(neo.contains("version=\"${mod_version}\""));
        assertTrue(neo.contains("displayName=\"Grade 8 Dark Matter\""));
        assertTrue(english.contains("\"item.dark_matter.dark_matter\": \"Grade 8 Dark Matter\""));
        assertTrue(chinese.contains("\"item.dark_matter.dark_matter\": \"8型暗物质\""));
        assertTrue(properties.contains("mod_version=1.0.1"));
        assertTrue(properties.contains("minecraft_version=26.1.2"));
        assertFalse(fabric.contains("\"create\":"));
        assertFalse(fabric.contains("\"botania\":"));
        assertFalse(neo.contains("modId=\"create\""));
        assertFalse(neo.contains("modId=\"botania\""));
    }

    @Test
    void optionalRecipesAreNativeConditionedPerLoader() throws IOException {
        for (String loader : List.of("fabric", "neoforge")) {
            Path recipes = ROOT.resolve(loader + "/src/main/resources/data/dark_matter/recipe");
            String create = Files.readString(recipes.resolve("create_heated_mixing.json"));
            String botania = Files.readString(recipes.resolve("botania_alchemy.json"));
            assertTrue(create.contains("\"type\": \"create:mixing\""));
            assertTrue(create.contains("\"heat_requirement\": \"heated\""));
            assertTrue(botania.contains("\"type\": \"botania:mana_infusion\""));
            assertTrue(botania.contains("\"mana\": 6000"));
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
                assertTrue(trade.contains("\"id\": \"minecraft:emerald\""));
                assertTrue(trade.contains("\"id\": \"dark_matter:dark_matter\""));
                assertTrue(trade.contains("\"count\": 1.0"));
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
