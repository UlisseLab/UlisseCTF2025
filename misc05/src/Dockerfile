FROM gradle:jdk21-alpine@sha256:3dd41aff1bf0421db1a094dbedd79ea18a55ec47e4b26f5d73625c7d0c88aa17 AS build
WORKDIR /app

COPY build.gradle ./
RUN gradle dependencies --no-daemon

COPY src ./src
RUN gradle build --no-daemon

FROM eclipse-temurin:21-jre-alpine@sha256:4e9ab608d97796571b1d5bbcd1c9f430a89a5f03fe5aa6c093888ceb6756c502
WORKDIR /app
COPY --from=build /app/build/libs/*.jar /app/server.jar
COPY ParkourSpiral /app/maps/ParkourSpiral

EXPOSE 25565
ENTRYPOINT ["java", "-jar", "server.jar"]
