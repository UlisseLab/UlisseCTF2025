import java.time.Instant;
import java.util.Random;

public class Main {

    public static void main(String args[]) {
        long timestamp = 1743706403;
        Random random = new Random(timestamp); //cambiare il timestamp
        int len = 12;
        int giri = 70605;
        int a = 97;
        int z = 122;
        for (int i = 0; i < giri; ++i) {
            int p = random.nextInt((int) Math.pow(104, 3));
        }
        String admin = new String("");
        while (admin.length() != len) {
            int p = random.nextInt((int) Math.pow(42, 5)) % (z + 1);
            admin = p >= a && p <= z ? admin + (char) p : admin;
        }
        boolean[] flag = new boolean[12];
        for (int i = 0; i < len; ++i) {
            flag[i] = false;
        }
        int[] array_numeri = new int[12];
        for (int i = 0; i < len; ++i) {
            int p = random.nextInt((int) Math.pow(1337, 2)) % len;
            if (flag[p]) {
                i--;
                continue;
            }
            array_numeri[i] = p;
            flag[p] = true;
        }
        char[] ans = new char[12];
        for (int i = 0; i < len; ++i) {
            ans[array_numeri[i]] = admin.charAt(i);
        }
        // i punti interrogativi per definire qualsiasi carattere
        System.out.print(String.valueOf(ans) + "????\n");
    }
}
