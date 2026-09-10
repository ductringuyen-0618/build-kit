# Container registry path, fallback hosts, custom domain, cost

Companion to steps 1, 8, and 9 of `SKILL.md`.

## Deploy from a container image

Use this when the GitHub integration is not authorised for the repo, or
when the buildpack keeps failing and the Dockerfile builds fine locally.

```
doctl registry create <registry-name>
doctl registry login
docker build -t registry.digitalocean.com/<registry-name>/api:<tag> backend
docker push registry.digitalocean.com/<registry-name>/api:<tag>
```

Use a git SHA or a timestamp as `<tag>`; never `latest`, because an
unchanged spec reuses the existing image. In the service block, replace
`github:` and `dockerfile_path:` with:

```yaml
    image:
      registry_type: DOCR
      repository: api
      tag: <tag>
```

Then `doctl apps create --spec .do/app.yaml` (first time) or
`doctl apps update <app-id> --spec .do/app.yaml`. After pushing a new
tag, either update the spec with the new tag or run
`doctl apps create-deployment <app-id>`, which always pulls the image.

GitHub Container Registry and Docker Hub work the same way with
`registry_type: GHCR` or `DOCKER_HUB`, a `registry` field (the owner or
namespace), and for private images `registry_credentials` in
`username:token` form, given in plain text on the first submit and
returned encrypted afterwards.

## Fallback 1: run the image locally

```
docker build -t app backend
docker run --rm -p 8080:8080 --env-file backend/.env app
curl -sS -w "\n%{http_code}\n" http://localhost:8080/health
```

Demo on `http://localhost:8080`. State plainly that the App Platform
deploy is in progress or failed, and what the last log line said.

## Fallback 2: a Droplet running the same image

A public IP on port 80 still counts as deployed on DigitalOcean.

```
doctl compute ssh-key list --format ID,Name
doctl compute droplet create demo --image docker-20-04 --size s-1vcpu-1gb \
  --region nyc3 --ssh-keys <key-id> --wait --format ID,PublicIPv4
ssh root@<ip>
```

On the Droplet (the `docker-20-04` 1-Click image ships Docker and
Compose; the slug is historical, the OS is current Ubuntu LTS):

```
git clone https://github.com/<owner>/<repo>.git && cd <repo>
docker build -t app backend
docker run -d --restart unless-stopped -p 80:8080 --env-file backend/.env app
```

Or pull the image pushed to the registry above after `doctl registry
login` on the Droplet. Point the frontend's API base URL at
`http://<ip>` and verify with the same curl checks as step 7, using
`URL=http://<ip>`.

## Custom domain (only if the task requires it)

```yaml
domains:
  - domain: app.example.com
    type: PRIMARY
```

Then create a CNAME at the DNS provider pointing `app.example.com` at the
`DefaultIngress` host. Certificates are issued automatically once DNS
resolves. Budget 10 to 30 minutes for propagation; do not start this in
the last half hour of a timed session.

## Cost and cleanup

| Resource | Approximate price | Delete with |
| --- | --- | --- |
| Service `apps-s-1vcpu-0.5gb` | $5/month | `doctl apps delete <app-id> --force` |
| Service `apps-s-1vcpu-1gb` | $12/month | same |
| Static site | free tier for the first few, then $3/month each | same |
| Dev database | $7/month | deleted with the app |
| Container registry (starter tier) | free for one repository | `doctl registry delete --force` |
| Droplet `s-1vcpu-1gb` | $6/month | `doctl compute droplet delete demo --force` |

Everything is billed hourly, so a two-hour demo costs cents. Afterwards
revoke the token in the control panel under API, Tokens, and run
`doctl auth remove --context <name>` if a dedicated context was created.

## Limits worth knowing

- Builds time out after 1 hour, deployments after 30 minutes.
- Images over 2 GiB are likely to fail to deploy; multi-stage Dockerfiles
  keep the runtime image small.
- The whole repo is cloned at build time, but only `source_dir` is
  present at run time.
