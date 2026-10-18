"""Predeclared causal ZOH qualification; exact timestamps and commands, no ODE/trials."""
import json
from pathlib import Path
import numpy as np
from baselines.p2_pose_force.clocking import EndpointClock
CFG=json.loads((Path(__file__).resolve().parents[1]/'configs/p2_closed_loop_protocol_v3.json').read_text())

def test_old_published_is_independent_of_new_command_and_delayed_actual():
 c=EndpointClock(CFG,delayed=True);u=np.array([[.01,0,0,0,0,.1],[.02,0,0,0,0,.2]])
 c.receive(0,u);events=c.publish_and_deliver(0,('pivot','pivot'))
 assert [e['type'] for e in events]==['publish','publish','apply_for_next_plant_interval']
 np.testing.assert_array_equal(c.published[:,:3],u[:,:3]);np.testing.assert_array_equal(c.published[:,5],0)
 np.testing.assert_array_equal(c.applied[0],c.published[0]);np.testing.assert_array_equal(c.applied[1],np.zeros(6))
 previous=c.published.copy();c.receive(12,-u);np.testing.assert_array_equal(c.published,previous)
 c.publish_and_deliver(15,('pivot','pivot'));np.testing.assert_array_equal(c.published[0,:3],-u[0,:3]);np.testing.assert_array_equal(c.published[1,:3],u[1,:3])
 assert c.queue[0][0]==900
 # No fresh publisher command need be fabricated to deliver first delayed input.
 c.publish_periods=(901,901);c.publish_and_deliver(900,('pivot','pivot'))
 np.testing.assert_array_equal(c.applied[1,:3],u[1,:3]);assert c.applied[1,5]==0

def test_coarse_and_fine_have_identical_physical_event_and_publication_times():
 traces=[]
 for scale in (1,2):
  c=EndpointClock(CFG,scale);tick=0;end=3000*scale;events=[]
  while True:
   if tick%c.periods[0]==0:c.receive(tick,np.ones((2,6))*.01)
   events.extend((e['type'],e['side'],e['tick']/(3000*scale)) for e in c.publish_and_deliver(tick,('pivot','pivot')))
   if tick==end:break
   tick=c.next_tick(tick,end)
  traces.append(events)
 assert traces[0]==traces[1]
 assert sum(e[0]=='publish' and e[1]==1 for e in traces[0])==201
 assert sum(e[0]=='publish' and e[1]==2 for e in traces[0])==51
 assert (7*3000)%12==(13*3000)%12==(76*3000)%200==0
