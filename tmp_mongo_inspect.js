printjson(db.getCollectionNames());
const cols = db.getCollectionNames();
for (const c of cols) {
  const hit = db.getCollection(c).findOne({
    $or: [
      { analysis_id: "e16b4117-6083-4aad-81c4-8ef2e7dc2422" },
      { _id: "e16b4117-6083-4aad-81c4-8ef2e7dc2422" },
      { "analysis.analysis_id": "e16b4117-6083-4aad-81c4-8ef2e7dc2422" },
    ],
  });
  if (hit) {
    print("COL=" + c);
    print("keys=" + Object.keys(hit));
    print("status=" + hit.status);
    print("outcome=" + hit.outcome);
    print("trace_id=" + hit.trace_id);
    print("sandbox=" + (hit.sandbox_id || hit.sandbox_root || hit.artifact_dir || ""));
    if (hit.progress) print("progress=" + JSON.stringify(hit.progress).slice(0, 800));
    print("result=" + String(hit.result_message || "").slice(0, 800));
  }
}
