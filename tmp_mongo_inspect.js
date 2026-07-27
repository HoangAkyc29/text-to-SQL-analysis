const j = db.analysis_jobs.findOne({analysis_id: '989abea0-8dbf-4151-b50b-2b3c92f42a6b'});
print('job status', j && j.status, 'pending', j && j.pending_interaction_id);
print('collections', db.getCollectionNames().join(','));
const names = db.getCollectionNames();
for (const c of names) {
  const hit = db.getCollection(c).findOne({
    $or: [
      {interaction_id: '399ee20b-ceb7-4505-b8ed-3644154aa648'},
      {analysis_id: '989abea0-8dbf-4151-b50b-2b3c92f42a6b'},
    ]
  });
  if (hit) {
    print('HIT', c, Object.keys(hit).join('|'));
  }
}
