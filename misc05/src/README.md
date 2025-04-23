# Challenge

## Avvio

Per avviare il progetto:

```sh
docker compose up --build
```

## Configurazione

Se utilizzi IntelliJ modifica la riga 30 nella classe Builder:

```java
iC.setChunkLoader(new AnvilLoader("./ParkourSpiral"));
```

Se invece stai usando Docker
```java
iC.setChunkLoader(new AnvilLoader("/app/maps/ParkourSpiral"));
```
