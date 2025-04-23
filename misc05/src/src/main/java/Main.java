import gen.Builder;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Main {

    private static final Logger log = LoggerFactory.getLogger(Main.class);

    public static void main(String[] args) {
        Builder b = new Builder();
        if (b.startServer()) {
            log.info("Error while starting the server");
        } else {
            log.info("Server correctly started");
        }
    }
}
