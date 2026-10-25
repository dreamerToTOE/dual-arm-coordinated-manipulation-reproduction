#!/usr/bin/env python3
"""[ENGINEERING] Render immutable qualified ABB paths; no planning/IK/collision.

Exact private author .tris assets are read, never copied to the output directory.
All path records are exported in source traversal order. Render-only elementary
FK is checked against saved poses; this comparison is not path requalification.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import sys
import time

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SCOPE = 'RECONSTRUCTED_ALIGNED_DISCRETE_SOURCE_COLLISION_POLICY_ONLY'
ASSET_DEFAULT = 'reports/p4_d083_spatial_assets_20261022'
DATA_DEFAULT = 'results/20261022_D083_spatial_visualization01'
SPEC = [
 ('II_PCS', 'II', 'PCS', 177, '20261015_R2_ABB_RRT_PATH01', 'reports/P4_FULL_R2_ABB_RRT_PATH_INDEPENDENT_SAVED_POST_REVIEW_20261015.json'),
 ('II_NR', 'II', 'NR', 393, '20261015_R2_ABB_RRT_NR_PATH01', 'reports/P4_FULL_R2_ABB_RRT_NR_PATH_ROOT_INDEPENDENT_POST_20261016.json'),
 ('III_PCS', 'III', 'PCS', 649, '20261018_R2_D080_III_RRT_PCS_PHYSICAL01', 'reports/P4_D080_ENV_III_RRT_PCS_PHYSICAL01_SAVED_INDEPENDENT_POST_20261018.json'),
]
MESH_NAMES = ['Base_r.tris','Link1_r.tris','Link2_r.tris','Link3_r.tris','Link4_r.tris','Link5_r.tris','Link6.tris','EE_r.tris','table.tris','obs.tris','cone.tris']
ARM_COLORS = ['#df7a31', '#437fb6']
ROLE_COLORS = ['#c86420', '#236aab']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def rel(path):
    path = Path(path).resolve()
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)


def write_json(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def rot(axis, angle):
    c, s = math.cos(angle), math.sin(angle)
    if axis == 'x': return np.array([[1.,0,0],[0,c,-s],[0,s,c]])
    if axis == 'y': return np.array([[c,0,s],[0,1.,0],[-s,0,c]])
    return np.array([[c,-s,0],[s,c,0],[0,0,1.]])


def mesh_frames(q, environment, arm):
    """Exact aligned source CAD-frame policy (not a new URDF/geometry model).

    Author collisionDetection.cpp has 134+168 collinear offsets and integer
    72-13/2=66, 13/2+60=66. These original CAD origins differ from the physical
    oracle's 149.6+152.4 and 65.5+66.5, while their final TCP is identical.
    """
    distance = 900. if environment == 'II' else 1200.
    r0 = np.eye(3) if arm == 0 else rot('z',3.1416/2) @ rot('z',3.1416/2)
    r = r0.copy(); p = np.array([(-1 if arm == 0 else 1)*distance/2,0.,0.])
    frames = [(r.copy(),p.copy())]
    p = p + r @ np.array([0.,0.,290.])
    offsets = [(0,0,0),(0,0,270),(134,0,70),(168,0,0),(66,0,0),(66,0,0)]
    for angle, axis, offset in zip(q, ['z','y','y','x','y','x'], offsets):
        r = r @ rot(axis,float(angle))
        frames.append((r.copy(),p.copy()))
        p = p + r @ np.asarray(offset)
    frames.append((r.copy(),p.copy()))
    # Link3 is at after270; Link4 at after134; Link5 at after168 etc.
    # Above loop gives exactly Base,Link1,Link2,Link3,Link4,Link5,Link6,EE.
    return frames


def load_path(spec, inputs):
    key, env, method, expected, run, certificate = spec
    run_path = ROOT/'results/p4_full'/run
    execution_path = run_path/'execution.json'
    execution = read(execution_path); cert = read(ROOT/certificate)
    assert sha(execution_path) == cert['execution_sha256'], 'Execution/certificate mismatch'
    assert cert.get('passed') is True or str(cert.get('status','')).startswith('PASS_')
    protocol_path = ROOT/execution['protocol']; protocol = read(protocol_path)
    assert sha(protocol_path) == execution['protocol_sha256']
    queue_path = run_path/'complete_original_saved_queue.json'
    queue = read(queue_path) if queue_path.exists() else protocol['fixed_queue']
    assert len(queue['nodes']) == expected
    # NR queue stores rich node records; PCS queues store raw q12 arrays.
    queue['nodes'] = [n['q12'] if isinstance(n,dict) else n for n in queue['nodes']]
    for path in [execution_path,ROOT/certificate,protocol_path]: inputs[rel(path)] = sha(path)
    if queue_path.exists(): inputs[rel(queue_path)] = sha(queue_path)
    # NR's saved unique queue is not path order; use original edge node IDs.
    order = []
    for edge in queue['edges']:
        ids = edge['node_ids']
        assert queue['nodes'][ids[0]] == edge['qa12'] and queue['nodes'][ids[-1]] == edge['qb12']
        if order:
            assert ids[0] == order[-1], 'Disconnected source traversal'
            order.extend(ids[1:])
        else: order.extend(ids)
    assert len(order) == expected and set(order) == set(range(expected))
    data=[]; max_render_position=0.; max_render_rotation=0.
    for index in range(expected):
        collision_suffix = '_collision_raw' if method == 'NR' else '_collision_response'
        paths=[run_path/f'node_{index:05d}{suffix}.json' for suffix in ['', '_math', collision_suffix]]
        n,m,c = map(read,paths)
        for path in paths: inputs[rel(path)] = sha(path)
        assert n['q12'] == m['q12'] == queue['nodes'][index]
        assert n['collision'] == c and m['math_qualified'] is True
        assert c['collision'] is False and c['variants']['aligned']['pose_consistency']['passed'] is True
        frames=[mesh_frames(n['q12'][6*i:6*i+6],env,i) for i in range(2)]
        poses=np.asarray(m['poses'])
        for arm in range(2):
            r,p=frames[arm][-1]
            max_render_position=max(max_render_position,float(np.max(np.abs(p-poses[arm,:3,3]))))
            max_render_rotation=max(max_render_rotation,float(np.max(np.abs(r-poses[arm,:3,:3]))))
        native=c['variants']['native']['pose_consistency']
        data.append({'id':index,'q':n['q12'],'poses':poses,'frames':frames,
                     'position_mm':m['closure']['position_max_abs'],
                     'rotation':m['closure']['rotation_matrix_max_abs'],
                     'native_pass':native['passed'],'aligned_pass':True,
                     'native_position_mm':max(e['translation_maxabs_mm'] for e in native['errors']),
                     'native_rotation':max(e['rotation_maxabs'] for e in native['errors'])})
    assert max_render_position < 1e-9 and max_render_rotation < 1e-12, 'Rendering TCP does not match saved poses'
    ordered=[data[i] for i in order]
    roles=[e.get('active_chain') for e in queue['edges']]
    switches=[]
    for i,(a,b) in enumerate(zip(roles,roles[1:]),1):
        if a is not None and a != b:
            node=queue['edges'][i]['node_ids'][0]
            switches.append({'number':len(switches)+1,'previous_edge_zero_based':i-1,
                             'next_edge_zero_based':i,'source_node_id':node,
                             'traversal_index':order.index(node),'from_active':a,'to_active':b})
    q=np.asarray([d['q'] for d in ordered]); limits=np.tile(np.array([[-165,165],[-110,110],[-110,70],[-160,160],[-120,120],[-400,400]])*3.1416/180,(2,1))
    metrics={'key':key,'environment':env,'method':method,'planner':'RRT','node_count':expected,
             'source_edge_count':len(queue['edges']),'milestones':queue['source_milestone_count'],
             'path_q12_l2_length_rad':float(np.linalg.norm(np.diff(q,axis=0),axis=1).sum()),
             'max_leaf_l2_rad':float(np.linalg.norm(np.diff(q,axis=0),axis=1).max()),
             'minimum_original_joint_limit_margin_rad':float(np.minimum(q-limits[:,0],limits[:,1]-q).min()),
             'maximum_saved_position_residual_mm':max(d['position_mm'] for d in data),
             'maximum_saved_rotation_matrix_residual':max(d['rotation'] for d in data),
             'aligned_pose_pass_nodes':expected,'native_pose_pass_nodes':sum(d['native_pass'] for d in data),
             'maximum_native_tcp_position_mismatch_mm':max(d['native_position_mm'] for d in data),
             'maximum_native_tcp_rotation_matrix_mismatch':max(d['native_rotation'] for d in data),
             'render_fk_saved_TCP_max_position_difference_mm':max_render_position,
             'render_fk_saved_TCP_max_rotation_difference':max_render_rotation,
             'active_roles':roles,'role_switches':switches,'role_switch_count':len(switches),
             'qualification_scope':SCOPE,'historical_certificate':certificate,'historical_certificate_sha256':sha(ROOT/certificate),
             'execution':rel(execution_path),'execution_sha256':sha(execution_path),
             'protocol':rel(protocol_path),'protocol_sha256':sha(protocol_path),
             'source_result':protocol.get('source_result'),
             'source_traversal_order_node_ids':order,
             'continuous_collision_certificate':False,'minimum_clearance_certificate':False}
    for p in [protocol.get('source_result')]:
        if p and (ROOT/p).exists(): inputs[p]=sha(ROOT/p)
    return {'key':key,'env':env,'method':method,'ordered':ordered,'queue':queue,'metrics':metrics}


def load_meshes(root, expected, inputs):
    meshes={}
    for name in MESH_NAMES:
        path=root/name
        assert sha(path)==expected[name], 'Private author mesh SHA mismatch: '+name
        inputs[rel(path)]=sha(path)
        a=np.fromstring(path.read_text(),sep=' ')
        assert len(a)==1+int(a[0])*9
        meshes[name]=a[1:].reshape(-1,3,3)
    return meshes


def transformed(tris,r,p): return (tris @ r.T + p)/1000.


def draw_tri(ax,tris,r,p,color,alpha=1.,edge=False):
    coll=Poly3DCollection(transformed(tris,r,p),facecolor=color,edgecolor=('#75828c' if edge else 'none'),linewidth=.15,alpha=alpha,zsort='average')
    ax.add_collection3d(coll)


def scene(ax,path,meshes,index,*,ghost=False,roles=False,obstacle_alpha=.15,trace=True):
    env=path['env']; record=path['ordered'][index]
    if trace:
        poses=np.array([d['poses'] for d in path['ordered']])
        for arm in range(2):
            p=poses[:,arm,:3,3]/1000
            ax.plot(*p.T,color=ARM_COLORS[arm],lw=1.4,alpha=.8)
            ax.scatter(*p[0],c='#27874e',marker='o',s=23,depthshade=False)
            ax.scatter(*p[-1],c='#a52b39',marker='*',s=52,depthshade=False)
    for arm in range(2):
        for name,(r,p) in zip(MESH_NAMES[:8],record['frames'][arm]):
            draw_tri(ax,meshes[name],r,p,ARM_COLORS[arm],.18 if ghost else .92)
    # Original table collision mesh is transformed by R0,T0 (arm1 base).
    table_p=np.array([-450. if env=='II' else -600.,0.,0.])
    draw_tri(ax,meshes['table.tris'],np.eye(3),table_p,'#cbd2d9',.08)
    if env=='II':
        for dx,dy in [(0,0),(250,250),(-250,-250)]:
            draw_tri(ax,meshes['obs.tris'],np.eye(3),np.array([dx,dy,0]),'#7f8992',obstacle_alpha,True)
    else:
        draw_tri(ax,meshes['cone.tris'],np.eye(3),np.zeros(3),'#8b969f',obstacle_alpha,True)
        draw_tri(ax,meshes['cone.tris'],rot('x',3.14),np.array([0,0,790.]),'#8b969f',obstacle_alpha,True)
    t=record['poses']; rod=np.stack([t[0,:3,3],t[1,:3,3]])/1000
    # Display width is a line glyph, not an asserted surface mesh or clearance.
    ax.plot(*rod.T,color='#243d49',lw=3.5,solid_capstyle='round',zorder=20)
    ax.scatter(*rod.T,c='#243d49',s=12,depthshade=False)
    if roles:
        role=next((e['active_chain'] for e in reversed(path['queue']['edges']) if record['id'] in e['node_ids']),0)
        ax.text2D(.02,.89,f'active A{role+1}; passive A{2-role}',transform=ax.transAxes,color=ROLE_COLORS[role],fontsize=9)
    distance=.45 if env=='II' else .6
    for x in [-distance,distance]:
        ax.text(x,-.18,0,'A1' if x<0 else 'A2',fontsize=9,color='#3d464d')
    setup_ax(ax,env)


def setup_ax(ax,env):
    ax.set_xlim(-.92,.92);ax.set_ylim(-.66,.66);ax.set_zlim(-.03,.97)
    ax.set_box_aspect((1.84,1.32,1.0))
    ax.view_init(elev=22,azim=-58)
    ax.set_xlabel('x / m',labelpad=-2);ax.set_ylabel('y / m',labelpad=-2);ax.set_zlabel('z / m',labelpad=-3)
    ax.xaxis.set_major_locator(plt.MaxNLocator(4));ax.yaxis.set_major_locator(plt.MaxNLocator(3));ax.zaxis.set_major_locator(plt.MaxNLocator(4))
    ax.tick_params(labelsize=8,pad=0)
    for axis in [ax.xaxis,ax.yaxis,ax.zaxis]:
        axis.pane.set_facecolor((.98,.985,.99,1));axis._axinfo['grid']['color']=(.85,.88,.91,.65)


def save(fig,assets,name):
    fig.savefig(assets/(name+'.png'),dpi=220,facecolor='white')
    fig.savefig(assets/(name+'.pdf'),facecolor='white')
    plt.close(fig)


def make_ii(pcs,nr,meshes,assets):
    fig=plt.figure(figsize=(14.8,8.9))
    fig.suptitle('Environment II | saved dual ABB IRB120 RRT trajectories',x=.035,ha='left',fontsize=17,fontweight='bold',y=.985)
    fig.text(.035,.944,'Same reconstructed endpoints and geometry; each displayed pose is an existing qualified discrete node.',fontsize=11,color='#53616e')
    for row,path in enumerate([pcs,nr]):
        n=len(path['ordered']); inds=[0,n//2,n-1]
        for col,index in enumerate(inds):
            ax=fig.add_subplot(2,3,row*3+col+1,projection='3d');scene(ax,path,meshes,index)
            ax.set_title(f"{path['method']} | {'start' if col==0 else 'goal' if col==2 else 'saved midpoint'} | {index+1}/{n}",fontsize=11,pad=0)
    fig.text(.035,.053,'Orange: arm 1   Blue: arm 2   Dark bar: grasped object   Green circle: start TCPs   Red star: goal TCPs',fontsize=10)
    fig.text(.035,.028,'Source CAD surfaces and aligned frames. Discrete source collision policy only; native TCP equivalence and continuous CCD are not certified.',fontsize=9,color='#92444b')
    fig.subplots_adjust(left=.005,right=.99,bottom=.095,top=.91,wspace=-.02,hspace=.03)
    save(fig,assets,'fig_A1_environment_II_saved_PCS_NR')


def make_iii(path,meshes,assets):
    fig=plt.figure(figsize=(14.8,7.1));fig.suptitle('Environment III | narrow passage and four active-arm role changes',x=.035,ha='left',y=.98,fontsize=17,fontweight='bold')
    for col,(idx,label) in enumerate([(0,'start'),(len(path['ordered'])//2,'saved midpoint'),(len(path['ordered'])-1,'goal')]):
        ax=fig.add_subplot(1,3,col+1,projection='3d');scene(ax,path,meshes,idx,roles=True,obstacle_alpha=.25)
        ax.set_title(f'{label} | node {idx+1}/649',fontsize=11,pad=0)
    fig.text(.035,.19,'Two original cone surfaces: lower (identity) and upper (Rx=3.14, z=0.790 m). Base separation 1.200 m; grasped bar 0.500 m.',fontsize=10)
    fig.text(.035,.145,'Saved evidence: closure max 4.55e-13 mm; rotation matrix max 4.47e-15; 649/649 aligned TCP poses pass; 0/649 native poses pass.',fontsize=10)
    fig.text(.035,.10,'The four role changes show the mechanism on this final path. A performance advantage over compatible fixed PCS or NR is not established.',fontsize=10)
    fig.text(.035,.055,'Aligned reconstructed discrete source collision policy only. Obstacle transparency is for visibility; no clearance or continuous CCD certificate.',fontsize=9,color='#92444b')
    fig.subplots_adjust(left=.005,right=.99,bottom=.23,top=.92,wspace=-.05)
    save(fig,assets,'fig_A2_environment_III_narrow_passage')


def make_switches(path,meshes,assets):
    switches=path['metrics']['role_switches'];assert len(switches)==4
    fig=plt.figure(figsize=(14.8,15.2));fig.suptitle('Environment III | the four recorded role transitions',x=.035,ha='left',y=.99,fontsize=17,fontweight='bold')
    fig.text(.035,.964,'Each row shows the immediately preceding saved node, the shared milestone, and the immediately following saved node.',fontsize=10)
    for row,event in enumerate(switches):
        j=event['traversal_index']
        for col,(index,label) in enumerate([(j-1,'before'),(j,'shared milestone'),(j+1,'after')]):
            ax=fig.add_subplot(4,3,row*3+col+1,projection='3d')
            scene(ax,path,meshes,index,trace=False,obstacle_alpha=.18)
            role=event['from_active'] if col==0 else event['to_active']
            text=f"S{row+1} {label} | node {index} (0-based)\nA{event['from_active']+1} → A{event['to_active']+1} active; incoming edge {event['previous_edge_zero_based']+1} / outgoing {event['next_edge_zero_based']+1}"
            ax.set_title(text,fontsize=9,pad=0)
            ax.text2D(.05,.86,f'A{role+1} active'+(' on outgoing edge' if col==1 else ''),transform=ax.transAxes,color=ROLE_COLORS[role],fontsize=9)
    fig.text(.035,.026,'Switch markers refer to edge roles, not an instantaneous physical action; node poses remain unchanged. All frames are exact saved configurations.',fontsize=9)
    fig.text(.035,.011,'Source mesh frames / aligned discrete qualification only; native TCP mismatch retained. No interpolation, new solve, IK, collision query, or CCD.',fontsize=9,color='#92444b')
    fig.subplots_adjust(left=.005,right=.99,bottom=.048,top=.94,hspace=.08,wspace=-.03)
    save(fig,assets,'fig_A3_environment_III_four_switch_frames')


def make_timeline(path,assets):
    fig,(ax,ax2,ax3)=plt.subplots(3,1,figsize=(13.5,8.3),gridspec_kw={'height_ratios':[1,1.5,1.5]},sharex=True)
    fig.suptitle('Environment III | edge-role timeline and preserved numerical evidence',x=.07,ha='left',y=.98,fontsize=16,fontweight='bold')
    for i,e in enumerate(path['queue']['edges']):
        a=path['metrics']['source_traversal_order_node_ids'].index(e['node_ids'][0]);b=path['metrics']['source_traversal_order_node_ids'].index(e['node_ids'][-1])
        ax.broken_barh([(a,b-a)],(e['active_chain']-.3,.6),facecolors=ROLE_COLORS[e['active_chain']])
        ax.text((a+b)/2,e['active_chain'],str(i+1),ha='center',va='center',color='white',fontsize=9)
    for event in path['metrics']['role_switches']:
        x=event['traversal_index']
        for axis in [ax,ax2,ax3]:axis.axvline(x,color='#a64f68',ls='--',lw=.9)
        ax.annotate(f"S{event['number']}\nn={x}",(x,1.35),ha='center',fontsize=9,color='#8a3550')
    ax.set_yticks([0,1],['A1 active\nA2 passive','A2 active\nA1 passive']);ax.set_ylim(-.5,1.95)
    ax.set_title('Numbers inside bars are final solution edge IDs (1–14); dashed lines are four role transitions.',fontsize=10,loc='left')
    n=np.arange(len(path['ordered'])); pos=np.array([d['position_mm'] for d in path['ordered']]);rotv=np.array([d['rotation'] for d in path['ordered']])
    ax2.semilogy(n,np.maximum(pos,1e-17),color='#186c8c',label='Saved position closure / mm')
    ax2.semilogy(n,np.maximum(rotv,1e-17),color='#ca7a27',label='Saved rotation matrix residual')
    ax2.set_ylabel('Saved residual\n(separate units)');ax2.legend(loc='upper right',fontsize=9)
    native=np.array([d['native_position_mm'] for d in path['ordered']]);ax3.plot(n,native,color='#a24960',label='Saved native TCP translation mismatch / mm')
    ax3.axhline(1e-5,ls=':',color='black',lw=1,label='Historical TCP position gate / mm')
    ax3.set_ylabel('Native TCP\nmismatch / mm');ax3.legend(loc='upper right',fontsize=9);ax3.set_xlabel('Saved path traversal index (0-based; arbitrary playback, not physical time)')
    for a in [ax,ax2,ax3]:a.grid(alpha=.2);a.spines[['top','right']].set_visible(False)
    fig.text(.07,.025,'649 aligned pass / 0 native pass; retained independent qualification does not certify continuous CCD, all entity surfaces, or minimum clearance.',fontsize=9,color='#92444b')
    fig.subplots_adjust(left=.1,right=.975,bottom=.095,top=.90,hspace=.34)
    save(fig,assets,'fig_A4_environment_III_roles_and_evidence')


def export_path(path,data_dir):
    p=data_dir/(path['key']+'_saved_path.csv')
    fields=['traversal_index','source_node_id']+[f'q{i+1}_rad' for i in range(12)]+[f'TCP{arm}_{a}_mm' for arm in [1,2] for a in ['x','y','z']]+['saved_closure_position_mm','saved_closure_rotation_matrix','aligned_TCP_pass','native_TCP_pass','native_TCP_translation_mismatch_mm','native_TCP_rotation_matrix_mismatch']
    with p.open('x',newline='') as f:
        w=csv.writer(f);w.writerow(fields)
        for i,d in enumerate(path['ordered']):
            w.writerow([i,d['id'],*d['q'],*d['poses'][0,:3,3],*d['poses'][1,:3,3],d['position_mm'],d['rotation'],1,int(d['native_pass']),d['native_position_mm'],d['native_rotation']])
    write_json(data_dir/(path['key']+'_provenance_and_metrics.json'),path['metrics'])


def make_gif(path,meshes,assets,count):
    # Select existing nodes, always including both sides of every role transition.
    indices=set(np.linspace(0,len(path['ordered'])-1,count).astype(int).tolist())
    for e in path['metrics']['role_switches']:
        indices.update([e['traversal_index']-1,e['traversal_index'],e['traversal_index']+1])
    frames=[]
    for index in sorted(indices):
        fig=plt.figure(figsize=(7,5.5),dpi=100);ax=fig.add_subplot(111,projection='3d');scene(ax,path,meshes,index,roles=True,obstacle_alpha=.18)
        fig.suptitle(f'Environment III | existing saved node {index}/648',fontsize=13,y=.97)
        fig.text(.06,.055,'Aligned discrete source policy only; native TCP mismatch retained.',fontsize=8)
        fig.text(.06,.025,'Arbitrary playback of saved states; no dynamics or continuous safety claim.',fontsize=8)
        fig.subplots_adjust(left=0,right=1,bottom=.12,top=.93);fig.canvas.draw()
        frame=Image.fromarray(np.array(fig.canvas.buffer_rgba())[:,:,:3]);frames.append(frame.copy());plt.close(fig)
    out=assets/'environment_III_saved_states.gif';frames[0].save(out,save_all=True,append_images=frames[1:],duration=150,loop=0,optimize=False)
    return sorted(indices)


def main():
    started=time.perf_counter();cpu=time.process_time()
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,default=Path(DATA_DEFAULT))
    p.add_argument('--figures',type=Path,default=Path(ASSET_DEFAULT))
    p.add_argument('--mesh-root',type=Path,required=True,help='Private pinned author simulator directory; each SHA must match saved collision evidence')
    p.add_argument('--animation-frames',type=int,default=0,help='0 skips GIF; positive selects saved nodes, plus all role-switch neighbors')
    args=p.parse_args()
    data_dir=args.output if args.output.is_absolute() else ROOT/args.output
    assets=args.figures if args.figures.is_absolute() else ROOT/args.figures
    assert not data_dir.exists(),'Refusing to overwrite output directory'
    assets.mkdir(parents=True,exist_ok=True)
    assert not list(assets.glob('fig_A*.png')),'Refusing to overwrite figures'
    inputs={rel(Path(__file__)):sha(__file__)}
    paths=[load_path(spec,inputs) for spec in SPEC]
    assert paths[2]['metrics']['active_roles']==[0,0,0,1,0,0,0,1,1,0,0,0,0,0]
    assert paths[2]['metrics']['role_switch_count']==4
    c=read(ROOT/'results/p4_full/20261018_R2_D080_III_RRT_PCS_PHYSICAL01/node_00000_collision_response.json')
    meshes=load_meshes(args.mesh_root,c['variants']['aligned']['provenance']['mesh_sha256'],inputs)
    source_path=args.mesh_root.parent/'validity_checkers/collisionDetection.cpp'
    if source_path.exists():inputs[rel(source_path)]=sha(source_path)
    data_dir.mkdir(parents=True)
    for path in paths:export_path(path,data_dir)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':11,'pdf.fonttype':42})
    make_ii(paths[0],paths[1],meshes,assets);make_iii(paths[2],meshes,assets);make_switches(paths[2],meshes,assets);make_timeline(paths[2],assets)
    animation=make_gif(paths[2],meshes,assets,args.animation_frames) if args.animation_frames>0 else []
    summary={'schema':'P4_D083_SPATIAL_RENDER_20261022_V1','status':'PASS_SAVED_PATH_BINDING_AND_RENDERING_ONLY',
      'qualification_scope':SCOPE,'new_planner_calls':0,'new_IK_calls':0,'new_NR_or_RBS_calls':0,'new_collision_queries':0,
      'render_FK_arm_calls':2*sum(x[3] for x in SPEC),'render_FK_is_not_requalification':True,
      'paths':[x['metrics'] for x in paths],'inputs_sha256':inputs,
      'rendered_meshes':MESH_NAMES,'source_meshes_copied_to_output':False,
      'animation_saved_traversal_indices':animation,'animation_physical_timing':False,
      'geometry':{'II':{'bases_mm_rad':[[-450,0,0],[450,0,3.1416]],'object_bar_length_mm':300,'obstacles':'obs.tris at [0,0,0], [250,250,0], [-250,-250,0]; table at arm1 base'},
                  'III':{'bases_mm_rad':[[-600,0,0],[600,0,3.1416]],'object_bar_length_mm':500,'obstacles':'cone.tris identity; cone.tris Rx(3.14), translation [0,0,790] mm; table at arm1 base'}},
      'limitations':['No new qualification: closure, limits, collision and native mismatch are inherited saved evidence.',
      'Source CAD-frame policy rendered; physical elementary FK TCP checked against saved independent poses.',
      'Rod is a line glyph between actual TCPs; display width is not a certified material surface.',
      'No continuous CCD, minimum clearance, omitted-pair safety, dynamic trajectory, or speed comparison.',
      'Private original author mesh files are SHA-bound and remain outside deliverable directories.'],
      'elapsed_render_and_binding_wall_s':time.perf_counter()-started,'elapsed_process_CPU_s':time.process_time()-cpu,
      'artifacts_sha256':{rel(p):sha(p) for folder in [data_dir,assets] for p in folder.iterdir() if p.is_file()}}
    write_json(data_dir/'manifest.json',summary)
    print(json.dumps({k:summary[k] for k in ['status','render_FK_arm_calls','elapsed_render_and_binding_wall_s','elapsed_process_CPU_s']}))

if __name__=='__main__': main()
