import sys, json; pass
import pandas as pd, numpy as np, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mplsoccer import Pitch
from scipy.spatial import ConvexHull
M='1925299'; import pathlib
D=str(pathlib.Path(__file__).resolve().parents[1]/'data'/'matches'/M)+'/'
meta=json.load(open(D+f'{M}_match.json',encoding='utf-8'))
team={p['id']:p['team_id'] for p in meta['players']}
gk={p['id'] for p in meta['players'] if 'Goalkeeper' in str(p['player_role'])}
name={p['id']:p['short_name'] for p in meta['players']}
frames=[json.loads(l) for l in open(D+f'{M}_tracking_extrapolated.jsonl',encoding='utf-8')]
fr={f['frame']:f for f in frames}
e=pd.read_csv(D+f'{M}_dynamic_events.csv',low_memory=False)
ph=pd.read_csv(D+f'{M}_phases_of_play.csv')
L,W=meta['pitch_length'],meta['pitch_width']
INK,DEF,ATT,HL='#2b2b2b','#c0392b','#2e6fb5','#f1c40f'
def base(ax):
    Pitch(pitch_type='skillcorner',pitch_length=L,pitch_width=W,line_color='#9aa0a6',pitch_color='white',linewidth=1).draw(ax=ax)
def players(f):
    return pd.DataFrame([dict(pid=p['player_id'],x=p['x'],y=p['y'],team=team.get(p['player_id'])) for p in f['player_data']])

# ---------- A: compact medium block that still conceded central access
pp=e[e.event_type=='player_possession'].copy()
ph['area']=ph.team_out_of_possession_width_start*ph.team_out_of_possession_length_start
mb=ph[ph.team_out_of_possession_phase_type=='medium_block']
cand=pp[(pp.team_out_of_possession_phase_type=='medium_block')&pp.inside_defensive_shape_start.eq(True)&pp.channel_start.eq('center')&pp.third_start.eq('middle_third')]
cand=cand.merge(mb[['index','area']],left_on='phase_index',right_on='index').sort_values('area')
row=cand.iloc[0]; f=fr[int(row.frame_start)]; P=players(f)
att_team=row.team_id; dfn=P[(P.team!=att_team)&(~P.pid.isin(gk))]
fig,ax=plt.subplots(figsize=(10,6.6)); base(ax)
h=ConvexHull(dfn[['x','y']].values); pts=dfn[['x','y']].values[h.vertices]
ax.fill(pts[:,0],pts[:,1],color=DEF,alpha=.12,zorder=2); ax.plot(np.r_[pts[:,0],pts[0,0]],np.r_[pts[:,1],pts[0,1]],color=DEF,lw=1.2,zorder=2)
a=P[P.team==att_team]; d=P[P.team!=att_team]
ax.scatter(d.x,d.y,s=110,c=DEF,edgecolors='white',zorder=4,label=f"Defending ({meta['away_team']['short_name'] if att_team==meta['home_team']['id'] else meta['home_team']['short_name']})")
ax.scatter(a.x,a.y,s=110,c=ATT,edgecolors='white',zorder=4,label=f"Attacking ({row.team_shortname})")
c=P[P.pid==row.player_id]; ax.scatter(c.x,c.y,s=380,facecolors='none',edgecolors=HL,lw=2.5,zorder=5)
ax.annotate(f"{name[row.player_id]} receives inside the block",(c.x.iloc[0],c.y.iloc[0]),xytext=(0,-34),textcoords='offset points',ha='center',fontsize=10,color=INK,zorder=6)
b=f['ball_data']; ax.scatter(b['x'],b['y'],s=40,c='black',zorder=6)
hw=dfn.y.max()-dfn.y.min(); hl=dfn.x.max()-dfn.x.min()
ax.set_title(f"Idea A · Compact, but vulnerable? — medium block {hl:.0f} m long × {hw:.0f} m wide (outfield players), minute {int(row.minute_start)}",fontsize=11,color=INK,loc='left')
ax.legend(loc='upper center',bbox_to_anchor=(.5,-.01),ncol=2,frameon=False,fontsize=9)
fig.savefig(''+str(pathlib.Path(__file__).parent/'figures')+'/ideaA_compact_block.png',dpi=150,bbox_inches='tight')
print('A', row.event_id, row.minute_start, round(row.area), hl, hw)

# ---------- B: dangerous run available, pass went elsewhere
po=e[e.event_type=='passing_option']
runs=po[po.dangerous.eq(True)&po.associated_off_ball_run_event_id.notna()&~po.targeted.eq(True)]
pass_pp=pp[pp.end_type.eq('pass')].set_index('event_id')
best=None
for _,r in runs.sort_values('xthreat',ascending=False).iterrows():
    pid=r.associated_player_possession_event_id
    if pid not in pass_pp.index: continue
    t=po[(po.associated_player_possession_event_id==pid)&po.targeted.eq(True)]
    if len(t)==0: continue
    best=(r,t.iloc[0],pass_pp.loc[pid]); break
r,t,poss=best
run=e[e.event_id==r.associated_off_ball_run_event_id].iloc[0]
fe=int(poss.frame_end); f=fr[fe]; P=players(f)
fig,ax=plt.subplots(figsize=(10,6.6)); base(ax)
a=P[P.team==poss.team_id]; d=P[P.team!=poss.team_id]
ax.scatter(d.x,d.y,s=110,c=DEF,edgecolors='white',zorder=4,label='Defending')
ax.scatter(a.x,a.y,s=110,c=ATT,edgecolors='white',zorder=4,label=f'Attacking ({poss.team_shortname})')
def pos(fno,pid):
    q=[p for p in fr[fno]['player_data'] if p['player_id']==pid]; return (q[0]['x'],q[0]['y']) if q else None
s=pos(int(run.frame_start),r.player_id); en=pos(fe,r.player_id)
ax.annotate('',xy=en,xytext=s,arrowprops=dict(arrowstyle='->',color=HL,lw=2.5,ls='--'),zorder=5)
ax.annotate(f"{name[r.player_id]}'s {run.event_subtype.replace('_',' ')} run\nthreat if served {r.xthreat:.2f}, completion {r.xpass_completion:.0%}",en,xytext=(-8,24),textcoords='data',ha='left',fontsize=9.5,color=INK,zorder=6,bbox=dict(fc='white',ec=HL,lw=1.5),arrowprops=dict(arrowstyle='-',color=HL,lw=1))
cp=pos(fe,poss.player_id); tp=pos(fe,t.player_id)
ax.annotate('',xy=tp,xytext=cp,arrowprops=dict(arrowstyle='->',color=INK,lw=2),zorder=5)
ax.annotate(f"pass chosen: {name[t.player_id]}\nthreat {t.xthreat:.2f}, completion {t.xpass_completion:.0%}",tp,xytext=(-8,-24),textcoords='data',ha='left',fontsize=9.5,color=INK,zorder=6,bbox=dict(fc='white',ec=INK,lw=1),arrowprops=dict(arrowstyle='-',color=INK,lw=1))
c0=pos(fe,poss.player_id); ax.scatter(*c0,s=380,facecolors='none',edgecolors=INK,lw=2,zorder=5)
ax.set_title(f"Idea B · Dangerous runs left unused — {name[poss.player_id]} on the ball, minute {int(poss.minute_start)}",fontsize=11,color=INK,loc='left')
ax.legend(loc='upper center',bbox_to_anchor=(.5,-.01),ncol=2,frameon=False,fontsize=9)
fig.savefig(''+str(pathlib.Path(__file__).parent/'figures')+'/ideaB_unused_run.png',dpi=150,bbox_inches='tight')
print('B', poss.name, poss.minute_start, r.xthreat, t.xthreat)
