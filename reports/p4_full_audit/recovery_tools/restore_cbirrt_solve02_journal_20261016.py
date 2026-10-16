"""Verify the lossless S02 delivery; optionally restore an absent original."""
from pathlib import Path
import argparse
import gzip
import hashlib
import json

root=Path(__file__).resolve().parents[3]
folder=root/'results/p4_full/20261015_R2_ABB_CBIRRT_D_SOLVE02'
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--restore',action='store_true',help='Exclusively create the original if absent; never overwrite.')
args=ap.parse_args()
m=json.loads((folder/'evidence_delivery_manifest.json').read_text())
archive=root/m['archive'];original=root/m['original']
def digest(p):
    h=hashlib.sha256()
    with p.open('rb')as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()
assert digest(archive)==m['archive_sha256'] and archive.stat().st_size==m['archive_bytes']
h=hashlib.sha256();length=0
with gzip.open(archive,'rb')as f:
    for chunk in iter(lambda:f.read(1024*1024),b''):
        h.update(chunk);length+=len(chunk)
assert h.hexdigest()==m['original_sha256'] and length==m['original_bytes']
restored=False
if args.restore and not original.exists():
    with original.open('xb')as output:
        with gzip.open(archive,'rb')as f:
            for chunk in iter(lambda:f.read(1024*1024),b''):output.write(chunk)
    restored=True
if original.exists():
    assert original.stat().st_size==length and digest(original)==h.hexdigest()
print(json.dumps(dict(lossless_verified=True,original_exists=original.exists(),restored=restored,
    original_bytes=length,original_sha256=h.hexdigest(),new_scientific_calls=0)))
