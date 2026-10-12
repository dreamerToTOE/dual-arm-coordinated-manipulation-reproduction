#include "baselines/p4_closed_chain/constrained_rrtconnect.hpp"
#include <algorithm>
#include <chrono>
#include <cmath>
#include <limits>
#include <random>
#include <stdexcept>
#include <utility>

namespace p4
{
const char* statusName(PlannerStatus s)
{
  switch(s)
  {
#define P4_CASE(x) case PlannerStatus::x: return #x
    P4_CASE(SUCCESS); P4_CASE(INVALID_OPTIONS); P4_CASE(INVALID_INPUT);
    P4_CASE(START_REJECTED); P4_CASE(GOAL_REJECTED); P4_CASE(ITERATION_LIMIT);
    P4_CASE(NODE_LIMIT); P4_CASE(TIME_LIMIT); P4_CASE(INTERNAL_ERROR);
#undef P4_CASE
  }
  return "UNKNOWN";
}
const char* statusName(PlannerTree s) { return s==PlannerTree::START ? "START" : "GOAL"; }
const char* statusName(GrowthMode s) { return s==GrowthMode::EXTEND ? "EXTEND" : "CONNECT"; }
const char* statusName(AttemptStatus s)
{
  switch(s)
  {
#define P4_CASE(x) case AttemptStatus::x: return #x
    P4_CASE(ACCEPTED); P4_CASE(PROJECTION_FAILED); P4_CASE(PROJECTION_JUMP);
    P4_CASE(EXTENSION_JUMP); P4_CASE(NO_PROGRESS); P4_CASE(CONNECTION_REJECTED);
    P4_CASE(NODE_LIMIT); P4_CASE(TIME_LIMIT); P4_CASE(INVALID_CANDIDATE);
#undef P4_CASE
  }
  return "UNKNOWN";
}
namespace
{
using Clock=std::chrono::steady_clock;
bool positive(double x) { return std::isfinite(x) && x>0.; }
bool exact(const JointVector& a,const JointVector& b) { return (a.array()==b.array()).all(); }
bool validOptions(const PlannerOptions& o)
{
  return positive(o.raw_steer_range_rad) &&
    positive(o.candidate_projection_correction_l2_limit_rad) &&
    positive(o.accepted_extension_l2_limit_rad) &&
    std::isfinite(o.minimum_progress_rad) && o.minimum_progress_rad>=0. &&
    o.max_nodes>=2 && positive(o.max_compute_wall_sec);
}
struct GrowthResult
{
  std::size_t node;
  bool reached{false}, terminated{false};
};

struct Search
{
  const PlannerOptions& o;
  PlannerResult& r;
  Clock::time_point begin;
  std::mt19937_64 rng;
  ConstraintEvaluator constraint;
  JointMarginEvaluator margin;
  CollisionEvaluator collision;

  Search(const PlannerOptions& options,PlannerResult& result,Clock::time_point start,
         const ConstraintEvaluator& evaluate,const JointMarginEvaluator& native_margin,
         const CollisionEvaluator& evaluate_collision)
    :o(options),r(result),begin(start),rng(options.seed)
  {
    constraint=[this,&evaluate](const JointVector& q) {
      ++r.counters.constraint_evaluations; return evaluate(q);
    };
    margin=[this,&native_margin](const JointVector& q) {
      ++r.counters.margin_evaluations;
      const double original=native_margin(q);
      // Both supplied bounds and this callback describe the same native position bounds.
      // Fail closed if a caller supplies an inconsistent box; no tolerance/clamping/wrapping.
      if(!std::isfinite(original)) return original;
      const double box_margin=std::min((q-r.native_lower).minCoeff(),
                                      (r.native_upper-q).minCoeff());
      return std::min(original,box_margin);
    };
    collision=[this,&evaluate_collision](const JointVector& q) {
      ++r.counters.collision_queries;
      try
      {
        auto evidence=evaluate_collision(q);
        if(evidence.self_collision || evidence.world_collision)
          ++r.counters.collision_positive_queries;
        if(!evidence.complete ||
           (!evidence.self_collision && !evidence.world_collision && !evidence.contacts.empty()))
          ++r.counters.collision_unavailable_queries;
        return evidence;
      }
      catch(...) { ++r.counters.collision_unavailable_queries; throw; }
    };
  }
  double elapsed() const { return std::chrono::duration<double>(Clock::now()-begin).count(); }
  bool timedOut() const { return elapsed()>=o.max_compute_wall_sec; }
  std::size_t nodeCount() const { return r.start_tree.size()+r.goal_tree.size(); }
  std::vector<PlannerNode>& tree(PlannerTree t)
    { return t==PlannerTree::START ? r.start_tree : r.goal_tree; }
  const std::vector<PlannerNode>& tree(PlannerTree t) const
    { return t==PlannerTree::START ? r.start_tree : r.goal_tree; }
  bool terminate(PlannerStatus status,const std::string& reason)
    { r.status=status; r.reason=reason; return true; }
  bool budget()
  {
    if(timedOut()) return terminate(PlannerStatus::TIME_LIMIT,"Declared compute wall budget exhausted");
    if(nodeCount()>=o.max_nodes)
      return terminate(PlannerStatus::NODE_LIMIT,"Declared total tree-node budget exhausted");
    return false;
  }
  JointVector sample()
  {
    JointVector q;
    for(Eigen::Index j=0;j<q.size();++j)
    {
      // [ENGINEERING] Exact declared binary53 mapping; no implementation-defined distribution.
      const double u=static_cast<double>(rng()>>11)*0x1.0p-53;
      ++r.counters.rng_draws;
      q(j)=r.native_lower(j)+(r.native_upper(j)-r.native_lower(j))*u;
    }
    ++r.counters.samples; r.sampled_targets.push_back(q); return q;
  }
  std::size_t nearest(PlannerTree t,const JointVector& target)
  {
    ++r.counters.nearest_queries;
    const auto& nodes=tree(t);
    if(nodes.empty()) throw std::logic_error("Nearest query on empty tree");
    std::size_t best=0;
    double best_distance=std::numeric_limits<double>::infinity();
    for(std::size_t k=0;k<nodes.size();++k)
    {
      ++r.counters.nearest_distance_evaluations;
      const double d=(nodes[k].q-target).norm();
      if(!std::isfinite(d)) throw std::logic_error("Nonfinite nearest-neighbor distance");
      // Strict comparison retains the earliest inserted node on exact distance ties.
      if(d<best_distance) { best_distance=d; best=k; }
    }
    return best;
  }
  ConnectionResult connection(const JointVector& a,const JointVector& b,bool root)
  {
    if(root) ++r.counters.root_connection_calls;
    else ++r.counters.tree_edge_connection_calls;
    auto result=connect(a,b,constraint,margin,collision,o.local_connection);
    r.counters.rbs_midpoint_projection_calls+=result.projection_calls;
    for(const auto& point:result.checked_points)
      if(point.projection && point.projection->status!=ProjectionStatus::CONVERGED)
        ++r.counters.rbs_midpoint_projection_failures;
    if(result.status!=ConnectionStatus::CONNECTED) ++r.counters.local_connection_rejections;
    return result;
  }
  void failurePrefix(std::size_t attempt,const ConnectionResult& result)
  {
    r.failed_prefix_attempt=attempt; r.failed_prefix.clear();
    for(const auto k:result.verified_prefix)
    {
      const auto& point=result.checked_points.at(k);
      if(!point.qualified) throw std::logic_error("Unqualified point in diagnostic prefix");
      r.failed_prefix.push_back(point.q);
    }
  }
  GrowthResult grow(PlannerTree t,std::size_t parent,const JointVector& target,
                    GrowthMode mode,std::size_t attempts,std::size_t iteration)
  {
    for(std::size_t step=0;step<attempts;++step)
    {
      if(budget()) return {parent,false,true};
      // Copy before insertion: the vectors may reallocate when a node is accepted.
      const JointVector from=tree(t).at(parent).q;
      const double d=(target-from).norm();
      PlannerAttempt a; a.tree=t; a.mode=mode; a.iteration=iteration;
      a.growth_attempt=step; a.nearest_node=parent; a.raw_target=target;
      a.target_is_existing=mode==GrowthMode::CONNECT;
      a.raw_target_within_range=d<=o.raw_steer_range_rad;
      a.raw_steer=a.raw_target_within_range ? target :
        (from+(o.raw_steer_range_rad/d)*(target-from)).eval();
      ++r.counters.growth_attempts;
      const std::size_t attempt_index=r.attempts.size();
      const auto reject=[&](AttemptStatus status,const std::string& reason,bool stop=false) {
        a.status=status; a.reason=reason;
        if(a.connection) failurePrefix(attempt_index,*a.connection);
        r.attempts.push_back(std::move(a));
        return GrowthResult{parent,false,stop};
      };
      if(mode==GrowthMode::EXTEND || !a.raw_target_within_range)
      {
        ++r.counters.candidate_projection_calls;
        a.projection=project(a.raw_steer,constraint,margin,o.local_connection.projection);
        a.candidate=a.projection->projected_q;
        a.projection_correction_l2_rad=(*a.candidate-a.raw_steer).norm();
        if(a.projection->status!=ProjectionStatus::CONVERGED)
          ++r.counters.candidate_projection_failures;
        if(timedOut())
        {
          terminate(PlannerStatus::TIME_LIMIT,"Compute wall budget exhausted after candidate projection");
          return reject(AttemptStatus::TIME_LIMIT,r.reason,true);
        }
        if(a.projection->status!=ProjectionStatus::CONVERGED)
          return reject(AttemptStatus::PROJECTION_FAILED,
            std::string(statusName(a.projection->status))+": "+a.projection->reason);
        if(!std::isfinite(*a.projection_correction_l2_rad) ||
           *a.projection_correction_l2_rad>o.candidate_projection_correction_l2_limit_rad)
        {
          ++r.counters.projection_jump_rejections;
          return reject(AttemptStatus::PROJECTION_JUMP,"Candidate projection exceeds declared correction bound");
        }
      }
      else a.candidate=target; // Exact final target from the other tree; never project/snap it.

      const double extension=(*a.candidate-from).norm();
      a.accepted_extension_l2_rad=extension;
      if(!a.candidate->allFinite() || !std::isfinite(extension))
      {
        ++r.counters.invalid_candidate_rejections;
        return reject(AttemptStatus::INVALID_CANDIDATE,"Nonfinite candidate or extension distance");
      }
      if(extension>o.accepted_extension_l2_limit_rad)
      {
        ++r.counters.extension_jump_rejections;
        return reject(AttemptStatus::EXTENSION_JUMP,"Projected extension exceeds declared step bound");
      }
      if(extension<=o.minimum_progress_rad)
      {
        ++r.counters.no_progress_rejections;
        return reject(AttemptStatus::NO_PROGRESS,"Candidate does not make declared minimum progress");
      }
      a.connection=connection(from,*a.candidate,false);
      if(timedOut())
      {
        terminate(PlannerStatus::TIME_LIMIT,"Compute wall budget exhausted after local connection");
        return reject(AttemptStatus::TIME_LIMIT,r.reason,true);
      }
      if(a.connection->status!=ConnectionStatus::CONNECTED)
        return reject(AttemptStatus::CONNECTION_REJECTED,
          std::string(statusName(a.connection->status))+": "+a.connection->reason);

      const std::size_t added=tree(t).size();
      tree(t).push_back({*a.candidate,parent,attempt_index});
      if(t==PlannerTree::START) ++r.counters.accepted_start_edges;
      else ++r.counters.accepted_goal_edges;
      a.status=AttemptStatus::ACCEPTED; a.reason="Candidate and whole unchanged TASK05 edge qualified";
      a.added_node=added; a.reached=a.raw_target_within_range;
      const bool reached=a.reached;
      r.attempts.push_back(std::move(a)); parent=added;
      if(reached) return {parent,true,false};
    }
    return {parent,false,false};
  }
  const ConnectionPoint& evidence(const PlannerPathPoint& p) const
  {
    if(p.attempt) return r.attempts.at(*p.attempt).connection->checked_points.at(p.checked_point);
    const auto& root=p.tree==PlannerTree::START ? r.start_root : r.goal_root;
    return root->checked_points.at(p.checked_point);
  }
  std::vector<std::size_t> ancestors(PlannerTree t,std::size_t node) const
  {
    const auto& nodes=tree(t); std::vector<std::size_t> chain;
    for(std::size_t count=0;count<nodes.size();++count)
    {
      const auto& current=nodes.at(node); chain.push_back(node);
      if(!current.parent)
      {
        if(node!=0 || current.incoming_attempt)
          throw std::logic_error("Malformed root in solution backtracking");
        return chain;
      }
      if(!current.incoming_attempt || *current.parent>=node)
        throw std::logic_error("Malformed/cyclic solution parent edge");
      node=*current.parent;
    }
    throw std::logic_error("Solution ancestry did not reach root");
  }
  void appendEdge(const PlannerPathEdge& edge)
  {
    const auto& nodes=tree(edge.tree);
    const auto& a=r.attempts.at(edge.attempt);
    if(a.status!=AttemptStatus::ACCEPTED || !a.connection || a.tree!=edge.tree ||
       a.nearest_node!=edge.parent || !a.added_node || *a.added_node!=edge.child ||
       a.connection->status!=ConnectionStatus::CONNECTED ||
       !exact(a.connection->requested_start,nodes.at(edge.parent).q) ||
       !exact(a.connection->requested_goal,nodes.at(edge.child).q))
      throw std::logic_error("Returned path edge lacks matching accepted TASK05 evidence");
    const auto& c=*a.connection;
    if(c.verified_prefix.empty() || c.leaf_edges.size()+1!=c.verified_prefix.size())
      throw std::logic_error("Malformed accepted local prefix");
    for(std::size_t k=0;k<c.leaf_edges.size();++k)
      if(!c.leaf_edges[k].accepted || c.leaf_edges[k].from!=c.verified_prefix[k] ||
         c.leaf_edges[k].to!=c.verified_prefix[k+1])
        throw std::logic_error("Returned local prefix lacks ordered accepted leaf edges");
    const auto checked=[&](std::size_t k) {
      return c.verified_prefix.at(edge.reversed ? c.verified_prefix.size()-1-k : k);
    };
    if(!exact(c.checked_points.at(checked(0)).q,r.dense_path.back()))
      throw std::logic_error("Dense path does not meet its next exact local endpoint");
    for(std::size_t k=1;k<c.verified_prefix.size();++k)
    {
      const std::size_t i=checked(k); const auto& point=c.checked_points.at(i);
      if(!point.qualified || !point.residual || !point.joint_margin_rad || !point.collision ||
         !point.q.allFinite() || !point.residual->allFinite() ||
         !std::isfinite(*point.joint_margin_rad) || *point.joint_margin_rad<0. ||
         !point.collision->complete || point.collision->self_collision ||
         point.collision->world_collision || !point.collision->contacts.empty())
        throw std::logic_error("Unqualified local point cannot enter returned solution");
      r.dense_path.push_back(point.q);
      r.dense_path_evidence.push_back({point.q,edge.tree,edge.attempt,i});
    }
  }
  void assemble(std::size_t start_node,std::size_t goal_node)
  {
    if(!exact(r.start_tree.at(start_node).q,r.goal_tree.at(goal_node).q))
      throw std::logic_error("Two trees did not join at an identical existing target");
    r.meeting_start_node=start_node; r.meeting_goal_node=goal_node;
    auto left=ancestors(PlannerTree::START,start_node);
    const auto right=ancestors(PlannerTree::GOAL,goal_node);
    std::reverse(left.begin(),left.end());
    for(const auto k:left) r.path_milestones.push_back(r.start_tree.at(k).q);
    for(std::size_t k=1;k<right.size();++k) r.path_milestones.push_back(r.goal_tree.at(right[k]).q);
    for(std::size_t k=1;k<left.size();++k)
      r.path_edges.push_back({PlannerTree::START,left[k-1],left[k],
        *r.start_tree.at(left[k]).incoming_attempt,false});
    for(std::size_t k=1;k<right.size();++k)
      r.path_edges.push_back({PlannerTree::GOAL,right[k],right[k-1],
        *r.goal_tree.at(right[k-1]).incoming_attempt,true});
    const std::size_t root_point=r.start_root->verified_prefix.at(0);
    r.dense_path.push_back(r.start_root->checked_points.at(root_point).q);
    r.dense_path_evidence.push_back({r.dense_path.back(),PlannerTree::START,{},root_point});
    for(const auto& edge:r.path_edges) appendEdge(edge);
    if(r.dense_path.empty() || !exact(r.dense_path.front(),r.requested_start) ||
       !exact(r.dense_path.back(),r.requested_goal))
      throw std::logic_error("Solution failed exact caller endpoint preservation");
    PlannerPathMetrics m; m.minimum_native_joint_margin_rad=std::numeric_limits<double>::infinity();
    double position_squares=0.,rotation_squares=0.;
    for(std::size_t k=0;k<r.dense_path.size();++k)
    {
      const auto& point=evidence(r.dense_path_evidence.at(k));
      const double position=point.residual->head<3>().norm(), rotation=point.residual->tail<3>().norm();
      m.maximum_position_residual_m=std::max(m.maximum_position_residual_m,position);
      m.maximum_rotation_residual_rad=std::max(m.maximum_rotation_residual_rad,rotation);
      m.minimum_native_joint_margin_rad=std::min(m.minimum_native_joint_margin_rad,*point.joint_margin_rad);
      position_squares+=position*position; rotation_squares+=rotation*rotation;
      if(k)
      {
        const JointVector delta=r.dense_path[k]-r.dense_path[k-1];
        m.joint_path_length_rad+=delta.norm();
        m.maximum_adjacent_l2_rad=std::max(m.maximum_adjacent_l2_rad,delta.norm());
        m.maximum_adjacent_max_abs_rad=std::max(m.maximum_adjacent_max_abs_rad,delta.cwiseAbs().maxCoeff());
      }
    }
    m.rms_position_residual_m=std::sqrt(position_squares/static_cast<double>(r.dense_path.size()));
    m.rms_rotation_residual_rad=std::sqrt(rotation_squares/static_cast<double>(r.dense_path.size()));
    for(std::size_t k=1;k<r.path_milestones.size();++k)
      m.milestone_path_length_rad+=(r.path_milestones[k]-r.path_milestones[k-1]).norm();
    r.path_metrics=m;
  }
  void clearSolution()
  {
    r.meeting_start_node.reset(); r.meeting_goal_node.reset(); r.path_edges.clear();
    r.path_milestones.clear(); r.dense_path.clear(); r.dense_path_evidence.clear(); r.path_metrics.reset();
  }
  void run()
  {
    r.start_root=connection(r.requested_start,r.requested_start,true);
    if(timedOut()) { terminate(PlannerStatus::TIME_LIMIT,"Compute wall budget exhausted validating exact start"); return; }
    if(r.start_root->status!=ConnectionStatus::CONNECTED)
    {
      terminate(r.start_root->status==ConnectionStatus::INVALID_OPTIONS ?
        PlannerStatus::INVALID_OPTIONS : PlannerStatus::START_REJECTED,
        std::string(statusName(r.start_root->status))+": "+r.start_root->reason); return;
    }
    r.start_tree.push_back({r.requested_start,{}, {}});
    r.goal_root=connection(r.requested_goal,r.requested_goal,true);
    if(timedOut()) { terminate(PlannerStatus::TIME_LIMIT,"Compute wall budget exhausted validating exact goal"); return; }
    if(r.goal_root->status!=ConnectionStatus::CONNECTED)
    {
      terminate(r.goal_root->status==ConnectionStatus::INVALID_OPTIONS ?
        PlannerStatus::INVALID_OPTIONS : PlannerStatus::GOAL_REJECTED,
        std::string(statusName(r.goal_root->status))+": "+r.goal_root->reason); return;
    }
    r.goal_tree.push_back({r.requested_goal,{}, {}});
    for(std::size_t iteration=0;iteration<o.max_iterations;++iteration)
    {
      if(budget()) return;
      ++r.counters.iterations;
      const PlannerTree primary=iteration%2==0 ? PlannerTree::START : PlannerTree::GOAL;
      const PlannerTree secondary=primary==PlannerTree::START ? PlannerTree::GOAL : PlannerTree::START;
      const JointVector target=sample();
      const auto first=grow(primary,nearest(primary,target),target,GrowthMode::EXTEND,o.extend_attempts,iteration);
      if(first.terminated) return;
      // Source behavior: even a trapped first grow is followed by the opposite-tree connect.
      const JointVector existing=tree(primary).at(first.node).q;
      const auto second=grow(secondary,nearest(secondary,existing),existing,GrowthMode::CONNECT,o.connect_attempts,iteration);
      if(second.terminated) return;
      if(second.reached)
      {
        const std::size_t start_node=primary==PlannerTree::START ? first.node : second.node;
        const std::size_t goal_node=primary==PlannerTree::GOAL ? first.node : second.node;
        assemble(start_node,goal_node);
        if(timedOut())
        { clearSolution(); terminate(PlannerStatus::TIME_LIMIT,"Compute wall budget exhausted assembling qualified path"); return; }
        terminate(PlannerStatus::SUCCESS,"Exact trees joined through qualified unchanged TASK05 edges"); return;
      }
    }
    terminate(PlannerStatus::ITERATION_LIMIT,"Declared outer-iteration budget exhausted");
  }
};
} // namespace

PlannerResult plan(const JointVector& start,const JointVector& goal,
                   const JointVector& lower,const JointVector& upper,
                   const ConstraintEvaluator& constraint,const JointMarginEvaluator& margin,
                   const CollisionEvaluator& collision,const PlannerOptions& o)
{
  const auto begin=Clock::now();
  PlannerResult r; r.requested_start=start; r.requested_goal=goal;
  r.native_lower=lower; r.native_upper=upper; r.seed=o.seed; r.options=o;
  if(!validOptions(o) || !constraint || !margin || !collision)
  { r.status=PlannerStatus::INVALID_OPTIONS; r.reason="Invalid explicit planner options/callbacks"; }
  else if(!start.allFinite() || !goal.allFinite())
  { r.status=PlannerStatus::INVALID_INPUT; r.reason="Caller endpoints must contain finite 14D joint positions"; }
  else if(!lower.allFinite() || !upper.allFinite() || !(upper-lower).allFinite() ||
          !(upper.array()>lower.array()).all())
  { r.status=PlannerStatus::INVALID_INPUT; r.reason="Native sampling box must have finite strictly ordered 14D bounds"; }
  else
  {
    Search search{o,r,begin,constraint,margin,collision};
    try { search.run(); }
    catch(const std::exception& e)
    { search.clearSolution(); r.status=PlannerStatus::INTERNAL_ERROR; r.reason=e.what(); }
  }
  r.compute_wall_time_sec=std::chrono::duration<double>(Clock::now()-begin).count();
  return r;
}
} // namespace p4
