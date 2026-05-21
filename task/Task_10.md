# Task 10 - Docker Development Deployment

## Current deployment phase

The goal of this task is to prepare a Docker-based local deployment for the implemented Participium application.

Its purpose is to run the existing backend, frontend, and database together through Docker Compose, while keeping the application configurable through environment variables.

This is a local development deployment task. Do not prepare a production release, a compiled frontend distribution, or a hardened production container setup.

## Deliverables to produce

Complete the following deliverables:

- **`../docker/backend.Dockerfile`**
- **`../docker/frontend.Dockerfile`**
- **`../docker/docker-compose.yml`**

The application source code should remain unchanged. The expected solution should configure the existing application through Docker and environment variables.

## Baseline scope reference

Work on the implemented application:

- **`../src/backend/`**
- **`../src/frontend/`**

The Docker files are intentionally stored in a separate directory:

- **`../docker/`**

This means that the Docker build context and the Dockerfile paths must be configured carefully. The Dockerfiles and the source code are not in the same directory.

In the Compose file the configuration should define the build context and the Dockerfile path for the services to be built:

```yaml
build:
  context: path/to/root/folder
  dockerfile: path/to/my.Dockerfile
```

The `context` decides which files Docker can see during the build. The `dockerfile` path is resolved inside that context. If these paths are wrong, Docker may fail to copy the application source or may accidentally send the wrong directory to the Docker daemon.

## Expected services

The Docker configuration must start:

- a Flask backend container, built from the project backend Dockerfile;
- a Vite frontend container, built from the project frontend Dockerfile;
- a MySQL 8 database container, started from the official MySQL image.

With the default Docker configuration:

- backend API: **`http://localhost:5050/api/v1`**
- backend Swagger UI: **`http://localhost:5050/apidocs/`**
- frontend application: **`http://localhost:5173`**
- MySQL database: **`localhost:3306`**

---

## 1) Configuration Rules

### Use environment variables from Compose

The Docker configuration must use environment variables that are already supported by the application.

Do not change backend or frontend source code only to make Docker work if an existing environment variable can express the required configuration.

Do not copy local environment files into the container images. In particular, files such as:

- `src/backend/.env`
- `src/frontend/.env`

must not become part of the Docker image configuration.

The Docker Compose file is the place where this task configures the runtime environment. The `.dockerignore` file excludes both the aforementioned local `.env` files, virtual environments, cache directories, `node_modules`, and other machine-specific files from the build context.

### Backend database configuration

The backend must use MySQL through `DATABASE_URL`.

Default value:

```text
DATABASE_URL=mysql+pymysql://participium:participium_password@database:3306/participium?autocommit=true
```

The hostname `database` is the Compose service name. It is resolved inside the Docker network and is different from `localhost` on the host machine.

The MySQL URL enables PyMySQL autocommit. This keeps seed data and normal application writes visible from other MySQL sessions, including verification commands executed with `docker exec`.

### Frontend backend configuration

The frontend must receive the backend addresses through Vite environment variables:

```text
VITE_API_BASE_URL=http://localhost:5050/api/v1
VITE_BACKEND_BASE_URL=http://localhost:5050
```

These are host-facing URLs because the frontend code runs in the user's browser. Even though the frontend container is inside the Compose network, the browser reaches the backend through the host port published by Docker Compose.

### Use development servers

The Dockerfiles should run development entry points:

- backend: `flask --app wsgi:app run`
- frontend: `npm run dev`

Do not introduce a production web server, a static frontend build, or a release-oriented packaging step for this task.

The backend development server must run without request threads:

```text
--without-threads
```

The current backend database module keeps one process-level SQLAlchemy connection. Running the Flask development server with multiple request threads can make concurrent requests share the same PyMySQL connection, which is not safe. This Docker setup should keep the existing code unchanged and constrain the development server accordingly.

---

## 2) Docker Files

### Backend image

Create a backend Dockerfile that:

- starts from a Python base image;
- sets `/usr/src/app` as the working directory;
- installs dependencies from `src/backend/requirements.txt`;
- copies the backend source from the build context;
- exposes the backend container port;
- starts the application with Flask CLI on the configured host and port;
- disables threaded request handling for compatibility with the existing database connection lifecycle.

### Frontend image

Create a frontend Dockerfile that:

- starts from a Node.js LTS base image;
- sets `/usr/src/app` as the working directory;
- installs dependencies from `src/frontend/package-lock.json`;
- copies the frontend source from the build context;
- exposes the frontend container port;
- starts Vite on `0.0.0.0`.

### Build context attention

Because the Dockerfiles are under `../docker/` and the source folders are under `../src/`, every `COPY` instruction must be written relative to the build context, not relative to the Dockerfile folder.

For example, if the build context is the repository root, this is valid:

```dockerfile
COPY src/backend/requirements.txt ./requirements.txt
```

Do not assume that `COPY . .` from the Dockerfile directory will copy the whole application. The Dockerfile location and the build context are separate concepts.

---

## 3) Docker Compose

### Services

The Compose file must define the following services:

- `backend`, built from `../docker/backend.Dockerfile`;
- `frontend`, built from `../docker/frontend.Dockerfile`;
- `database`, using `mysql:8`.

### Built images and pulled images

The backend and frontend are application services. They must be built from Dockerfiles because their images depend on the project source code and dependency files.

When `docker compose up --build` is executed, Docker Compose builds these two images using the declared build context and Dockerfile. The `--build` flag applies to services that have a `build` section.

The database is different. MySQL is not built by this project. Instead of locally building an image it must use the official one directly:

```yaml
  image: mysql:8
```

If the image is not already present locally, Docker downloads it automatically from Docker Hub, using the official MySQL image. The local project only configures that image through Compose environment variables, volumes, ports, and health checks.

Do not create a custom MySQL Dockerfile, the required database behavior is available off the shelf from `mysql:8`.

### MySQL configuration

Configure the database only through Docker Compose environment variables:

- `MYSQL_ROOT_PASSWORD`
- `MYSQL_DATABASE`
- `MYSQL_USER`
- `MYSQL_PASSWORD`

Do not add database initialization SQL files for this task.

### Backend dependency on MySQL

The `backend` must depend on MySQL, but the dependency must express readiness, not only startup order.

A plain `depends_on` only tells Compose to start the database container before the backend container. This is not always enough. On a fresh volume, MySQL can take several seconds to create the database files, apply the root password, create the application database, and create the application user.

For this task, add a `healthcheck` to the database service and make the backend wait for:

```text
condition: service_healthy
```

The health check should perform a real application-level database check. It should verify that:

- the MySQL server is accepting connections;
- the application database exists;
- the application user can authenticate;
- a minimal query can be executed against that database.

A useful shape for the command is:

```text
mysql -h 127.0.0.1 -u<application-user> -p<application-password> <application-database> -e "SELECT 1"
```

Adapt the placeholders to the values configured in the Compose file. Suppress command output if desired, but keep the exit status meaningful: the command must fail when the application credentials or database are not usable.

A command such as `mysqladmin ping` is only a server reachability check. It can report that MySQL is alive without proving that the application user can log in and use the application database.

Use a plain `depends_on` only when startup order is enough. Use `condition: service_healthy` when the dependent service needs the other service to be operational, as the backend does with MySQL.

### Seed data

The Docker Compose backend configuration must keep the same seeded users available for local testing:

```text
citizen@example.com  / Citizen123!
operator@example.com / Operator123!
admin@example.com    / Admin123!
```

Use:

```text
AUTO_INIT_DB=true
BOOTSTRAP_REFERENCE_DATA=true
BOOTSTRAP_DEMO_DATA=true
```

The seed steps are expected to be idempotent, so the stack can be restarted without duplicating the default data.

### Ports and coherence

Ports may be changed in the Dockerfiles and in Docker Compose, but every related configuration must remain coherent.

Use explicit port mappings. With the default configuration:

```text
3306:3306
5050:5050
5173:5173
```

In a Compose port mapping:

```text
HOST_PORT:CONTAINER_PORT
```

Changing the container port does not automatically change the address exposed on the host. Changing the host port does not automatically change the port used by services inside the Compose network.

The `EXPOSE` instructions in the Dockerfiles are documentation for the container ports. The actual host-to-container mapping is controlled by Docker Compose.

If a port is changed, update all dependent configuration:

- if the backend container port changes, update the backend `PORT`, the backend Compose `ports` mapping, and any service that reaches the backend inside Docker;
- if the backend host port changes, update `VITE_API_BASE_URL` and `VITE_BACKEND_BASE_URL`, because the browser reaches the backend through the host port;
- if the frontend host port changes, update backend `FRONTEND_ORIGIN`, otherwise CORS may block browser requests;
- if the MySQL internal port or service name changes, update backend `DATABASE_URL` and the database health check;
- if only the MySQL host port changes, the backend usually does not need a change, because it reaches MySQL through the Compose network, not through the host mapping.

Do not treat ports as isolated values. Backend, frontend, database, browser URLs, CORS, health checks, and Compose service names must agree.

### Volumes

Use Docker volumes for data that should survive container restarts:

- MySQL data;
- backend instance files;
- uploaded media;
- frontend `node_modules`.

Bind mount the backend and frontend source folders only for local development convenience.

### YAML anchors

Use YAML anchors where they improve readability for repeated configuration values, especially database credentials and application ports.

Keep the `ports` mappings as explicit strings.

---

## 4) Execution

Run the stack from the repository root with:

```powershell
docker compose -f docker/docker-compose.yml up --build
```

To stop the stack while preserving named volumes:

```powershell
docker compose -f docker/docker-compose.yml down
```

To reset the MySQL data and force a clean reseed:

```powershell
docker compose -f docker/docker-compose.yml down -v
```

---

## 5) Verification

### Startup verification

After startup, verify that the services answer from the host machine:

- open **`http://localhost:5173`** and check that the frontend loads;
- open **`http://localhost:5050/apidocs/`** and check that Swagger is available;
- call **`http://localhost:5050/api/v1/meta/reference-data`** and check that reference data is returned.

Verify MySQL with:

```powershell
docker exec participium-database mysql -uparticipium -pparticipium_password participium -e "SELECT 1; SHOW TABLES;"
```

The output must show a successful `SELECT 1` and the application tables created by the backend seed/bootstrap process.

The seeded accounts must be usable from the frontend login page once the backend has completed initialization.

### Seed login verification

Use the frontend login page and verify that a seeded user can log in successfully.

Suggested flow:

1. Start the full Compose stack.
2. Open **`http://localhost:5173`**.
3. Log in with one seeded account, for example `citizen@example.com` / `Citizen123!`.
4. Verify that the authenticated user interface is shown.
5. Log out from the application.

### Database dependency verification

After a successful login/logout check, verify that authentication really depends on MySQL being available.

Suggested flow:

1. Stop only the database container:

```powershell
docker compose -f docker/docker-compose.yml stop database
```

2. Keep backend and frontend running.
3. Try to log in again from the frontend with a seeded account.
4. The login must not succeed, because the backend cannot reach the database.

The exact browser message may depend on frontend error handling, but the important behavior is that the user is not authenticated when MySQL is unavailable.

Restart the database before continuing development:

```powershell
docker compose -f docker/docker-compose.yml start database
```

If needed, recreate the backend after the database is healthy:

```powershell
docker compose -f docker/docker-compose.yml up -d backend
```

---

## 6) Quality Criteria

### Configuration quality

The Docker setup should make configuration visible in `docker-compose.yml` and avoid hard-coded source-code changes.

Local `.env` files must not be copied into images. The Compose file must be the authoritative source for the container runtime configuration required by this task.

### Local reproducibility

The stack should be startable from a clean checkout with Docker installed. The first run may take longer because Docker must download base images and install Python and Node dependencies.

### Development fit

The setup is intended for local development. It is not a hardened production deployment.

### Critical constraints

The setup assumes that host ports `3306`, `5050`, and `5173` are free.

If MySQL is already running on the host, port `3306` may conflict. Stop the local MySQL service or temporarily adjust the host-side mapping in `../docker/docker-compose.yml`.

If any default port is changed, update all related Compose variables, Dockerfile `EXPOSE` documentation, application environment variables, and browser-facing URLs so that backend, frontend, and database still refer to each other consistently.
