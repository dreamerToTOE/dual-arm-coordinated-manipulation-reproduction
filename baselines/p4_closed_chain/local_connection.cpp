#include "baselines/p4_closed_chain/local_connection.hpp"
#include <algorithm>
#include <chrono>
#include <cmath>
#include <stdexcept>

namespace p4
{
const char* statusName(ConnectionStatus s)
{
  switch(s)
  {
#define P4_CASE(x) case ConnectionStatus::x: return #x
    P4_CASE(CONNECTED); P4_CASE(INVALID_OPTIONS); P4_CASE(INVALID_INPUT);
    P4_CASE(JOINT_LIMIT); P4_CASE(CLOSURE); P4_CASE(EVALUATION_ERROR);
    P4_CASE(COLLISION_UNAVAILABLE); P4_CASE(COLLISION); P4_CASE(PROJECTION_FAILED);
    P4_CASE(PROJECTION_JUMP); P4_CASE(CONTINUITY); P4_CASE(DEPTH_LIMIT);
    P4_CASE(PROJECTION_BUDGET); P4_CASE(PATH_BUDGET);
#undef P4_CASE
  }
  return "UNKNOWN";
}
namespace
{
bool positive(double x) { return std::isfinite(x) && x>0.; }
bool valid(const LocalConnectionOptions& o)
{
  const auto& p=o.projection;
  return positive(o.leaf_resolution_rad) && positive(o.adjacent_l2_limit_rad) &&
    positive(o.adjacent_max_abs_limit_rad) && positive(o.projection_correction_limit_rad) &&
    o.max_depth>0 && o.max_depth<=64 && o.max_projections>0 && o.max_path_points>=2 &&
    positive(p.position_tolerance_m) && positive(p.rotation_tolerance_rad) &&
    p.max_iterations>0 && std::isfinite(p.svd_absolute_cutoff) && p.svd_absolute_cutoff>=0. &&
    positive(p.svd_relative_cutoff) && p.svd_relative_cutoff<1. &&
    std::isfinite(p.stagnation_step_rad) && p.stagnation_step_rad>=0.;
}
struct Connector
{
  const ConstraintEvaluator& constraint;
  const JointMarginEvaluator& margin;
  const CollisionEvaluator& collision;
  const LocalConnectionOptions& o;
  ConnectionResult& r;

  bool fail(ConnectionStatus s,const std::string& why,std::optional<std::size_t> i={})
  {
    r.status=s; r.reason=why; r.failed_point=i;
    if(i) r.checked_points.at(*i).failure=why;
    return false;
  }
  std::size_t add(const JointVector& q,const std::string& role,std::size_t depth)
  {
    ConnectionPoint p; p.q=q; p.role=role; p.depth=depth;
    r.checked_points.push_back(std::move(p));
    r.maximum_depth=std::max(r.maximum_depth,depth);
    return r.checked_points.size()-1;
  }
  bool qualify(std::size_t i)
  {
    auto& p=r.checked_points[i];
    if(!p.q.allFinite()) return fail(ConnectionStatus::INVALID_INPUT,"Nonfinite 14q",i);
    try
    {
      const double m=margin(p.q); p.joint_margin_rad=m;
      if(!std::isfinite(m)) return fail(ConnectionStatus::EVALUATION_ERROR,"Nonfinite native margin",i);
      if(m<0.) return fail(ConnectionStatus::JOINT_LIMIT,"Unchanged native joint bounds violated",i);
      const auto c=constraint(p.q); p.residual=c.residual;
      if(!c.residual.allFinite() || !c.jacobian.allFinite())
        return fail(ConnectionStatus::EVALUATION_ERROR,"Nonfinite C/Jc",i);
      if(c.residual.head<3>().norm()>o.projection.position_tolerance_m ||
         c.residual.tail<3>().norm()>o.projection.rotation_tolerance_rad)
        return fail(ConnectionStatus::CLOSURE,"Separate position/rotation closure test failed",i);
    }
    catch(const std::exception& e) { return fail(ConnectionStatus::EVALUATION_ERROR,e.what(),i); }
    try { p.collision=collision(p.q); }
    catch(const std::exception& e) { return fail(ConnectionStatus::COLLISION_UNAVAILABLE,e.what(),i); }
    if(!p.collision->complete)
      return fail(ConnectionStatus::COLLISION_UNAVAILABLE,p.collision->reason,i);
    if(p.collision->self_collision || p.collision->world_collision)
      return fail(ConnectionStatus::COLLISION,p.collision->reason,i);
    // 非碰撞检查返回 contacts 是矛盾证据，fail closed，不以reason字符串覆盖结果。
    if(!p.collision->contacts.empty())
      return fail(ConnectionStatus::COLLISION_UNAVAILABLE,"Free result contains collision contacts",i);
    p.qualified=true; return true;
  }
  bool segment(std::size_t a,std::size_t b,std::size_t depth)
  {
    r.maximum_depth=std::max(r.maximum_depth,depth);
    // value copy：递归add会重分配vector，不能保留悬空引用。
    const JointVector qa=r.checked_points[a].q, qb=r.checked_points[b].q;
    const JointVector d=qb-qa;
    if(d.norm()<=o.leaf_resolution_rad)
    {
      const bool continuous=d.norm()<=o.adjacent_l2_limit_rad &&
        d.cwiseAbs().maxCoeff()<=o.adjacent_max_abs_limit_rad;
      r.leaf_edges.push_back({a,b,d.norm(),d.cwiseAbs().maxCoeff(),continuous});
      if(!continuous) return fail(ConnectionStatus::CONTINUITY,"Projected leaf violates adjacency limits",b);
      if(r.verified_prefix.size()>=o.max_path_points)
      {
        r.leaf_edges.back().accepted=false;
        return fail(ConnectionStatus::PATH_BUDGET,"Verified path-point budget exhausted",b);
      }
      r.verified_prefix.push_back(b); return true;
    }
    if(depth>=o.max_depth) return fail(ConnectionStatus::DEPTH_LIMIT,"RBS depth exhausted");
    if(r.projection_calls>=o.max_projections)
      return fail(ConnectionStatus::PROJECTION_BUDGET,"RBS midpoint-projection budget exhausted");
    const JointVector seed=(qa+qb)*0.5;
    const auto m=add(seed,"PROJECTED_MIDPOINT",depth+1);
    ++r.projection_calls;
    auto projected=project(seed,constraint,margin,o.projection); // 原TASK04，失败q绝不能当成功。
    r.checked_points[m].q=projected.projected_q;
    r.checked_points[m].residual=projected.final_residual;
    const double correction=(projected.projected_q-seed).norm();
    r.checked_points[m].projection_correction_l2_rad=correction;
    const auto status=projected.status;
    const std::string reason=projected.reason;
    r.checked_points[m].projection=std::move(projected);
    if(status!=ProjectionStatus::CONVERGED)
      return fail(ConnectionStatus::PROJECTION_FAILED,std::string(statusName(status))+": "+reason,m);
    if(!std::isfinite(correction) || correction>o.projection_correction_limit_rad)
      return fail(ConnectionStatus::PROJECTION_JUMP,"Midpoint projection correction exceeds finite locality guard",m);
    if(!qualify(m)) return false;
    return segment(a,m,depth+1) && segment(m,b,depth+1);
  }
};
} // namespace

ConnectionResult connect(const JointVector& start,const JointVector& goal,
                         const ConstraintEvaluator& constraint,const JointMarginEvaluator& margin,
                         const CollisionEvaluator& collision,const LocalConnectionOptions& o)
{
  const auto begin=std::chrono::steady_clock::now();
  ConnectionResult r; r.requested_start=start; r.requested_goal=goal;
  Connector c{constraint,margin,collision,o,r};
  if(!valid(o) || !constraint || !margin || !collision)
    c.fail(ConnectionStatus::INVALID_OPTIONS,"Invalid explicit options/callbacks");
  else
  {
    const auto a=c.add(start,"EXACT_START",0);
    if(c.qualify(a))
    {
      r.verified_prefix.push_back(a);
      if(goal.allFinite() && (goal.array()==start.array()).all())
        { r.status=ConnectionStatus::CONNECTED; r.reason="Identical qualified configuration"; }
      else
      {
        const auto b=c.add(goal,"EXACT_GOAL",0);
        if(c.qualify(b) && c.segment(a,b,0))
          { r.status=ConnectionStatus::CONNECTED; r.reason="Discrete projected RBS connection; not continuous collision certificate"; }
      }
    }
  }
  r.compute_wall_time_sec=std::chrono::duration<double>(std::chrono::steady_clock::now()-begin).count();
  return r;
}
} // namespace p4
