// [ENGINEERING] 纯合成 RBS/原 TASK04 投影测试；碰撞回调仅测接口，不是 FCL/FR3 证据。
#include "baselines/p4_closed_chain/local_connection.hpp"
#include <cmath>
#include <iostream>
#include <limits>
#include <stdexcept>

namespace
{
int checks=0;
void check(bool condition,const char* name)
{
  if(!condition) throw std::runtime_error(name);
  ++checks;
}

p4::LocalConnectionOptions protocol()
{
  // e308a71 预声明工程协议；下面另行标记的 toy 参数只覆盖负向分支。
  return {{1e-8,1e-8,40,1e-12,1e-10,1e-14},.01,.01,.01,.02,12,1023,1025};
}
p4::ConstraintJacobian identityRows()
{
  p4::ConstraintJacobian j=p4::ConstraintJacobian::Zero();
  j.leftCols<6>().setIdentity();
  return j;
}
p4::ClosureSample sample(const p4::Residual& residual,const p4::ConstraintJacobian& jacobian)
{
  p4::ClosureSample s;
  s.left_object=Eigen::Isometry3d::Identity();
  s.right_object=Eigen::Isometry3d::Identity();
  s.residual=residual; s.jacobian=jacobian;
  return s;
}
p4::ClosureSample flat(const p4::JointVector& q)
{
  const p4::Residual residual=q.head<6>();
  return sample(residual,identityRows());
}
p4::ClosureSample parabola(const p4::JointVector& q)
{
  // 六约束、八自由维；解析导数，NR 必须消除直线中点的曲率误差。
  p4::Residual residual=q.head<6>();
  residual(0)=q(0)-q(6)*q(6);
  auto j=identityRows(); j(0,6)=-2.*q(6);
  return sample(residual,j);
}
p4::JointVector freePoint(double t)
{
  p4::JointVector q=p4::JointVector::Zero(); q(6)=t; return q;
}
p4::JointVector curvePoint(double t)
{
  auto q=freePoint(t); q(0)=t*t; return q;
}
p4::JointMarginEvaluator unrestricted()
{
  return [](const p4::JointVector& q) {return 10.-q.cwiseAbs().maxCoeff();};
}
p4::CollisionEvidence freeEvidence()
{
  p4::CollisionEvidence e;
  e.complete=true; e.backend="SYNTHETIC_INTERFACE_ONLY";
  e.acm_identity="NO_REAL_ACM"; e.reason="Synthetic complete free result";
  return e;
}
p4::CollisionEvidence colliding(bool self)
{
  auto e=freeEvidence();
  e.self_collision=self; e.world_collision=!self;
  e.reason="Synthetic rejected collision";
  p4::CollisionContact contact;
  contact.body_a="synthetic_robot"; contact.body_b="synthetic_obstacle";
  contact.category=self?"SELF":"WORLD";
  contact.penetration_depth_m=.001;
  e.contacts.push_back(contact);
  return e;
}
p4::CollisionEvaluator clear()
{
  return [](const p4::JointVector&) {return freeEvidence();};
}
bool exact(const p4::JointVector& a,const p4::JointVector& b)
{
  return (a.array()==b.array()).all();
}
void finiteReport(const p4::ConnectionResult& r)
{
  check(std::isfinite(r.compute_wall_time_sec)&&r.compute_wall_time_sec>=0.,
    "compute cost is finite; no synthetic physical time");
}
void onlyStart(const p4::ConnectionResult& r,const p4::JointVector& start)
{
  check(r.verified_prefix.size()==1,"failed midpoint/endpoint keeps only connected start");
  check(exact(r.checked_points.at(r.verified_prefix.front()).q,start),
    "failure prefix starts at exact caller start");
  check(r.checked_points.at(r.verified_prefix.front()).qualified,
    "failure prefix contains qualified start");
}
void successfulPath(const p4::ConnectionResult& r,const p4::JointVector& start,
                    const p4::JointVector& goal,const p4::LocalConnectionOptions& opt)
{
  check(r.status==p4::ConnectionStatus::CONNECTED,"complete connection succeeds");
  check(!r.failed_point,"successful connection has no failed point");
  check(exact(r.requested_start,start)&&exact(r.requested_goal,goal),
    "request endpoints preserved exactly");
  check(!r.verified_prefix.empty(),"successful prefix is nonempty");
  check(exact(r.checked_points.at(r.verified_prefix.front()).q,start),
    "connected path begins at exact start");
  check(exact(r.checked_points.at(r.verified_prefix.back()).q,goal),
    "connected path reaches exact requested goal without snap");
  check(r.verified_prefix.size()<=opt.max_path_points&&r.projection_calls<=opt.max_projections&&
    r.maximum_depth<=opt.max_depth,"successful connection respects declared finite budgets");
  check(r.leaf_edges.size()+1==r.verified_prefix.size(),"prefix contains ordered completed leaves");
  for(const auto i:r.verified_prefix)
  {
    const auto& p=r.checked_points.at(i);
    check(p.qualified&&p.q.allFinite(),"connected point is finite and qualified");
    check(p.joint_margin_rad&&*p.joint_margin_rad>=0.,"connected point has valid native margin");
    check(p.residual&&p.residual->head<3>().norm()<=opt.projection.position_tolerance_m&&
      p.residual->tail<3>().norm()<=opt.projection.rotation_tolerance_rad,
      "connected point passes separate residual norms");
    check(p.collision&&p.collision->complete&&!p.collision->self_collision&&
      !p.collision->world_collision&&p.collision->contacts.empty(),
      "synthetic connected point has complete free collision evidence");
  }
  for(std::size_t k=0;k<r.leaf_edges.size();++k)
  {
    const auto& edge=r.leaf_edges[k];
    const auto d=(r.checked_points.at(r.verified_prefix[k+1]).q-
                  r.checked_points.at(r.verified_prefix[k]).q).eval();
    check(edge.accepted&&edge.from==r.verified_prefix[k]&&edge.to==r.verified_prefix[k+1],
      "leaf edges follow traversal order rather than checked-point insertion order");
    check(d.norm()<=opt.adjacent_l2_limit_rad&&d.cwiseAbs().maxCoeff()<=opt.adjacent_max_abs_limit_rad,
      "projected adjacent q obey both continuity limits");
  }
  finiteReport(r);
}
}

int main()
{
  try
  {
    const auto opt=protocol();
    const auto margin=unrestricted();
    const p4::JointVector zero=p4::JointVector::Zero();
    auto r=p4::connect(zero,zero,flat,margin,clear(),opt);
    successfulPath(r,zero,zero,opt);
    check(r.checked_points.size()==1&&r.projection_calls==0,"identical state needs no midpoint projection");

    // 曲线端点精确闭合；原 TASK04 project 必须实际作 Newton 更新。
    const auto start=curvePoint(-.03),goal=curvePoint(.03);
    r=p4::connect(start,goal,parabola,margin,clear(),opt);
    successfulPath(r,start,goal,opt);
    check(r.projection_calls>0&&r.verified_prefix.size()>2,"near curved states require subdivided connection");
    check(r.checked_points.front().role=="EXACT_START"&&r.checked_points[1].role=="EXACT_GOAL"&&
      !r.checked_points.front().projection&&!r.checked_points[1].projection,
      "caller endpoints validated without projection repair");
    bool newton_used=false;
    for(const auto& p:r.checked_points)
      if(p.projection)
      {
        check(p.projection->status==p4::ProjectionStatus::CONVERGED,
          "successful midpoint consumed only converged original projection");
        newton_used=newton_used||p.projection->accepted_updates>0;
      }
    check(newton_used,"parabolic chord midpoint requires real original Newton updates");
    for(std::size_t k=1;k<r.verified_prefix.size();++k)
      check(r.checked_points[r.verified_prefix[k]].q(6)>r.checked_points[r.verified_prefix[k-1]].q(6),
        "curved path prefix increases along analytic parameter");
    check(r.verified_prefix[1]!=1,"prechecked future goal is not the next connected waypoint");
    const auto repeat=p4::connect(start,goal,parabola,margin,clear(),opt);
    check(repeat.status==r.status&&repeat.verified_prefix==r.verified_prefix&&
      repeat.projection_calls==r.projection_calls&&repeat.checked_points.size()==r.checked_points.size(),
      "deterministic traversal and projection counts repeat");
    for(std::size_t i=0;i<r.checked_points.size();++i)
      check(exact(repeat.checked_points[i].q,r.checked_points[i].q),"deterministic projected q repeats exactly");

    // 合法端点，但中点需要修正且 rank 为零：有限 returned q 不能当成功。
    const auto singular_midpoint=[](const p4::JointVector& q) {
      auto s=parabola(q);
      if(q(6)==0.) s.jacobian.setZero();
      return s;
    };
    r=p4::connect(start,goal,singular_midpoint,margin,clear(),opt);
    check(r.status==p4::ConnectionStatus::PROJECTION_FAILED,"midpoint projection failure rejects whole edge");
    onlyStart(r,start);
    check(r.failed_point&&r.checked_points[*r.failed_point].projection&&
      r.checked_points[*r.failed_point].projection->status==p4::ProjectionStatus::RANK_DEFICIENT,
      "original rank-deficient projection failure preserved");
    check(r.checked_points[*r.failed_point].q.allFinite()&&!r.checked_points[*r.failed_point].qualified,
      "finite failed projection q is not a qualified midpoint");
    check(r.checked_points[1].qualified,"checked goal can be valid but remains unreachable");

    const p4::ConstraintEvaluator throwing_midpoint=[](const p4::JointVector& q) {
      if(q(6)==0.) throw std::runtime_error("intentional midpoint constraint exception");
      return parabola(q);
    };
    r=p4::connect(start,goal,throwing_midpoint,margin,clear(),opt);
    check(r.status==p4::ConnectionStatus::PROJECTION_FAILED&&r.failed_point&&
      r.checked_points[*r.failed_point].projection->status==p4::ProjectionStatus::EVALUATION_ERROR,
      "original projection evaluator exception rejects midpoint connection");
    onlyStart(r,start);
    const p4::JointMarginEvaluator throwing_margin=[](const p4::JointVector& q) {
      if(q(6)==0.) throw std::runtime_error("intentional midpoint bounds exception");
      return 10.-q.cwiseAbs().maxCoeff();
    };
    r=p4::connect(start,goal,parabola,throwing_margin,clear(),opt);
    check(r.status==p4::ConnectionStatus::PROJECTION_FAILED&&r.failed_point&&
      r.checked_points[*r.failed_point].projection->status==p4::ProjectionStatus::BOUNDS_ERROR,
      "original projection bounds exception rejects midpoint connection");
    onlyStart(r,start);

    const p4::JointMarginEvaluator small_bounds=[](const p4::JointVector& q) {
      return .02-q.cwiseAbs().maxCoeff();
    };
    const auto outside=freePoint(.03);
    r=p4::connect(zero,outside,flat,small_bounds,clear(),opt);
    check(r.status==p4::ConnectionStatus::JOINT_LIMIT&&r.projection_calls==0,
      "out-of-bounds original endpoint rejected before projection");
    onlyStart(r,zero);
    check(exact(r.checked_points[*r.failed_point].q,outside),"invalid endpoint is not clamped");
    const auto exact_bound=freePoint(.02);
    r=p4::connect(exact_bound,exact_bound,flat,small_bounds,clear(),opt);
    check(r.status==p4::ConnectionStatus::CONNECTED,"exact original bound is legal");
    r=p4::connect(zero,freePoint(.02+1e-12),flat,small_bounds,clear(),opt);
    check(r.status==p4::ConnectionStatus::JOINT_LIMIT,"native bound has no epsilon relaxation");

    // 端点和 seed 都合法；full Newton proposal 会越界，不能 clamp 或使用 seed。
    const p4::JointMarginEvaluator lower_bound=[](const p4::JointVector& q) {
      return q(0)-.0008;
    };
    r=p4::connect(start,goal,parabola,lower_bound,clear(),opt);
    check(r.status==p4::ConnectionStatus::PROJECTION_FAILED,"out-of-bounds Newton proposal rejects connection");
    onlyStart(r,start);
    const auto& rejected=*r.checked_points[*r.failed_point].projection;
    check(rejected.status==p4::ProjectionStatus::UPDATE_JOINT_LIMIT&&rejected.accepted_updates==0,
      "original full-step bound failure not converted to connector success");
    check(rejected.history.size()==1&&rejected.history[0].proposed_q&&
      (*rejected.history[0].proposed_q)(0)<.0008&&!rejected.history[0].update_accepted,
      "rejected proposal retained as evidence without acceptance");

    // 独立两种单位及三个分量的 norm，不使用 mixed norm 或逐分量门限。
    for(int row:{0,3})
    {
      auto bad_goal=freePoint(.03); bad_goal(row)=1.1e-8;
      r=p4::connect(zero,bad_goal,flat,margin,clear(),opt);
      check(r.status==p4::ConnectionStatus::CLOSURE&&r.projection_calls==0,
        "invalid original position/rotation endpoint never repaired");
      onlyStart(r,zero);
      check(exact(r.requested_goal,bad_goal)&&exact(r.checked_points[*r.failed_point].q,bad_goal),
        "original failed goal remains exact without silent snap");
      auto vector_norm=zero; vector_norm(row)=.8e-8; vector_norm(row+1)=.8e-8;
      r=p4::connect(vector_norm,vector_norm,flat,margin,clear(),opt);
      check(r.status==p4::ConnectionStatus::CLOSURE,"three-component norm rejects individually small residual rows");
    }
    auto independent=zero; independent(0)=.9e-8; independent(3)=.9e-8;
    r=p4::connect(independent,independent,flat,margin,clear(),opt);
    check(r.status==p4::ConnectionStatus::CONNECTED,"each separate residual norm passes despite larger mixed norm");
    check(exact(r.checked_points[r.verified_prefix.back()].q,independent),
      "already-qualified near-closed endpoint is not normalized or projected");

    for(bool self:{false,true})
    {
      const p4::CollisionEvaluator at_midpoint=[self](const p4::JointVector& q) {
        return q(6)==0.?colliding(self):freeEvidence();
      };
      r=p4::connect(freePoint(-.04),freePoint(.04),flat,margin,at_midpoint,opt);
      check(r.status==p4::ConnectionStatus::COLLISION,"self/world collision at valid midpoint rejects edge");
      onlyStart(r,freePoint(-.04));
      const auto& e=*r.checked_points[*r.failed_point].collision;
      check(e.complete&&e.contacts.size()==1&&e.contacts[0].body_b=="synthetic_obstacle"&&
        e.contacts[0].penetration_depth_m==.001,"raw synthetic rejected collision evidence preserved");
    }
    const p4::CollisionEvaluator later_collision=[](const p4::JointVector& q) {
      return q(6)>.029&&q(6)<.031?colliding(false):freeEvidence();
    };
    r=p4::connect(zero,freePoint(.04),flat,margin,later_collision,opt);
    check(r.status==p4::ConnectionStatus::COLLISION&&r.verified_prefix.size()>1,
      "later collision preserves completed ordered prefix");
    check(r.checked_points[r.verified_prefix.back()].q(6)==.02,
      "connected prefix stops at completed left half before right failure");
    for(const auto i:r.verified_prefix)
      check(r.checked_points[i].qualified&&r.checked_points[i].q(6)<=.02&&i!=1&&i!=*r.failed_point,
        "future prechecked goal and rejected midpoint never appear in failure prefix");
    check(r.checked_points[1].qualified&&r.checked_points[1].role=="EXACT_GOAL",
      "prechecked future endpoint is logged separately from reachability");

    const p4::CollisionEvaluator throws=[](const p4::JointVector&)->p4::CollisionEvidence {
      throw std::runtime_error("intentional synthetic checker exception");
    };
    r=p4::connect(zero,zero,flat,margin,throws,opt);
    check(r.status==p4::ConnectionStatus::COLLISION_UNAVAILABLE&&r.verified_prefix.empty(),
      "throwing collision checker fails closed before any prefix");
    const p4::CollisionEvaluator incomplete=[](const p4::JointVector&) {
      auto e=freeEvidence(); e.complete=false; return e;
    };
    r=p4::connect(zero,zero,flat,margin,incomplete,opt);
    check(r.status==p4::ConnectionStatus::COLLISION_UNAVAILABLE,"incomplete free result is not collision proof");
    const p4::CollisionEvaluator contradictory=[](const p4::JointVector&) {
      auto e=colliding(false); e.world_collision=false; return e;
    };
    r=p4::connect(zero,zero,flat,margin,contradictory,opt);
    check(r.status==p4::ConnectionStatus::COLLISION_UNAVAILABLE,"free flags plus contacts fail closed");

    r=p4::connect(curvePoint(-.2),curvePoint(.2),parabola,margin,clear(),opt);
    check(r.status==p4::ConnectionStatus::PROJECTION_JUMP,"large converged midpoint correction rejects locality jump");
    onlyStart(r,curvePoint(-.2));
    const auto& jumped=r.checked_points[*r.failed_point];
    check(jumped.projection&&jumped.projection->status==p4::ProjectionStatus::CONVERGED&&
      jumped.projection_correction_l2_rad&&*jumped.projection_correction_l2_rad>opt.projection_correction_limit_rad&&
      !jumped.qualified&&!jumped.collision,"jump gate precedes collision qualification without discarding projection evidence");

    // 以下 toy options 仅覆盖独立有限门禁，不改变预声明实际试验参数。
    for(bool l2:{true,false})
    {
      auto toy=opt;
      if(l2) toy.adjacent_l2_limit_rad=.007;
      else toy.adjacent_max_abs_limit_rad=.007;
      r=p4::connect(zero,freePoint(.008),flat,margin,clear(),toy);
      check(r.status==p4::ConnectionStatus::CONTINUITY&&r.projection_calls==0,
        "leaf checks projected L2 and max-absolute adjacency independently");
      onlyStart(r,zero);
      check(r.leaf_edges.size()==1&&!r.leaf_edges[0].accepted,
        "failed adjacency edge recorded without appending prechecked goal");
    }
    auto toy=opt; toy.max_depth=1;
    r=p4::connect(zero,freePoint(.03),flat,margin,clear(),toy);
    check(r.status==p4::ConnectionStatus::DEPTH_LIMIT&&r.projection_calls==1,
      "RBS depth exhausted without retry or changed resolution");
    onlyStart(r,zero);
    toy=opt; toy.max_projections=1;
    r=p4::connect(zero,freePoint(.03),flat,margin,clear(),toy);
    check(r.status==p4::ConnectionStatus::PROJECTION_BUDGET&&r.projection_calls==1,
      "midpoint budget checked before additional projection");
    onlyStart(r,zero);
    toy=opt; toy.max_path_points=2;
    r=p4::connect(zero,freePoint(.03),flat,margin,clear(),toy);
    check(r.status==p4::ConnectionStatus::PATH_BUDGET&&r.verified_prefix.size()==2,
      "path budget retains only previously completed prefix");
    check(r.checked_points[r.verified_prefix.back()].q(6)<.03&&r.verified_prefix.back()!=1,
      "path budget cannot silently append original goal");

    const double nan=std::numeric_limits<double>::quiet_NaN();
    const double inf=std::numeric_limits<double>::infinity();
    for(double bad:{nan,inf})
      for(int joint:{0,13})
      {
        auto invalid=zero; invalid(joint)=bad;
        r=p4::connect(invalid,zero,flat,margin,clear(),opt);
        check(r.status==p4::ConnectionStatus::INVALID_INPUT&&r.verified_prefix.empty(),
          "nonfinite start is rejected before prefix qualification");
        r=p4::connect(zero,invalid,flat,margin,clear(),opt);
        check(r.status==p4::ConnectionStatus::INVALID_INPUT,"nonfinite goal cannot use identical-state shortcut");
        onlyStart(r,zero);
      }
    for(bool bad_j:{false,true})
    {
      const p4::ConstraintEvaluator invalid=[bad_j,nan](const p4::JointVector& q) {
        auto s=flat(q); if(bad_j) s.jacobian(0,0)=nan; else s.residual(0)=nan; return s;
      };
      r=p4::connect(zero,zero,invalid,margin,clear(),opt);
      check(r.status==p4::ConnectionStatus::EVALUATION_ERROR,"nonfinite original C or Jc rejected");
    }
    const p4::JointMarginEvaluator bad_margin=[nan](const p4::JointVector&) {return nan;};
    r=p4::connect(zero,zero,flat,bad_margin,clear(),opt);
    check(r.status==p4::ConnectionStatus::EVALUATION_ERROR,"nonfinite native bound margin rejected");
    const p4::ConstraintEvaluator bad_chart=[](const p4::JointVector&)->p4::ClosureSample {
      common_geometry::so3LeftJacobianInverse({common_geometry::pi,0.,0.});
      throw std::runtime_error("unreachable accepted pi chart");
    };
    r=p4::connect(zero,zero,bad_chart,margin,clear(),opt);
    check(r.status==p4::ConnectionStatus::EVALUATION_ERROR,"SO3 pi chart failure not ignored");

    int callback_count=0;
    const p4::ConstraintEvaluator counted=[&](const p4::JointVector& q) {++callback_count; return flat(q);};
    for(int field=0;field<21;++field)
    {
      auto invalid=opt;
      switch(field)
      {
        case 0: invalid.leaf_resolution_rad=0.; break;
        case 1: invalid.adjacent_l2_limit_rad=-1.; break;
        case 2: invalid.adjacent_max_abs_limit_rad=nan; break;
        case 3: invalid.projection_correction_limit_rad=inf; break;
        case 4: invalid.max_depth=0; break;
        case 5: invalid.max_depth=65; break;
        case 6: invalid.max_projections=0; break;
        case 7: invalid.max_path_points=1; break;
        case 8: invalid.projection.position_tolerance_m=0.; break;
        case 9: invalid.projection.rotation_tolerance_rad=-1.; break;
        case 10: invalid.projection.position_tolerance_m=inf; break;
        case 11: invalid.projection.max_iterations=0; break;
        case 12: invalid.projection.svd_absolute_cutoff=-1.; break;
        case 13: invalid.projection.svd_absolute_cutoff=nan; break;
        case 14: invalid.projection.svd_relative_cutoff=0.; break;
        case 15: invalid.projection.svd_relative_cutoff=1.; break;
        case 16: invalid.projection.svd_relative_cutoff=2.; break;
        case 17: invalid.projection.svd_relative_cutoff=nan; break;
        case 18: invalid.projection.stagnation_step_rad=-1.; break;
        case 19: invalid.projection.stagnation_step_rad=inf; break;
        case 20: invalid.projection.rotation_tolerance_rad=nan; break;
      }
      callback_count=0;
      r=p4::connect(zero,zero,counted,margin,clear(),invalid);
      check(r.status==p4::ConnectionStatus::INVALID_OPTIONS&&callback_count==0&&r.checked_points.empty(),
        "invalid explicit local or original projection options rejected before callbacks");
    }
    r=p4::connect(zero,zero,p4::ConstraintEvaluator{},margin,clear(),opt);
    check(r.status==p4::ConnectionStatus::INVALID_OPTIONS,"missing C/Jc callback rejected");
    r=p4::connect(zero,zero,flat,p4::JointMarginEvaluator{},clear(),opt);
    check(r.status==p4::ConnectionStatus::INVALID_OPTIONS,"missing native bounds callback rejected");
    r=p4::connect(zero,zero,flat,margin,p4::CollisionEvaluator{},opt);
    check(r.status==p4::ConnectionStatus::INVALID_OPTIONS,"missing collision callback cannot claim success");

    auto allowed_zero=opt;
    allowed_zero.projection.svd_absolute_cutoff=0.;
    allowed_zero.projection.stagnation_step_rad=0.;
    r=p4::connect(start,goal,parabola,margin,clear(),allowed_zero);
    successfulPath(r,start,goal,allowed_zero);
    check(r.projection_calls>0,"original allowed zero absolute cutoff and stagnation still permit NR");

    std::cout<<"TASK05 SYNTHETIC LOCAL CONNECTION PASS checks="<<checks
      <<" original NR/RBS; synthetic collision interface only; no FCL/physics proof\n";
    return 0;
  }
  catch(const std::exception& e)
  {
    std::cerr<<"TASK05 SYNTHETIC LOCAL CONNECTION FAIL after checks="<<checks<<": "<<e.what()<<'\n';
    return 1;
  }
}
