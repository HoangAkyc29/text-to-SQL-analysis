const a=db.analysis_jobs.findOne({analysis_id:"af72abec-49f3-4001-9f05-4d0406cf3c8a"});
print("status="+ (a&&a.status));
print("outcome="+ (a&&a.outcome));
print("trace="+ (a&&a.trace_id));
print("result="+ String(a&&a.result_message||"").slice(0,300));
