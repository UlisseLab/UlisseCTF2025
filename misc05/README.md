# M1n3ctf

|         |                                |
| ------- | ------------------------------ |
| Authors | Francesco Rizzello <@cestello> |
| Points  | 500                            |
| Tags    | misc,minecraft                 |

## Challenge Description

We love custom minecraft servers, _#ДоCвидания_

Server: mc.challs.ulisse.ovh 25565

## Overview

We’ve obtained what appears to be the source code for the Minecraft server we need to connect to.

## Source Code Analysis

The server is written in Java and uses the Minestom server framework.

Notably, the file `commands/CommandList.java` defines the commands available to players. However, all function and variable names are written in Cyrillic, so the first step is to rename them to something more readable.

```java
private String ген() {
    for (int i = 0; i < iterations; ++i) {
        int p = random.nextInt((int) Math.pow(104, 3));
    }
    // Iterates 70605 times to "mix" the random generator

    String result = new String("");
    while (result.length() != LENGTH) {
        int p = module.apply(random.nextInt((int) Math.pow(42, 5)), MAX + 1);
        result = p >= MIN && p <= MAX ? result + (char) p : result;
    }
    // Generates a 12-character random string

    boolean[] used = new boolean[12];
    for (int i = 0; i < LENGTH; ++i) {
        used[i] = false;
    }
    for (int i = 0; i < LENGTH; ++i) {
        int p = module.apply(random.nextInt((int) Math.pow(1337, 2)), LENGTH);
        if (used[p]) {
            i--;
            continue;
        }
        order[i] = p;
        used[p] = true;
    }
    // Creates a random permutation of the indices [0, 11]

    return result;
    // This is the admin string
}
```

Once that’s done, we can see that the server uses a random number generator to create a 12-character string. This string is then used to determine if a player is an admin by checking whether their username contains the generated string.

Next, we analyze the check function by changing the names to something more readable:

```java
private boolean check(String playerName) {
    if (playerName.length() < 12) return false;

    String temp = new String("");
    for (int i = 0; i < 12; ++i) {
        // Picks characters from the player's name using the randomized indices
        temp += playerName.charAt(randomIndices[i]);
    }

    if (temp.contains(admin)) return true;

    // The use of `contains` allows multiple valid usernames
    // Example: if admin = fabrizio, then fabrizio, 12fabrizio12, etc., are valid

    return false;
}
```

We then observe that the server's start time is used as the seed for the random number generator, and we can retrieve this timestamp using the `/info` command:

```java
@Command("info")
public void info(MinestomCommandActor actor) {
    StringBuilder sb = new StringBuilder()
        .append("Name of the server: M1n3ctf\n")
        .append("Creators: drcesty, matafino\n")
        .append("Started at ")
        .append(new java.util.Date(f * 1000)) // <- this is the required timestamp
        ...

    actor.reply(sb.toString());
}
```

By re-implementing the logic from the `ген()` function and extracting the timestamp via the `/info` command, we can reconstruct the admin username.

> **NOTE:** During the CTF, we had to apply a hotfix because the server used a different timezone than our local environment.
> The server ran in UTC+0, while we were in UTC+2. This caused discrepancies in the generated string. We resolved this by setting the `TZ=Europe/Rome` environment variable in the Docker container.

## Script

```java
import java.util.Random;

public class Main {
    public static void main(String args[]) {
        long timestamp = 1743174172L;
        Random random = new Random(timestamp); // Change timestamp accordingly
        int len = 12;
        int mixIterations = 70605;
        int a = 97;
        int z = 122;

        for (int i = 0; i < mixIterations; ++i) {
            int p = random.nextInt((int) Math.pow(104, 3));
        }

        String admin = new String("");
        while (admin.length() != len) {
            int p = random.nextInt((int) Math.pow(42, 5)) % (z + 1);
            admin = p >= a && p <= z ? admin + (char) p : admin;
        }

        boolean[] used = new boolean[12];
        for (int i = 0; i < len; ++i) {
            used[i] = false;
        }

        int[] indices = new int[12];
        for (int i = 0; i < len; ++i) {
            int p = random.nextInt((int) Math.pow(1337, 2)) % len;
            if (used[p]) {
                i--;
                continue;
            }
            indices[i] = p;
            used[p] = true;
        }

        char[] result = new char[12];
        for (int i = 0; i < len; ++i) {
            result[indices[i]] = admin.charAt(i);
        }

        System.out.print(String.valueOf(result) + "????\n");
    }
}
```
