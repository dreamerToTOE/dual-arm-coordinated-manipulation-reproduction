"""Create a lossless delivery copy; retain the original scientific journal."""
from pathlib import Path
import gzip
import hashlib
import json
import time

root=Path(__file__).resolve().parents[3]
source=root/'results/p4_full/20261015_R2_ABB_CBIRRT_D_SOLVE02/evidence.jsonl'
archive=source.with_name('evidence.jsonl.gz')
manifest=source.with_name('evidence_delivery_manifest.json')
execution=source.with_name('execution.json')
started=time.monotonic()
e=json.loads(execution.read_text())
assert source.stat().st_size>100*1024*1024
def digest(p):
    h=hashlib.sha256()
    with p.open('rb')as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()
original_sha=digest(source)
assert original_sha==e['evidence_journal_sha256']
with archive.open('xb')as output:
    with gzip.GzipFile(filename='',mode='wb',fileobj=output,compresslevel=6,mtime=0)as compressed:
        with source.open('rb')as original:
            for chunk in iter(lambda:original.read(1024*1024),b''):compressed.write(chunk)
check=hashlib.sha256();length=0
with gzip.open(archive,'rb')as saved:
    for chunk in iter(lambda:saved.read(1024*1024),b''):
        check.update(chunk);length+=len(chunk)
assert check.hexdigest()==original_sha and length==source.stat().st_size
assert digest(source)==original_sha
record=dict(schema='P4_SOLVE02_JOURNAL_LOSSLESS_DELIVERY_V1',
    original=str(source.relative_to(root)),original_sha256=original_sha,original_bytes=length,
    archive=str(archive.relative_to(root)),archive_sha256=digest(archive),archive_bytes=archive.stat().st_size,
    execution=str(execution.relative_to(root)),execution_sha256=digest(execution),
    decompressed_sha256=check.hexdigest(),decompressed_bytes=length,
    original_file_retained=True,scientific_bytes_modified=False,new_scientific_calls=0,
    reason='Original journal exceeds 100 MiB per-file GitHub limit. Commit this gzip copy and manifest; keep the original locally. Restore exclusively to an absent original path and verify SHA before audits.',
    analysis_wall_s=time.monotonic()-started)
with manifest.open('x')as f:json.dump(record,f,indent=2);f.write('\n')
print(json.dumps(record))
