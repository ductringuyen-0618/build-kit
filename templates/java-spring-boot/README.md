# Backend skeleton: Spring Boot 3 + Gradle

Pattern from salon-hub (Spring Boot 3.4, Java 17, JPA, Flyway, Actuator,
Postgres). Scaffold with the start.spring.io command in
`playbook/stack-picker.md`, then copy the four files in this folder.

## Layout

```
backend/
  build.gradle, settings.gradle, gradlew, gradle/
  src/main/java/<pkg>/
    Application.java
    config/AppProperties.java       @ConfigurationProperties: the only reader of env
    api/<Resource>Controller.java
    domain/<Resource>.java, <Resource>Repository.java
    service/<Resource>Service.java
  src/main/resources/
    application.yml                 server.port=${PORT:8080}, datasource from env
    db/migration/V1__init.sql       Flyway
  src/test/java/<pkg>/
    HealthTest.java                 @SpringBootTest + MockMvc on /actuator/health
  Dockerfile
```

## Rules

- `server.port: ${PORT:8080}` so App Platform's `PORT` and the Dockerfile
  agree.
- `spring.datasource.url: ${SPRING_DATASOURCE_URL:jdbc:h2:mem:dev}`; in
  the deploy bind it to `${db.JDBC_DATABASE_URL}`. Do not pass the plain
  `DATABASE_URL`; it is not JDBC-shaped.
- Actuator health at `/actuator/health` with `management.endpoint.health.show-details: always`
  so the database check is visible.
- Flyway runs on boot; that is the migration story. Say "Flyway on boot,
  pre-deploy job next" in the demo.
- Tests use the `test` profile with H2 or a Postgres service container in
  CI (salon-hub uses the container).

## Commands

```
./gradlew test --no-daemon
./gradlew bootJar --no-daemon
java -jar build/libs/*.jar
curl localhost:8080/actuator/health
```
