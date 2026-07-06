# Triển khai Docker và compose

Tách từ [`docs/TAI_LIEU_VAN_HANH_TOAN_BO_REPO.md`](../docs/TAI_LIEU_VAN_HANH_TOAN_BO_REPO.md) (dòng 633–646).

← [Mục lục docs2](README.md)

---

# Phần V — Deploy

docker compose build profiles docker-bases trước.

Volumes: supermarket-artifacts, supermarket-attachments, supermarket-state, redis, mongo.

prod overlay: Caddy 80/443, Redis requirepass, Mongo root auth, no host ports except Caddy.

extra_hosts host.docker.internal cho SQL Server trên host Windows.

scripts/init_auth_db.py — idempotent schema + seed.

---

