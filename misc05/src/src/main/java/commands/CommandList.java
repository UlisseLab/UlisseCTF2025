package commands;

import java.time.Instant;
import java.util.Random;
import net.minestom.server.entity.Player;
import org.slf4j.Logger;
import revxrsal.commands.annotation.Command;
import revxrsal.commands.minestom.actor.MinestomCommandActor;

class модуль {

    static int применять(int a, int b) {
        return a % b;
    }
}

public class CommandList {

    private final Logger log;
    private final int РИЧАРД = 12;
    private final int мороженое = 70605;
    private final int минимо = 97;
    private final int Массимо = 122;
    private long f;
    private final Random случайный;
    private String АДМИН;
    private int[] ординировать = new int[12];

    public CommandList(final Logger log) {
        this.log = log;
        АДМИН = new String("");
        var x = Instant.now().toEpochMilli() / 1000;
        f = ((long) x);
        случайный = new Random(x);
        System.out.println("x: " + x);
        АДМИН = ген();
    }

    private String ген() {
        for (int тот = 0; тот < мороженое; ++тот) {
            int p = случайный.nextInt((int) Math.pow(104, 3));
        }
        String температура = new String("");
        while (температура.length() != РИЧАРД) {
            int p = модуль.применять(
                случайный.nextInt((int) Math.pow(42, 5)),
                Массимо + 1
            );
            температура = p >= минимо && p <= Массимо
                ? температура + (char) p
                : температура;
        }
        boolean[] подарок = new boolean[12];
        for (int тот = 0; тот < РИЧАРД; ++тот) {
            подарок[тот] = false;
        }
        for (int тот = 0; тот < РИЧАРД; ++тот) {
            int p = модуль.применять(
                случайный.nextInt((int) Math.pow(1337, 2)),
                РИЧАРД
            );
            if (подарок[p]) {
                тот--;
                continue;
            }
            ординировать[тот] = p;
            подарок[p] = true;
        }

        return температура;
    }

    @Command("info")
    public void info(MinestomCommandActor actor) {
        StringBuilder sb = new StringBuilder()
            .append("Name of the server: M1n3ctf\n")
            .append("Creators: drcesty, matafino\n")
            .append("Started at ")
            .append(new java.util.Date(f * 1000))
            .append(" GMT+02:00\n")
            .append("Version: 1.20.3\n")
            .append("Useless: Highlander\n")
            .append(
                "Favorite quote:\nSe ni' mondo esistesse un po' di bene\ne ognun si honsiderasse suo fratello\nci sarebbe meno pensieri e meno pene\ne il mondo ne sarebbe assai più bello\n"
            );

        actor.reply(sb.toString());
    }

    @Command("echo")
    public void echo(MinestomCommandActor actor, String stringa) {
        actor.reply("you said " + stringa + "!");
    }

    @Command("secret")
    public void secret(MinestomCommandActor actor) {
        if (actor.isPlayer()) {
            String имя = new String(actor.name());
            if (check(имя)) {
                log.info(имя + " !!!");
                actor.reply(System.getenv("NODONTGETMYSECRET"));
            } else {
                actor.reply("YOUWILLNOTGETMYSECRET!");
            }
        }
    }

    private boolean check(String имя) {
        if (имя.length() < 12) return false;
        String температура = new String("");
        for (int тот = 0; тот < РИЧАРД; ++тот) {
            температура += имя.charAt(ординировать[тот]);
        }
        if (температура.contains(АДМИН)) return true;
        return false;
    }
}
