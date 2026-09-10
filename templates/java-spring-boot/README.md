# java-spring-boot

Spring Boot + Gradle backend in `backend/` with JPA, Flyway and Actuator.
Listens on `PORT` (default 8080); health check is `GET /actuator/health`.
App Platform has no Java buildpack, so the Dockerfile is mandatory there.

## Scaffold (from the repo root)

```
curl https://start.spring.io/starter.zip -d type=gradle-project -d javaVersion=17 \
  -d dependencies=web,data-jpa,postgresql,h2,flyway,actuator,validation \
  -d baseDir=backend -d name=app -o app.zip && unzip app.zip && rm app.zip
cp <kit>/templates/java-spring-boot/{Dockerfile,.env.example} backend/
```

Initializr picks its current default Boot version (4.x). Pin `-d bootVersion=`
only to a value listed at `https://start.spring.io/metadata/client`.

Add to `src/main/resources/application.yml`:

```yaml
server.port: ${PORT:8080}
spring.datasource.url: ${SPRING_DATASOURCE_URL:jdbc:h2:mem:dev;MODE=PostgreSQL}
management.endpoint.health.show-details: always
```

First test (`src/test/java/.../HealthTest.java`): `@SpringBootTest` +
`@AutoConfigureMockMvc`, `GET /actuator/health` expects 200 and `$.status == "UP"`.

## Commands (run from `backend/`)

| Task | Command |
| --- | --- |
| run | `./gradlew bootRun --no-daemon` |
| test | `./gradlew test --no-daemon` |
| lint | `./gradlew check -x test --no-daemon` |
| build | `./gradlew bootJar --no-daemon` then `java -jar build/libs/*.jar` |
| image | `docker build -t api .` |

## Files in this folder

- `Dockerfile`: JDK build stage, JRE runtime, non-root user, HEALTHCHECK on Actuator. Copy to `backend/Dockerfile`.
- `ci-job.yml`: GitHub Actions job with a Postgres service container. Paste under `jobs:` in `.github/workflows/ci.yml`.
- `.env.example`: every variable the app reads. Copy to `backend/.env.example`; `.env` is git-ignored.
- `app-component.yaml`: App Platform `services:` entry with the JDBC bindings. Paste into `.do/app.yaml`.

## Conventions

- One `@ConfigurationProperties` class reads the environment; nothing else calls `System.getenv`.
- `SPRING_DATASOURCE_URL` must be JDBC-shaped. On App Platform bind
  `${db.JDBC_DATABASE_URL}`, not the plain `DATABASE_URL`.
- Flyway runs on boot from `src/main/resources/db/migration/V1__init.sql`; that is the migration story.
- Tests default to H2 in PostgreSQL mode; CI runs against real Postgres.
- Actuator shows the database check, so a down database fails the health probe.
