# DigitalOcean scaling references

Checked 2026-09-09 against the pages named. Each bullet is a paraphrase
of what the page says; quote it as "the docs say". Anything not backed
by a URL here is a judgment call and the skill text says so.

## App Platform: instances and autoscaling

- Horizontal scaling adds containers and spreads load across them:
  `instance_count`, default 1, minimum 1, maximum 250 per component.
  Vertical scaling changes `instance_size_slug` and is a manual update
  (control panel, API, or `doctl apps update <id> --spec <file>`).
  https://docs.digitalocean.com/products/app-platform/how-to/scale-app/
- Autoscaling block in the service spec: `autoscaling.min_instance_count`,
  `autoscaling.max_instance_count`, and at least one metric under
  `autoscaling.metrics`: `cpu.percent` (1 to 100, requires a dedicated
  CPU plan), `requests_per_second.per_instance` (minimum 1), or
  `request_duration.p95_milliseconds` (minimum 1). The request-based
  metrics work on shared and dedicated plans but only for services
  receiving external HTTP traffic. Do not set `instance_count` when
  autoscaling is on. When several metrics are set the service scales up
  when any threshold is exceeded and down when all are below target.
  https://docs.digitalocean.com/products/app-platform/reference/app-spec/
  and the scale-app page above.
- Limits: 250 containers per app for fixed or CPU-based scaling, 100
  maximum for request-based autoscaling; request-based autoscaling and
  scale-to-zero cannot be combined on one service; local filesystem is
  4 GiB per container and a full disk replaces the container; builds
  time out after 1 hour and deploy jobs after 30 minutes by default;
  file uploads time out after 600 seconds; apps need two or more
  containers for high-availability failover; static sites cannot have
  resources scaled (use the built-in CDN, or Spaces).
  https://docs.digitalocean.com/products/app-platform/details/limits/
- Instance size slugs and prices (`apps-s-1vcpu-0.5gb`,
  `apps-s-1vcpu-1gb-fixed`, `apps-s-1vcpu-1gb`, `apps-s-1vcpu-2gb`,
  `apps-s-2vcpu-4gb`, and `apps-d-*` dedicated tiers):
  https://docs.digitalocean.com/products/app-platform/details/pricing/
- Health check fields (`http_path`, `initial_delay_seconds`,
  `period_seconds`, `timeout_seconds`, `failure_threshold`) and the
  alert rules `RESTART_COUNT`, `CPU_UTILIZATION`, `MEM_UTILIZATION`,
  `DEPLOYMENT_FAILED`: app spec reference above and
  https://docs.digitalocean.com/products/app-platform/how-to/manage-health-checks/

## Managed PostgreSQL: connections, pools, replicas

- Backend connection limits by plan RAM: 1 GiB 22, 2 GiB 47, 4 GiB 97,
  8 GiB 197, 16 GiB 397, 32 GiB 797, 64 GiB and up 997. For higher
  demand the docs recommend PgBouncer pooling; each cluster supports 21
  pools and up to 1,000 client connections. A cluster has at most 3
  nodes; standby nodes must be in the cluster's region and are not
  offered on some 1 vCPU shared plans. Default 10 clusters per account.
  https://docs.digitalocean.com/products/databases/postgresql/details/limits/
- Connection pools use PgBouncer; the docs describe 25 connections per
  1 GiB of RAM with 3 reserved for maintenance. Modes: transaction
  (default; connection held per transaction, extra transactions queue),
  session (held until the client disconnects; needed for prepared
  statements and advisory locks), statement (one query at a time,
  autocommit only). Sizing advice: start at about half the available
  connections and adjust on CPU. Create with
  `doctl databases pool create <cluster-id> <pool-name> --size <n>`.
  `pg_dump` against a transaction-mode pool errors; back up against the
  cluster directly.
  https://docs.digitalocean.com/products/databases/postgresql/how-to/manage-connection-pools/
- Read-only nodes are replicas of the primary in additional regions,
  replicating over SSL on the public network, sized equal to or larger
  than the primary; unlike standby nodes they do not fail over. Create
  with `doctl databases replica create <cluster-id> <name> --region <r> --size <slug>`;
  promote with `doctl databases replica promote`, after which the two
  clusters are independent. The page does not state replication lag
  figures.
  https://docs.digitalocean.com/products/databases/postgresql/how-to/add-read-only-nodes/
- App Platform dev database (`production: false`) is PostgreSQL only,
  one size, no standby, and exposed to the app as `${db.DATABASE_URL}`;
  a production cluster attaches with `cluster_name` and
  `production: true`.
  https://docs.digitalocean.com/products/app-platform/how-to/manage-databases/

## Managed Valkey (caching)

- DigitalOcean's managed in-memory store is Valkey, described as fully
  Redis-compatible and a drop-in replacement, for caching, message
  queues and primary key-value use. Connection strings are TLS-capable;
  a guide on choosing eviction policies exists on the same site.
  https://docs.digitalocean.com/products/databases/valkey/
- Not verified: the App Platform bindable for a Valkey database. The
  app spec's environment-variable page lists `${<db>.REDIS_URL}` among
  database bindables (see the deploy skill's references); whether that
  name is also what a Valkey component exposes was not checked. Say
  "the docs list a REDIS_URL bindable" and check the panel.

## Spaces (object storage and CDN)

- S3-compatible object storage with a built-in CDN, organised in
  buckets, access by keys or team permissions; typical use is static
  assets, uploads and retention. Billing is storage plus bandwidth;
  traffic over DigitalOcean's internal network does not count against
  outbound transfer in the listed region groups.
  https://docs.digitalocean.com/products/spaces/

## Load Balancers

- Managed Regional and Global Load Balancers distribute traffic to
  backend Droplets or Kubernetes nodes, with health checks, sticky
  sessions and SSL termination; network (TCP/UDP) and internal-only
  variants exist. App Platform services do not need one; the platform
  fronts them. A Load Balancer is the answer when the deploy moves to
  Droplets.
  https://docs.digitalocean.com/products/networking/load-balancers/

## Not verified

- Replication lag for read-only nodes (not stated on the page fetched).
- Whether a Valkey database exposes `${db.REDIS_URL}` to App Platform
  components.
- Load Balancer node-count limits and the exact App Platform ingress
  rate-limiting behaviour (none is documented on the pages fetched; the
  skill assumes rate limiting is the service's job).
