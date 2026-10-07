python - <<'PY'
import csv
from collections import defaultdict

totals = defaultdict(float)
seen = set()
bad_hours = []

with open('data/workload.csv', newline='') as f:
    for i, row in enumerate(csv.DictReader(f), start=2):
        tid = (row.get('task_id') or '').strip()
        owner = (row.get('owner') or '').strip()
        h_raw = (row.get('hours') or '').strip()
        try:
            h = float(h_raw)
        except ValueError:
            bad_hours.append((i, tid, owner, h_raw))
            continue
        if tid in seen:
            continue  # bỏ qua task_id trùng
        seen.add(tid)
        totals[owner or '(trống)'] += h

for o, v in sorted(totals.items()):
    print(f"{o}: {v:g}")
print('bỏ qua giờ sai:', bad_hours)
PY
