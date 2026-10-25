#!/usr/bin/env python3
"""Additional D083 plots from exported saved CSVs; no scientific requalification."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import render_spatial as render

ROOT=render.ROOT


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--data',type=Path,default=Path(render.DATA_DEFAULT))
    ap.add_argument('--figures',type=Path,default=Path(render.ASSET_DEFAULT))
    ap.add_argument('--mesh-root',type=Path,required=True)
    args=ap.parse_args();started=time.perf_counter();cpu=time.process_time()
    data=ROOT/args.data;assets=ROOT/args.figures
    assert not (assets/'fig_A2_environment_III_narrow_passage_v2.png').exists()
    assert not (assets/'fig_A5_spatial_saved_trajectories.png').exists()
    inputs={render.rel(__file__):render.sha(__file__),render.rel(Path(render.__file__)):render.sha(render.__file__)}
    paths={}
    for key in ['II_PCS','II_NR','III_PCS']:
        p=data/(key+'_saved_path.csv');inputs[render.rel(p)]=render.sha(p)
        rows=list(csv.DictReader(p.open()));paths[key]=rows
    rows=paths['III_PCS'];ordered=[]
    for row in rows:
        poses=np.tile(np.eye(4),(2,1,1))
        for arm in [1,2]:poses[arm-1,:3,3]=[float(row[f'TCP{arm}_{a}_mm']) for a in ['x','y','z']]
        q=[float(row[f'q{i+1}_rad']) for i in range(12)]
        ordered.append({'id':int(row['source_node_id']),'q':q,'poses':poses,'frames':None})
    manifest=render.read(data/'manifest.json');metrics=next(x for x in manifest['paths'] if x['key']=='III_PCS')
    qp=ROOT/'results/p4_full/20261018_R2_D080_III_RRT_PCS_PHYSICAL01/complete_original_saved_queue.json'
    queue=render.read(qp);inputs[render.rel(qp)]=render.sha(qp)
    path={'env':'III','method':'PCS','ordered':ordered,'queue':queue,'metrics':metrics}
    chosen=[0,len(ordered)//2,len(ordered)-1];max_difference=0.
    for index in chosen:
        d=ordered[index];d['frames']=[render.mesh_frames(d['q'][6*i:6*i+6],'III',i) for i in range(2)]
        for arm in range(2):max_difference=max(max_difference,float(np.max(np.abs(d['frames'][arm][-1][1]-d['poses'][arm,:3,3]))))
    assert max_difference<1e-9
    c=render.read(ROOT/'results/p4_full/20261018_R2_D080_III_RRT_PCS_PHYSICAL01/node_00000_collision_response.json')
    meshes=render.load_meshes(args.mesh_root,c['variants']['aligned']['provenance']['mesh_sha256'],inputs)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'pdf.fonttype':42})
    fig=plt.figure(figsize=(14.8,7.1));fig.suptitle('Environment III | narrow passage and four active-arm role changes',x=.035,ha='left',y=.98,fontsize=17,fontweight='bold')
    for col,(idx,label) in enumerate(zip(chosen,['start','saved midpoint','goal'])):
        ax=fig.add_subplot(1,3,col+1,projection='3d');render.scene(ax,path,meshes,idx,roles=True,obstacle_alpha=.25)
        # Wider inner margins prevent the oblique y-axis labels being clipped.
        ax.tick_params(labelsize=7,pad=-1);ax.set_xlabel('x / m',labelpad=-6);ax.set_ylabel('y / m',labelpad=-6);ax.set_zlabel('z / m',labelpad=-5)
        ax.set_title(f'{label} | node {idx+1}/649',fontsize=11,pad=0)
    fig.text(.035,.19,'Original lower cone: identity. Original upper cone: Rx=3.14, z=0.790 m. Base separation: 1.200 m. Bar: 0.500 m.',fontsize=10)
    fig.text(.035,.145,'Saved evidence: closure max 4.55e-13 mm; rotation matrix max 4.47e-15; 649/649 aligned TCPs pass; 0/649 native TCPs pass.',fontsize=10)
    fig.text(.035,.10,'Four role changes show the mechanism on this final path. A performance advantage over compatible fixed PCS or NR is not established.',fontsize=10)
    fig.text(.035,.055,'Aligned reconstructed discrete source collision policy only. Transparency aids visibility; no clearance or continuous CCD certificate.',fontsize=9,color='#92444b')
    fig.subplots_adjust(left=.065,right=.935,bottom=.26,top=.91,wspace=.14)
    render.save(fig,assets,'fig_A2_environment_III_narrow_passage_v2')
    fig=plt.figure(figsize=(13.5,9.1));fig.suptitle('Saved spatial trajectories | position and joint coordinates',x=.055,ha='left',y=.98,fontsize=17,fontweight='bold')
    ax=fig.add_subplot(221,projection='3d')
    for key,color in [('II_PCS','#bd621e'),('II_NR','#266f9f')]:
        r=paths[key];p=np.array([[float(x[f'TCP{a}_{v}_mm']) for a in [1,2] for v in ['x','y','z']] for x in r]).reshape(-1,2,3).mean(axis=1)/1000
        ax.plot(*p.T,color=color,lw=2,label=key.replace('II_',''))
        ax.scatter(*p[0],c='#27874e',marker='o',s=35);ax.scatter(*p[-1],c='#a52b39',marker='*',s=65)
    ax.set_title('Environment II | object center',fontsize=12);ax.set_xlabel('x / m');ax.set_ylabel('y / m');ax.set_zlabel('z / m');ax.view_init(25,-62);ax.legend(loc='upper left',fontsize=9)
    ax2=fig.add_subplot(222,projection='3d');r=paths['III_PCS'];p=np.array([[float(x[f'TCP{a}_{v}_mm']) for a in [1,2] for v in ['x','y','z']] for x in r]).reshape(-1,2,3).mean(axis=1)/1000
    for e in queue['edges']:
        ids=e['node_ids'];a,b=ids[0],ids[-1];part=p[a:b+1];ax2.plot(*part.T,color=render.ROLE_COLORS[e['active_chain']],lw=2)
    for e in metrics['role_switches']:
        point=p[e['traversal_index']];ax2.scatter(*point,c='#8a3550',s=22);ax2.text(*point,f" S{e['number']}",fontsize=9)
    ax2.scatter(*p[0],c='#27874e',marker='o',s=35);ax2.scatter(*p[-1],c='#a52b39',marker='*',s=65)
    ax2.set_title('Environment III | object center and role changes',fontsize=12);ax2.set_xlabel('x / m');ax2.set_ylabel('y / m');ax2.set_zlabel('z / m');ax2.view_init(25,-62)
    for subplot,key in [(223,'II_PCS'),(224,'III_PCS')]:
        axis=fig.add_subplot(subplot);r=paths[key];q=np.array([[float(row[f'q{i+1}_rad']) for i in range(12)] for row in r]);u=np.linspace(0,1,len(q))
        for i in range(12):axis.plot(u,q[:,i],color=plt.cm.tab20(i),lw=1,label=f'A{1+i//6} J{1+i%6}')
        axis.set_title(key.replace('_',' / ')+' | saved joint coordinates',fontsize=12);axis.set_xlabel('Normalized saved-node index (not physical time)');axis.set_ylabel('q / rad');axis.grid(alpha=.2);axis.spines[['top','right']].set_visible(False)
        if key=='III_PCS':
            for e in metrics['role_switches']:axis.axvline(e['traversal_index']/(len(q)-1),ls='--',c='#8a3550',lw=.7)
    fig.legend(*fig.axes[-1].get_legend_handles_labels(),loc='lower center',ncol=6,fontsize=8,bbox_to_anchor=(.5,.045))
    fig.text(.055,.022,'Object center is the arithmetic midpoint of saved TCPs. Lines join recorded states for display; these single examples establish no speed or success advantage.',fontsize=9,color='#92444b')
    fig.subplots_adjust(left=.065,right=.94,bottom=.17,top=.92,wspace=.22,hspace=.38)
    render.save(fig,assets,'fig_A5_spatial_saved_trajectories')
    out={'schema':'P4_D083_SPATIAL_FIGURE_SUPPLEMENT_V1','status':'PASS_SAVED_CSV_RENDER_ONLY','inputs_sha256':inputs,'new_scientific_qualification_calls':0,'render_FK_arm_calls':6,'maximum_render_TCP_vs_exported_saved_translation_difference_mm':max_difference,'elapsed_wall_s':time.perf_counter()-started,'elapsed_CPU_s':time.process_time()-cpu,'reason':'A2 v2 adds plot margins after visual QA; original figure and manifest retained. A5 adds explicit saved object-center and joint-coordinate trajectories.','outputs_sha256':{render.rel(p):render.sha(p) for p in assets.glob('fig_A*') if '_v2' in p.name or 'A5_' in p.name}}
    render.write_json(data/'figure_supplement_manifest.json',out)
    original=data/'manifest_render_original.json';original.write_bytes((data/'manifest.json').read_bytes())
    manifest['report_figures']={'ii_scene':render.rel(assets/'fig_A1_environment_II_saved_PCS_NR.png'),'ii_paths':render.rel(assets/'fig_A5_spatial_saved_trajectories.png'),'iii_scene':render.rel(assets/'fig_A2_environment_III_narrow_passage_v2.png'),'iii_switches':render.rel(assets/'fig_A3_environment_III_four_switch_frames.png'),'iii_timeline':render.rel(assets/'fig_A4_environment_III_roles_and_evidence.png')}
    manifest['figure_supplement_manifest']=render.rel(data/'figure_supplement_manifest.json')
    manifest['figure_supplement_manifest_sha256']=render.sha(data/'figure_supplement_manifest.json')
    manifest['original_render_manifest']=render.rel(original);manifest['original_render_manifest_sha256']=render.sha(original)
    (data/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'status':out['status'],'render_FK_arm_calls':6,'wall_s':out['elapsed_wall_s']}))

if __name__=='__main__':main()
