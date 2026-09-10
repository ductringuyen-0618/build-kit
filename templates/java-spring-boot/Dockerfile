# syntax=docker/dockerfile:1.6
# Spring Boot service. Copy to backend/Dockerfile and build from that folder.
# Stage 1 builds the jar with the Gradle wrapper; stage 2 is a JRE-only
# non-root runtime. Required on App Platform (no Java buildpack).

FROM eclipse-temurin:17-jdk AS builder
# CHANGE: 17 -> the javaVersion used when scaffolding (also in ci-job.yml)
WORKDIR /app
COPY gradle gradle
COPY gradlew build.gradle settings.gradle ./
# CHANGE: build.gradle.kts settings.gradle.kts if the project uses Kotlin DSL
RUN chmod +x gradlew && ./gradlew dependencies --no-daemon > /dev/null
COPY src src
RUN ./gradlew bootJar --no-daemon

FROM eclipse-temurin:17-jre
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && addgroup --system spring && adduser --system spring --ingroup spring
COPY --from=builder /app/build/libs/*.jar app.jar
USER spring:spring
ENV PORT=8080 JAVA_OPTS="-Xmx512m"
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -fsS "http://127.0.0.1:${PORT}/actuator/health" || exit 1
EXPOSE 8080
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
