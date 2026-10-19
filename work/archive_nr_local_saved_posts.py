from pathlib import Path
import gzip,hashlib,json
R=Path('/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-p4-full')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=[]
for name in ['P4_FULL_R2_ABB_NR_LOCAL_INDEPENDENT_POST_20261015.json','P4_FULL_R2_ABB_NR_LOCAL_ROOT_INDEPENDENT_POST_20261015.json']:
 p=R/'reports'/name;gz=Path(str(p)+'.gz');before=sha(p)
 with gz.open('xb') as out:
  with gzip.GzipFile(filename='',mode='wb',fileobj=out,mtime=0,compresslevel=9) as z:z.write(p.read_bytes())
 assert hashlib.sha256(gzip.decompress(gz.read_bytes())).hexdigest()==before==sha(p)
 files.append({'original':str(p.relative_to(R)),'original_sha256':before,'original_bytes':p.stat().st_size,'gzip':str(gz.relative_to(R)),'gzip_sha256':sha(gz),'gzip_bytes':gz.stat().st_size,'lossless_verified':True})
p=R/'reports/P4_FULL_R2_ABB_NR_LOCAL_SAVED_POST_ARCHIVE_20261016.json'
with p.open('x')as f:json.dump({'schema':'P4_NR_LOCAL_SAVED_POST_LOSSLESS_ARCHIVE_V1','original_files_retained_unchanged':True,'zero_new_scientific_calls':True,'reason':'The first saved-only audit JSON exceeds GitHub per-file 100MB; both original JSONs remain local and exact deterministic gzip archives are versioned.','restore':'Read gzip member and write original path exclusively if absent, then verify original_sha256; no scientific recomputation.','files':files},f,ensure_ascii=False,indent=2);f.write('\n')
ignore=R/'.gitignore'
with ignore.open('a')as f:
 f.write('\n# Large saved-only audit JSON originals retained locally; exact lossless gzip and SHA manifests are versioned.\n')
 for x in files:f.write(x['original']+'\n')
print(json.dumps(files,ensure_ascii=False))
