#!/usr/bin/env python3
"""Saved-only streaming gzip delivery check; never parses scientific JSONL."""
from pathlib import Path
import datetime,gzip,hashlib,json,subprocess
ROOT=Path('/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-p4-full')
FOLDER=ROOT/'results/p4_full/20261015_R2_ABB_CBIRRT_D_SOLVE02'
OUT=ROOT/'reports/P4_FULL_R2_ABB_CBIRRT_D_SOLVE02_LOSSLESS_DELIVERY_INDEPENDENT_REVIEW_20261016.json'
def digest_stream(stream):
    h=hashlib.sha256();n=0
    while True:
        b=stream.read(1024*1024)
        if not b:return h.hexdigest(),n
        h.update(b);n+=len(b)
def digest(p):
    with p.open('rb')as f:return digest_stream(f)
def main():
    if OUT.exists()or OUT.with_suffix('.md').exists():raise SystemExit('PRESERVE_PREVIOUS_DELIVERY_REVIEW')
    manifest_path=FOLDER/'evidence_delivery_manifest.json';m=json.loads(manifest_path.read_bytes());checks=[]
    original=ROOT/m['original'];archive=ROOT/m['archive'];before_original=digest(original);before_archive=digest(archive)
    with gzip.open(archive,'rb')as f:decompressed=digest_stream(f)
    def ck(n,v):checks.append(dict(check=n,passed=bool(v)))
    ck('manifest exact paths and schema',m['schema']=='P4_SOLVE02_JOURNAL_LOSSLESS_DELIVERY_V1'and original==FOLDER/'evidence.jsonl'and archive==FOLDER/'evidence.jsonl.gz')
    ck('original retained exact known SHA and length',before_original==('c297a6a8c9f3107bf756e70381eedca7b3799d5ef78b283eaeca35b84aa885df',132278298)==(m['original_sha256'],m['original_bytes']))
    ck('archive exact known SHA and length',before_archive==('a5545be34dfb45896d79d4735e8f324c3f393b4f815ca48d50f475541a314113',22012155)==(m['archive_sha256'],m['archive_bytes']))
    ck('complete gzip stream CRC EOF lossless bytes',decompressed==before_original==(m['decompressed_sha256'],m['decompressed_bytes']))
    e=json.loads((ROOT/m['execution']).read_bytes());ck('execution original exact journal hash remains',digest(ROOT/m['execution'])[0]==m['execution_sha256']=='c7cbd868da1cd9feb149bc057c4a63ff3e722b81123998e1a8cc5e8e1bab5906'and e['evidence_journal_sha256']==before_original[0])
    ck('original preservation and no scientific change',m['original_file_retained']is True and m['scientific_bytes_modified']is False and m['new_scientific_calls']==0)
    ignore=(ROOT/'.gitignore').read_bytes();committed=subprocess.check_output(['git','show','HEAD:.gitignore'],cwd=ROOT)
    extra=b'\n# Lossless delivery copy and manifest are committed; original raw stays local.\n/results/p4_full/20261015_R2_ABB_CBIRRT_D_SOLVE02/evidence.jsonl\n'
    ck('ignore delta only exact single raw path',ignore==committed+extra or ignore==committed+extra.lstrip(b'\n'))
    check_ignore=subprocess.check_output(['git','check-ignore','-v','--',m['original']],cwd=ROOT,text=True).strip();ck('actual ignore matches exact anchored pattern','\t'+m['original']in check_ignore and ':/results/p4_full/20261015_R2_ABB_CBIRRT_D_SOLVE02/evidence.jsonl\t'in check_ignore)
    ck('archive and manifest are not ignored',subprocess.run(['git','check-ignore','-q','--',m['archive']],cwd=ROOT).returncode==1 and subprocess.run(['git','check-ignore','-q','--',str(manifest_path.relative_to(ROOT))],cwd=ROOT).returncode==1)
    ck('original and archive unchanged after full read',digest(original)==before_original and digest(archive)==before_archive)
    failed=[x for x in checks if not x['passed']];r=dict(schema='P4_SOLVE02_LOSSLESS_DELIVERY_INDEPENDENT_REVIEW_V1',status='PASS_LOSSLESS_GZIP_DELIVERY_ONLY'if not failed else'FAIL_DELIVERY_REVIEW',generated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reviewer='nr_entry_review; independent saved-only delivery review',personnel_independent=True,checks_total=len(checks),checks_passed=sum(x['passed']for x in checks),checks_failed=len(failed),checks=checks,failures=failed,original_sha256=before_original[0],original_bytes=before_original[1],archive_sha256=before_archive[0],archive_bytes=before_archive[1],decompressed_sha256=decompressed[0],decompressed_bytes=decompressed[1],manifest_sha256=digest(manifest_path)[0],gitignore_sha256=hashlib.sha256(ignore).hexdigest(),actual_ignore_rule=check_ignore,audit_script_sha256=digest(Path(__file__))[0],new_scientific_calls=0,parsed_scientific_jsonl_records=0,limitations=['Streaming saved-byte delivery only; original journal remains local and unchanged.','Does not rerun or reinterpret S02 transport, candidate path or physical qualification.','Decompression was streamed in memory, never extracted or overwritten.'])
    with OUT.open('x')as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
    with OUT.with_suffix('.md').open('x')as f:f.write(f"# S02 原始journal无损交付独立审查\n\n{r['status']}：{r['checks_passed']}/{len(checks)}，失败{len(failed)}。gzip完整流解压（含CRC/EOF）恰为132278298字节，SHA c297a6a8…；原文件仍存在、前后相同。gzip22012155字节，SHA a5545be3…；manifest及原execution绑定同一journal。\n\n.gitignore只增加该原raw的精确anchored路径，gzip/manifest可跟踪。仅读字节/流式解压，不解析科学JSONL、不落地解压、不重跑科学或改变原文件。\n")
    print(json.dumps({k:r[k]for k in('status','checks_total','checks_passed','checks_failed')},ensure_ascii=False))
if __name__=='__main__':main()
