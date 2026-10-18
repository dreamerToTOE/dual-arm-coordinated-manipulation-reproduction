"""Integer event scheduler and causal endpoint ZOH; no truth/observer inputs."""
import heapq
import numpy as np
from .contact_geometry import selection

class EndpointClock:
    def __init__(self,protocol,scale=1,delayed=False):
        if scale not in (1,2):raise ValueError('UNREGISTERED_TICK_SCALE')
        c=protocol['clocks'];self.scale=scale;self.periods=tuple(scale*x for x in (c['controller_period_ticks'],*c['EE_sensor_period_ticks'],c['tactile_period_ticks'],c['visual_period_ticks']))
        self.publish_periods=tuple(scale*x for x in c['EE_command_period_ticks']);self.delays=tuple(scale*x for x in c['stress_delay_ticks']) if delayed else (0,0)
        self.command=np.zeros((2,6));self.command_tick=None;self.published=np.zeros((2,6));self.applied=np.zeros((2,6));self.queue=[];self.serial=0
    def receive(self,tick,command):
        a=np.array(command,dtype=float,copy=True)
        if a.shape!=(2,6) or not np.isfinite(a).all():raise ValueError('COMMAND_INVALID')
        if tick%self.periods[0]!=0:raise ValueError('COMMAND_OFF_CONTROLLER_CLOCK')
        if self.command_tick is not None and tick<=self.command_tick:raise ValueError('REPEATED_OR_BACKWARDS_COMMAND')
        self.command=a;self.command_tick=int(tick)
    def publish_and_deliver(self,tick,modes):
        events=[]
        for side,period in enumerate(self.publish_periods):
            if tick%period:continue
            if self.command_tick is None or self.command_tick>tick:raise ValueError('NO_CAUSAL_CONTROLLER_COMMAND')
            H=selection(modes[side]);u=H.T@H@self.command[side];self.published[side]=u
            due=int(tick+self.delays[side]);self.serial+=1;heapq.heappush(self.queue,(due,self.serial,side,u.copy()))
            events.append({'type':'publish','side':side+1,'tick':int(tick),'source_command_tick':self.command_tick,'delivery_tick':due,'U':u.tolist()})
        while self.queue and self.queue[0][0]<=tick:
            due,serial,side,u=heapq.heappop(self.queue)
            if due!=tick:raise ValueError('MISSED_ACTUATION_TIMESTAMP')
            self.applied[side]=u;events.append({'type':'apply_for_next_plant_interval','side':side+1,'tick':int(tick),'queue_serial':serial,'U':u.tolist()})
        return events
    def next_tick(self,tick,end_tick,event_ticks=()):
        candidates=[(tick//p+1)*p for p in self.periods]+[end_tick]+[t for t in event_ticks if t>tick]
        if self.queue:candidates.append(self.queue[0][0])
        next_tick=min(candidates)
        if next_tick<=tick:raise ValueError('EVENT_CLOCK_DID_NOT_ADVANCE')
        return next_tick
