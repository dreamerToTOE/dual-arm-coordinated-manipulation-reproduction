#!/usr/bin/env python3
"""Run the bundled DOCX renderer on Ubuntu 22 without changing host libraries.

Invoke with the Python executable returned by load_workspace_dependencies.
The only LibreOffice and Poppler executables used are the bundled ones.
An Ubuntu 24 glibc sysroot lives under work/ and must not be committed.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[2]
IMAGE = 'ubuntu@sha256:68ee22004a9109b44973313b02ff7b1de250f1de0f5ecb628d73f579aaff33ac'
DEFAULT_DEPS = '/home/ubuntu2004/.cache/codex-runtimes/codex-primary-runtime/dependencies'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--docx', required=True, type=Path)
    parser.add_argument('--output-dir', required=True, type=Path)
    parser.add_argument('--runtime-dir', type=Path, default=ROOT/'work/d082_render_runtime')
    parser.add_argument('--dependencies', type=Path, default=Path(DEFAULT_DEPS))
    args = parser.parse_args()
    deps = args.dependencies.resolve()
    runtime = args.runtime_dir.resolve()
    logs = runtime/'logs'
    logs.mkdir(parents=True, exist_ok=True)
    rootfs = runtime/'sysroot'
    rootfs.mkdir(exist_ok=True)
    if not (rootfs/'ld-linux-x86-64.so.2').exists():
        container = 'd082-render-'+uuid.uuid4().hex[:12]
        with (logs/'prepare_pinned_ubuntu24.log').open('x') as log:
            subprocess.run(['docker','pull',IMAGE],stdout=log,stderr=subprocess.STDOUT,check=True)
            try:
                subprocess.run(['docker','create','--name',container,IMAGE],stdout=log,stderr=subprocess.STDOUT,check=True)
                subprocess.run(['docker','cp',container+':/usr/lib/x86_64-linux-gnu/.',str(rootfs)],stdout=log,stderr=subprocess.STDOUT,check=True)
            finally:
                subprocess.run(['docker','rm',container],stdout=log,stderr=subprocess.STDOUT,check=False)
    linker = rootfs/'ld-linux-x86-64.so.2'
    lo = deps/'native/libreoffice-headless/libreoffice/program'
    poppler = deps/'native/poppler/poppler'
    package = deps.parent/'plugins/openai-primary-runtime/plugins/documents/skills/documents'
    canonical = package/'render_docx.py'
    local_bin = runtime/'bin'
    local_bin.mkdir(exist_ok=True)

    def wrapper(path, binary, libraries, extra_env=''):
        text = '#!/bin/sh\nset -eu\nexport FONTCONFIG_FILE=/etc/fonts/fonts.conf\nexport FONTCONFIG_PATH=/etc/fonts\n'
        text += extra_env
        text += 'exec '+shlex.quote(str(linker))+' --library-path '+shlex.quote(':'.join(map(str,libraries)))+' '+shlex.quote(str(binary))+' "$@"\n'
        path.write_text(text)
        path.chmod(0o755)

    soffice = runtime/'bundled_soffice_isolated'
    wrapper(soffice,lo/'soffice.bin',[lo,poppler/'lib',rootfs],'export SAL_USE_VCLPLUGIN=svp\n')
    for name in ('pdfinfo','pdftoppm'):
        wrapper(local_bin/name,poppler/'bin'/name,[poppler/'lib',rootfs],
                'export POPPLER_DATADIR='+shlex.quote(str(poppler/'share/poppler'))+'\n')
    source = canonical.read_text()
    start = source.index('def _resolve_soffice() -> str:')
    end = source.index('\ndef _read_ooxml_member',start)
    replacement = 'def _resolve_soffice() -> str:\n'
    replacement += '    """Use unchanged bundled binaries with task-local glibc only."""\n'
    replacement += '    os.environ["PATH"] = '+repr(str(local_bin)+os.pathsep+str(deps/'bin/override'))+' + os.pathsep + os.environ.get("PATH", "")\n'
    replacement += '    return '+repr(str(soffice))+'\n\n'
    renderer = runtime/'render_docx_isolated.py'
    renderer.write_text(source[:start]+replacement+source[end:])
    docx = args.docx.resolve()
    output = args.output_dir.resolve()
    now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    command = [str(deps/'python/bin/python3'),str(renderer),str(docx),'--output_dir',str(output),'--emit_pdf','--verbose']
    log_path = logs/('render_'+now+'.log')
    with log_path.open('x') as log:
        result = subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
    pages = sorted(output.glob('page-*.png')) if output.exists() else []
    record = {
        'schema':'P4_D082_ISOLATED_BUNDLED_RENDER_V1',
        'timestamp_utc':now,'host_libraries_changed':False,'desktop_libreoffice_used':False,
        'sysroot_image':IMAGE,'sysroot_extraction':'/usr/lib/x86_64-linux-gnu from pinned Ubuntu24 OCI image',
        'canonical_renderer':str(canonical),'canonical_renderer_sha256':sha(canonical),
        'task_local_renderer':str(renderer),'task_local_renderer_sha256':sha(renderer),
        'bundled_soffice_binary':str(lo/'soffice.bin'),'bundled_soffice_sha256':sha(lo/'soffice.bin'),
        'bundled_poppler_pdfinfo':str(poppler/'bin/pdfinfo'),'bundled_poppler_pdftoppm':str(poppler/'bin/pdftoppm'),
        'isolated_loader_sha256':sha(linker),'isolated_libc_sha256':sha(rootfs/'libc.so.6'),
        'docx':str(docx),'docx_sha256':sha(docx),'command':command,'returncode':result.returncode,
        'log':str(log_path),'output_dir':str(output),'rendered_pages':len(pages),
        'pdfs':[{'path':str(p),'sha256':sha(p)} for p in output.glob('*.pdf')] if output.exists() else [],
        'visual_review':'PENDING_HUMAN_OR_AGENT_INSPECTION_OF_ALL_PAGES',
    }
    record_path = logs/('render_'+now+'.json')
    with record_path.open('x') as stream:
        json.dump(record,stream,ensure_ascii=False,indent=2)
        stream.write('\n')
    print(json.dumps({'returncode':result.returncode,'rendered_pages':len(pages),'output_dir':str(output),'record':str(record_path)},ensure_ascii=False))
    return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
