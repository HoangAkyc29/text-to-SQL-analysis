# Scripts vận hành (tổng quan)

Tách từ [`docs/TAI_LIEU_VAN_HANH_TOAN_BO_REPO.md`](../docs/TAI_LIEU_VAN_HANH_TOAN_BO_REPO.md) (dòng 665–678).

← [Mục lục docs2](README.md)

---

# Phần Y — Scripts

init_auth_db.py — chạy SQL migrations + seed_auth.

seed_auth.py — bcrypt upsert users từ AUTH_SEED_* env.

gen_rbac_seed.py — sinh 004_permissions từ project.yaml.

explore_db_deep.py — khảo sát DB + TCVN3 validate.

index_schema_docs.py — embed schema vào Mongo.

---

