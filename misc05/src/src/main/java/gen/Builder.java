package gen;

import commands.CommandList;
import java.util.List;
import net.kyori.adventure.text.Component;
import net.kyori.adventure.text.format.NamedTextColor;
import net.minestom.server.MinecraftServer;
import net.minestom.server.coordinate.Pos;
import net.minestom.server.entity.GameMode;
import net.minestom.server.entity.Player;
import net.minestom.server.event.*;
import net.minestom.server.event.player.*;
import net.minestom.server.instance.InstanceContainer;
import net.minestom.server.instance.InstanceManager;
import net.minestom.server.instance.LightingChunk;
import net.minestom.server.instance.anvil.AnvilLoader;
import net.minestom.server.network.packet.server.play.PlayerInfoUpdatePacket;
import net.minestom.server.network.packet.server.play.PlayerInfoUpdatePacket.Entry;
import net.minestom.server.network.packet.server.play.TeamsPacket;
import net.minestom.server.scoreboard.Team;
import net.minestom.server.scoreboard.TeamManager;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import revxrsal.commands.minestom.MinestomLamp;

public class Builder {

    private static final Logger log = LoggerFactory.getLogger(Builder.class);
    private final MinecraftServer server;
    private final InstanceManager iM;
    private final GlobalEventHandler gEH;
    private final InstanceContainer iC;
    private final String TEAM_NAME = "hidden_nametag_team";

    public Builder() {
        server = MinecraftServer.init();
        createHiddenNametagTeam();
        iM = MinecraftServer.getInstanceManager();
        iC = iM.createInstanceContainer();
        iC.setChunkLoader(new AnvilLoader("/app/maps/ParkourSpiral"));
        iC.setChunkSupplier(LightingChunk::new);
        gEH = MinecraftServer.getGlobalEventHandler();
        addListeners();
        var lamp = MinestomLamp.builder().build();
        lamp.register(new CommandList(log));
    }

    private void createHiddenNametagTeam() {
        TeamManager teamManager = MinecraftServer.getTeamManager();
        Team team = teamManager.createTeam(TEAM_NAME);
        team.setNameTagVisibility(TeamsPacket.NameTagVisibility.NEVER);
        team.setCollisionRule(TeamsPacket.CollisionRule.NEVER);
        team.setTeamColor(NamedTextColor.WHITE);
        team.setPrefix(Component.text(""));
        team.setSuffix(Component.text(""));
    }

    private void addPlayerToTeam(Player player) {
        TeamManager teamManager = MinecraftServer.getTeamManager();
        Team team = teamManager.getTeam(TEAM_NAME);
        if (team != null) {
            team.addMember(player.getUsername());
        }
    }

    private void addListeners() {
        gEH.addListener(AsyncPlayerConfigurationEvent.class, event -> {
            final Player p = event.getPlayer();
            event.setSpawningInstance(iC);
            p.setDisplayName(Component.text("1337"));
            p.setGameMode(GameMode.ADVENTURE);
            p.setRespawnPoint(new Pos(0, 53, -126));

            Entry entry = new Entry(
                p.getUuid(),
                p.getUsername(),
                List.of(),
                true,
                p.getLatency(),
                p.getGameMode(),
                p.getDisplayName(),
                null,
                0
            );

            PlayerInfoUpdatePacket addPacket = new PlayerInfoUpdatePacket(
                PlayerInfoUpdatePacket.Action.ADD_PLAYER,
                entry
            );
            for (Player player : MinecraftServer.getConnectionManager()
                .getOnlinePlayers()) {
                if (player != p) {
                    player.sendPacket(addPacket);
                }
            }

            PlayerInfoUpdatePacket updatePacket = new PlayerInfoUpdatePacket(
                PlayerInfoUpdatePacket.Action.UPDATE_DISPLAY_NAME,
                entry
            );
            for (Player player : MinecraftServer.getConnectionManager()
                .getOnlinePlayers()) {
                if (player != p) {
                    player.sendPacket(updatePacket);
                }
            }

            addPlayerToTeam(p);
            log.info("{} joined the server", p.getUsername());
        });

        gEH.addListener(PlayerChatEvent.class, event -> {
            event.setCancelled(true);
        });
    }

    public boolean startServer() {
        try {
            server.start("0.0.0.0", 25565);
        } catch (Exception e) {
            return true;
        }
        return false;
    }
}
