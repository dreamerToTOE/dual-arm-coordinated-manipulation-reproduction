// [ENGINEERING] Synthetic search-orchestration tests only, not FR3/FCL or physics evidence.
// Production TASK04 project() and TASK05 connect() are used without replacement.
#include "baselines/p4_closed_chain/constrained_rrtconnect.hpp"

#include <algorithm>
#include <chrono>
#include <cmath>
#include <iostream>
#include <limits>
#include <random>
#include <stdexcept>
#include <thread>

namespace
{
int checks = 0;

void check(bool condition, const char* name)
{
  if (!condition) throw std::runtime_error(name);
  ++checks;
}

bool exact(const p4::JointVector& a, const p4::JointVector& b)
{
  return (a.array() == b.array()).all();
}

p4::ConstraintJacobian identityRows()
{
  p4::ConstraintJacobian j = p4::ConstraintJacobian::Zero();
  j.leftCols<6>().setIdentity();
  return j;
}

p4::ClosureSample syntheticSample(const p4::Residual& c, const p4::ConstraintJacobian& j)
{
  p4::ClosureSample result;
  result.left_object = Eigen::Isometry3d::Identity();
  result.right_object = Eigen::Isometry3d::Identity();
  result.residual = c;
  result.jacobian = j;
  return result;
}

p4::ClosureSample flat(const p4::JointVector& q)
{
  return syntheticSample(q.head<6>(), identityRows());
}

p4::JointVector point(double t)
{
  p4::JointVector q = p4::JointVector::Zero();
  q(6) = t;
  return q;
}

p4::JointVector lowerBounds()
{
  p4::JointVector q = p4::JointVector::Constant(-.002);
  q.head<6>().setConstant(-.01);
  q(6) = -.4;
  return q;
}

p4::JointVector upperBounds()
{
  return -lowerBounds();
}

p4::JointMarginEvaluator margin(const p4::JointVector& lower, const p4::JointVector& upper)
{
  return [lower, upper](const p4::JointVector& q) {
    return std::min((q - lower).minCoeff(), (upper - q).minCoeff());
  };
}

p4::CollisionEvidence freeEvidence()
{
  p4::CollisionEvidence e;
  e.complete = true;
  e.backend = "SYNTHETIC_INTERFACE_ONLY";
  e.acm_identity = "NO_REAL_ACM";
  e.reason = "Synthetic complete free result";
  return e;
}

p4::CollisionEvidence collisionEvidence()
{
  auto e = freeEvidence();
  e.world_collision = true;
  e.reason = "Intentional synthetic world collision";
  p4::CollisionContact contact;
  contact.body_a = "synthetic_robot";
  contact.body_b = "synthetic_obstacle";
  contact.category = "SYNTHETIC_WORLD";
  contact.penetration_depth_m = .001;
  e.contacts.push_back(contact);
  return e;
}

p4::CollisionEvaluator clear()
{
  return [](const p4::JointVector&) { return freeEvidence(); };
}

p4::PlannerOptions options()
{
  // Fixed synthetic coverage parameters; the committed real-model protocol is untouched.
  return {{{1e-8, 1e-8, 40, 1e-12, 1e-10, 1e-14},
           .01, .01, .01, .02, 12, 1023, 1025},
          7, .05, .25, .45, 1e-12, 2, 100, 200, 20, 5.};
}

const std::vector<p4::PlannerNode>& tree(const p4::PlannerResult& r, p4::PlannerTree side)
{
  return side == p4::PlannerTree::START ? r.start_tree : r.goal_tree;
}

void qualifiedConnection(const p4::ConnectionResult& c,
                         const p4::JointVector& start, const p4::JointVector& goal,
                         const p4::LocalConnectionOptions& o)
{
  check(c.status == p4::ConnectionStatus::CONNECTED, "inserted edge has CONNECTED local evidence");
  check(exact(c.requested_start, start) && exact(c.requested_goal, goal),
        "local evidence preserves exact edge endpoints");
  check(!c.failed_point && !c.verified_prefix.empty(), "connected edge has a complete prefix");
  check(exact(c.checked_points.at(c.verified_prefix.front()).q, start) &&
        exact(c.checked_points.at(c.verified_prefix.back()).q, goal),
        "edge prefix spans its exact requested endpoints");
  check(c.leaf_edges.size() + 1 == c.verified_prefix.size(), "all prefix adjacencies have leaf evidence");
  for (const auto i : c.verified_prefix)
  {
    const auto& p = c.checked_points.at(i);
    check(p.qualified && p.q.allFinite(), "every accepted prefix point is qualified and finite");
    check(p.joint_margin_rad && std::isfinite(*p.joint_margin_rad) && *p.joint_margin_rad >= 0.,
          "every accepted prefix point obeys native bounds");
    check(p.residual && p.residual->allFinite() &&
          p.residual->head<3>().norm() <= o.projection.position_tolerance_m &&
          p.residual->tail<3>().norm() <= o.projection.rotation_tolerance_rad,
          "accepted prefix points pass separate closure norms");
    check(p.collision && p.collision->complete && !p.collision->self_collision &&
          !p.collision->world_collision && p.collision->contacts.empty(),
          "accepted prefix points have complete free synthetic collision evidence");
  }
  for (std::size_t k = 0; k < c.leaf_edges.size(); ++k)
  {
    const auto& edge = c.leaf_edges[k];
    const auto delta = (c.checked_points.at(c.verified_prefix[k + 1]).q -
                        c.checked_points.at(c.verified_prefix[k]).q).eval();
    check(edge.accepted && edge.from == c.verified_prefix[k] && edge.to == c.verified_prefix[k + 1],
          "all accepted leaves follow ordered prefix indices");
    check(delta.norm() <= o.adjacent_l2_limit_rad &&
          delta.cwiseAbs().maxCoeff() <= o.adjacent_max_abs_limit_rad,
          "accepted leaf obeys both inherited continuity limits");
  }
}

void allTreeEdges(const p4::PlannerResult& r, const p4::PlannerOptions& o)
{
  for (const auto side : {p4::PlannerTree::START, p4::PlannerTree::GOAL})
  {
    const auto& nodes = tree(r, side);
    if (nodes.empty()) continue;
    check(!nodes.front().parent && !nodes.front().incoming_attempt, "root has no parent or incoming edge");
    check(exact(nodes.front().q, side == p4::PlannerTree::START ? r.requested_start : r.requested_goal),
          "tree root is the unchanged caller endpoint");
    for (std::size_t i = 1; i < nodes.size(); ++i)
    {
      const auto& node = nodes[i];
      check(node.parent && *node.parent < i && node.incoming_attempt,
            "every non-root has an earlier same-tree parent and edge provenance");
      const auto& a = r.attempts.at(*node.incoming_attempt);
      check(a.tree == side && a.status == p4::AttemptStatus::ACCEPTED && a.added_node &&
            *a.added_node == i && a.nearest_node == *node.parent,
            "node insertion exactly matches its accepted parent attempt");
      check(a.candidate && exact(*a.candidate, node.q) && a.connection,
            "inserted node cannot skip candidate or local-connection evidence");
      qualifiedConnection(*a.connection, nodes.at(*node.parent).q, node.q, o.local_connection);
    }
  }
  std::size_t accepted = 0;
  for (const auto& a : r.attempts)
  {
    if (a.status == p4::AttemptStatus::ACCEPTED)
    {
      ++accepted;
      check(a.added_node && a.connection, "every accepted attempt inserts exactly one evidenced node");
    }
    else check(!a.added_node, "failed projection or connection never inserts a tree node");
  }
  const std::size_t roots = !r.start_tree.empty() + !r.goal_tree.empty();
  check(accepted + roots == r.start_tree.size() + r.goal_tree.size(),
        "tree node count excludes all failed candidate attempts");
  check(r.counters.accepted_start_edges + r.counters.accepted_goal_edges == accepted,
        "accepted-edge counters equal actual inserted nodes");
}

void noSolution(const p4::PlannerResult& r)
{
  check(r.status != p4::PlannerStatus::SUCCESS && r.path_edges.empty() &&
        r.path_milestones.empty() && r.dense_path.empty() &&
        r.dense_path_evidence.empty() && !r.path_metrics,
        "failed search exposes no partial path or success metrics");
  check(!r.meeting_start_node && !r.meeting_goal_node, "failed search has no fictitious meeting nodes");
}

void successfulPath(const p4::PlannerResult& r, const p4::JointVector& start,
                    const p4::JointVector& goal, const p4::PlannerOptions& o)
{
  check(r.status == p4::PlannerStatus::SUCCESS, "synthetic closed manifold search succeeds");
  check(exact(r.requested_start, start) && exact(r.requested_goal, goal), "caller endpoints remain exact");
  check(r.start_root && r.goal_root, "both exact roots retain qualification evidence");
  qualifiedConnection(*r.start_root, start, start, o.local_connection);
  qualifiedConnection(*r.goal_root, goal, goal, o.local_connection);
  allTreeEdges(r, o);
  check(r.meeting_start_node && r.meeting_goal_node, "successful search identifies both meeting nodes");
  check(exact(r.start_tree.at(*r.meeting_start_node).q, r.goal_tree.at(*r.meeting_goal_node).q),
        "trees meet at one identical configuration, not a proximity snap");

  std::vector<p4::PlannerPathEdge> expected;
  std::size_t child = *r.meeting_start_node;
  while (r.start_tree.at(child).parent)
  {
    const auto& n = r.start_tree.at(child);
    expected.push_back({p4::PlannerTree::START, *n.parent, child, *n.incoming_attempt, false});
    child = *n.parent;
  }
  std::reverse(expected.begin(), expected.end());
  child = *r.meeting_goal_node;
  while (r.goal_tree.at(child).parent)
  {
    const auto& n = r.goal_tree.at(child);
    expected.push_back({p4::PlannerTree::GOAL, *n.parent, child, *n.incoming_attempt, true});
    child = *n.parent;
  }
  check(r.path_edges.size() == expected.size(), "solution includes every parent-chain edge exactly once");
  std::vector<p4::JointVector> milestones{start}, dense{start};
  for (std::size_t k = 0; k < expected.size(); ++k)
  {
    const auto& e = r.path_edges[k];
    const auto& wanted = expected[k];
    check(e.tree == wanted.tree && e.parent == wanted.parent && e.child == wanted.child &&
          e.attempt == wanted.attempt && e.reversed == wanted.reversed,
          "path edges preserve parents and correctly reverse the goal tree");
    const auto& nodes = tree(r, e.tree);
    milestones.push_back(nodes.at(e.reversed ? e.parent : e.child).q);
    const auto& c = *r.attempts.at(e.attempt).connection;
    auto order = c.verified_prefix;
    if (e.reversed) std::reverse(order.begin(), order.end());
    check(exact(dense.back(), c.checked_points.at(order.front()).q),
          "concatenated local edges share exact endpoints");
    for (std::size_t i = 1; i < order.size(); ++i) dense.push_back(c.checked_points.at(order[i]).q);
  }
  check(milestones.size() == r.path_milestones.size() && dense.size() == r.dense_path.size(),
        "returned paths contain the complete reconstructed edges without duplicated meetings");
  for (std::size_t i = 0; i < milestones.size(); ++i)
    check(exact(milestones[i], r.path_milestones[i]), "milestone order equals independently walked parents");
  check(!r.dense_path.empty() && exact(r.dense_path.front(), start) && exact(r.dense_path.back(), goal),
        "dense solution reaches exact original endpoints without repair");
  check(r.dense_path_evidence.size() == dense.size(), "every dense output point retains local evidence");
  double length = 0., max_l2 = 0., max_abs = 0.;
  for (std::size_t i = 0; i < dense.size(); ++i)
  {
    check(exact(dense[i], r.dense_path[i]), "dense output equals ordered local prefix reconstruction");
    const auto& source = r.dense_path_evidence[i];
    const auto& c = source.attempt ? *r.attempts.at(*source.attempt).connection :
                    (source.tree == p4::PlannerTree::START ? *r.start_root : *r.goal_root);
    const auto& p = c.checked_points.at(source.checked_point);
    check(p.qualified && exact(p.q, source.q) && exact(source.q, dense[i]),
          "dense provenance resolves to an actually qualified local point");
    if (i)
    {
      const auto d = (dense[i] - dense[i - 1]).eval();
      length += d.norm();
      max_l2 = std::max(max_l2, d.norm());
      max_abs = std::max(max_abs, d.cwiseAbs().maxCoeff());
      check(d.norm() <= o.local_connection.adjacent_l2_limit_rad &&
            d.cwiseAbs().maxCoeff() <= o.local_connection.adjacent_max_abs_limit_rad,
            "assembled dense adjacency retains inherited local continuity bounds");
    }
  }
  check(r.path_metrics && std::abs(r.path_metrics->joint_path_length_rad - length) < 1e-12 &&
        std::abs(r.path_metrics->maximum_adjacent_l2_rad - max_l2) < 1e-12 &&
        std::abs(r.path_metrics->maximum_adjacent_max_abs_rad - max_abs) < 1e-12,
        "path metrics describe the returned dense path in radians");
  check(r.minimum_distance_status == "UNAVAILABLE_NATIVE_DISTANCE_NOT_QUERIED",
        "synthetic free evidence does not invent a native collision clearance");
  check(std::isfinite(r.compute_wall_time_sec) && r.compute_wall_time_sec >= 0.,
        "compute wall cost is finite and is not physical execution duration");
}

void repeated(const p4::PlannerResult& a, const p4::PlannerResult& b)
{
  check(a.status == b.status && a.start_tree.size() == b.start_tree.size() &&
        a.goal_tree.size() == b.goal_tree.size() && a.sampled_targets.size() == b.sampled_targets.size() &&
        a.attempts.size() == b.attempts.size() && a.dense_path.size() == b.dense_path.size(),
        "same seed repeats termination and all deterministic record counts");
  const auto& x = a.counters;
  const auto& y = b.counters;
  check(x.iterations == y.iterations && x.samples == y.samples && x.rng_draws == y.rng_draws &&
        x.nearest_queries == y.nearest_queries &&
        x.nearest_distance_evaluations == y.nearest_distance_evaluations &&
        x.growth_attempts == y.growth_attempts && x.candidate_projection_calls == y.candidate_projection_calls &&
        x.candidate_projection_failures == y.candidate_projection_failures &&
        x.tree_edge_connection_calls == y.tree_edge_connection_calls &&
        x.rbs_midpoint_projection_calls == y.rbs_midpoint_projection_calls &&
        x.collision_queries == y.collision_queries && x.constraint_evaluations == y.constraint_evaluations &&
        x.margin_evaluations == y.margin_evaluations &&
        x.accepted_start_edges == y.accepted_start_edges && x.accepted_goal_edges == y.accepted_goal_edges,
        "deterministic search counters repeat, excluding wall clock");
  for (std::size_t i = 0; i < a.sampled_targets.size(); ++i)
    check(exact(a.sampled_targets[i], b.sampled_targets[i]), "same seed repeats exact sampled 14q");
  for (std::size_t i = 0; i < a.attempts.size(); ++i)
  {
    const auto& first = a.attempts[i];
    const auto& second = b.attempts[i];
    check(first.tree == second.tree && first.mode == second.mode && first.status == second.status &&
          first.nearest_node == second.nearest_node && first.added_node == second.added_node &&
          exact(first.raw_target, second.raw_target) && exact(first.raw_steer, second.raw_steer),
          "same seed repeats exact growth decisions and failure statuses");
    check(first.candidate.has_value() == second.candidate.has_value(), "candidate availability repeats");
    if (first.candidate) check(exact(*first.candidate, *second.candidate), "projected candidates repeat exactly");
  }
  for (std::size_t i = 0; i < a.dense_path.size(); ++i)
    check(exact(a.dense_path[i], b.dense_path[i]), "same seed repeats exact dense path");
}
}  // namespace

int main()
{
  try
  {
    const auto lower = lowerBounds(), upper = upperBounds();
    const auto native = margin(lower, upper);
    const auto start = point(-.15), goal = point(.15);
    const auto opt = options();
    auto r = p4::plan(start, goal, lower, upper, flat, native, clear(), opt);
    successfulPath(r, start, goal, opt);
    check(r.start_tree.size() > 1 && r.goal_tree.size() > 1 && r.path_edges.size() >= 3,
          "synthetic positive grows both trees and assembles multiple accepted edges");
    check(r.counters.candidate_projection_calls > 0 && r.counters.tree_edge_connection_calls > 0 &&
          r.counters.rbs_midpoint_projection_calls > 0,
          "positive uses production projection and RBS for actual search edges");
    check(std::any_of(r.path_edges.begin(), r.path_edges.end(), [](const auto& e) { return e.reversed; }),
          "positive exercises reversed goal-tree connection evidence");
    const auto again = p4::plan(start, goal, lower, upper, flat, native, clear(), opt);
    repeated(r, again);
    auto other_seed = opt;
    other_seed.seed = 41;
    const auto other = p4::plan(start, goal, lower, upper, flat, native, clear(), other_seed);
    successfulPath(other, start, goal, other_seed);
    check(!r.sampled_targets.empty() && !other.sampled_targets.empty() &&
          !exact(r.sampled_targets.front(), other.sampled_targets.front()), "different seeds produce different ambient targets");
    check(r.counters.rng_draws == 14 * r.counters.samples, "uniform sampler consumes one RNG draw per native variable");
    std::mt19937_64 engine(opt.seed);
    p4::JointVector first_target;
    for (int j = 0; j < 14; ++j)
      first_target(j) = lower(j) + (upper(j) - lower(j)) * static_cast<double>(engine() >> 11) * 0x1.0p-53;
    check(exact(r.sampled_targets.front(), first_target), "first target follows the declared engine and binary53 mapping");
    for (const auto& q : r.sampled_targets)
      check(q.allFinite() && (q.array() >= lower.array()).all() && (q.array() <= upper.array()).all(),
            "ambient samples stay inside supplied native bounds");

    // An already valid near-closed exact endpoint must not be projected or snapped.
    auto near_goal = goal;
    near_goal(0) = .9e-8;
    near_goal(3) = .9e-8;
    r = p4::plan(start, near_goal, lower, upper, flat, native, clear(), opt);
    successfulPath(r, start, near_goal, opt);
    check(!r.goal_root->checked_points.front().projection &&
          exact(r.goal_root->checked_points.front().q, near_goal), "exact goal is qualified without endpoint repair");
    r = p4::plan(start, start, lower, upper, flat, native, clear(), opt);
    successfulPath(r, start, start, opt);
    check(r.counters.samples > 0 && !r.path_edges.empty(),
          "identical endpoints still use the declared search rather than a direct-return shortcut");

    auto bad_start = start;
    bad_start(6) = upper(6) + 1e-12;
    r = p4::plan(bad_start, goal, lower, upper, flat, native, clear(), opt);
    check(r.status == p4::PlannerStatus::START_REJECTED, "native bound violation rejects exact start without epsilon");
    noSolution(r);
    check(exact(r.requested_start, bad_start) && r.counters.candidate_projection_calls == 0,
          "out-of-bounds exact start is not clamped or projected");
    auto bad_goal = goal;
    bad_goal(3) = 1.1e-8;
    r = p4::plan(start, bad_goal, lower, upper, flat, native, clear(), opt);
    check(r.status == p4::PlannerStatus::GOAL_REJECTED, "invalid exact goal closure rejects before search");
    noSolution(r);
    check(exact(r.requested_goal, bad_goal) && r.counters.candidate_projection_calls == 0,
          "unclosed goal is not repaired or snapped to a projected state");
    auto nonfinite = start;
    nonfinite(6) = std::numeric_limits<double>::quiet_NaN();
    r = p4::plan(nonfinite, goal, lower, upper, flat, native, clear(), opt);
    check(r.status == p4::PlannerStatus::INVALID_INPUT, "nonfinite caller input rejects deterministically");
    noSolution(r);

    // Valid endpoints with rank-zero residual away from the roots: finite q is not success.
    const auto singular = [](const p4::JointVector& q) {
      p4::Residual residual = q.head<6>();
      residual(0) += q(6) * q(6) - .15 * .15;
      return syntheticSample(residual, p4::ConstraintJacobian::Zero());
    };
    auto finite_budget = opt;
    finite_budget.max_iterations = 2;
    finite_budget.extend_attempts = 1;
    finite_budget.connect_attempts = 1;
    r = p4::plan(start, goal, lower, upper, singular, native, clear(), finite_budget);
    check(r.status == p4::PlannerStatus::ITERATION_LIMIT && r.counters.candidate_projection_failures > 0,
          "failed original projection cannot become a search node or success");
    check(r.counters.iterations == finite_budget.max_iterations && r.attempts.size() <= 4,
          "projection failures respect both per-grow caps and the outer-iteration budget");
    noSolution(r);
    allTreeEdges(r, finite_budget);
    check(r.start_tree.size() == 1 && r.goal_tree.size() == 1, "rank failures preserve only the two qualified roots");
    check(std::any_of(r.attempts.begin(), r.attempts.end(), [](const auto& a) {
      return a.status == p4::AttemptStatus::PROJECTION_FAILED && a.projection &&
             a.projection->status == p4::ProjectionStatus::RANK_DEFICIENT &&
             a.projection->projected_q.allFinite() && !a.added_node;
    }), "rank-deficient original projection trace and finite rejected q are retained");
    check(r.attempts.size() >= 2 && r.attempts[0].tree != r.attempts[1].tree,
          "trapped first tree is followed by attempted growth of the other tree");

    const auto root_only_collision = [start, goal](const p4::JointVector& q) {
      return exact(q, start) || exact(q, goal) ? freeEvidence() : collisionEvidence();
    };
    r = p4::plan(start, goal, lower, upper, flat, native, root_only_collision, finite_budget);
    check(r.status == p4::PlannerStatus::ITERATION_LIMIT && r.counters.local_connection_rejections > 0 &&
          r.counters.collision_positive_queries > 0, "local collision rejection prevents node insertion");
    noSolution(r);
    allTreeEdges(r, finite_budget);
    check(r.start_tree.size() == 1 && r.goal_tree.size() == 1 && r.failed_prefix_attempt,
          "rejected local edges preserve only roots and diagnostic prefix provenance");
    check(std::any_of(r.attempts.begin(), r.attempts.end(), [](const auto& a) {
      return a.status == p4::AttemptStatus::CONNECTION_REJECTED && a.connection &&
             a.connection->status == p4::ConnectionStatus::COLLISION && !a.added_node;
    }), "failed original connector collision evidence is preserved");

    const auto incomplete_inside = [start, goal](const p4::JointVector& q) {
      auto e = freeEvidence();
      if (!exact(q, start) && !exact(q, goal)) { e.complete = false; e.reason = "Synthetic unavailable evidence"; }
      return e;
    };
    r = p4::plan(start, goal, lower, upper, flat, native, incomplete_inside, finite_budget);
    check(r.counters.collision_unavailable_queries > 0 && r.start_tree.size() == 1 && r.goal_tree.size() == 1,
          "unqualified collision evidence cannot enter either search tree");
    noSolution(r);
    allTreeEdges(r, finite_budget);
    check(std::any_of(r.attempts.begin(), r.attempts.end(), [](const auto& a) {
      return a.connection && a.connection->status == p4::ConnectionStatus::COLLISION_UNAVAILABLE;
    }), "incomplete local collision evidence remains an explicit rejection");
    const auto incomplete_root = [](const p4::JointVector&) {
      auto e = freeEvidence(); e.complete = false; return e;
    };
    r = p4::plan(start, goal, lower, upper, flat, native, incomplete_root, opt);
    check(r.status == p4::PlannerStatus::START_REJECTED && r.attempts.empty(),
          "unqualified exact-root evidence stops before search");
    noSolution(r);

    auto exhausted = opt;
    exhausted.max_iterations = 0;
    r = p4::plan(start, goal, lower, upper, flat, native, clear(), exhausted);
    check(r.status == p4::PlannerStatus::ITERATION_LIMIT && r.counters.iterations == 0 &&
          r.sampled_targets.empty() && r.attempts.empty(), "zero outer-iteration budget is terminal without a direct-return shortcut");
    noSolution(r);
    exhausted = opt;
    exhausted.max_nodes = 2;
    r = p4::plan(start, goal, lower, upper, flat, native, clear(), exhausted);
    check(r.status == p4::PlannerStatus::NODE_LIMIT && r.start_tree.size() + r.goal_tree.size() == 2,
          "node budget includes both roots and forbids a third node");
    noSolution(r);
    allTreeEdges(r, exhausted);
    exhausted.max_nodes = 3;
    r = p4::plan(start, goal, lower, upper, flat, native, clear(), exhausted);
    check(r.status == p4::PlannerStatus::NODE_LIMIT && r.start_tree.size() + r.goal_tree.size() <= 3,
          "node budget is enforced inside repeated growth before every insertion");
    noSolution(r);
    allTreeEdges(r, exhausted);
    exhausted = opt;
    exhausted.extend_attempts = 0;
    exhausted.connect_attempts = 0;
    exhausted.max_iterations = 2;
    r = p4::plan(start, goal, lower, upper, flat, native, clear(), exhausted);
    check(r.status == p4::PlannerStatus::ITERATION_LIMIT && r.attempts.empty() && r.counters.iterations == 2,
          "zero growth caps make bounded finite progress through the outer-iteration budget");
    noSolution(r);
    exhausted = opt;
    exhausted.max_compute_wall_sec = .02;
    std::size_t slow_calls = 0;
    const auto slow_clear = [&slow_calls](const p4::JointVector&) {
      ++slow_calls;
      std::this_thread::sleep_for(std::chrono::milliseconds(25));
      return freeEvidence();
    };
    r = p4::plan(start, goal, lower, upper, flat, native, slow_clear, exhausted);
    check(r.status == p4::PlannerStatus::TIME_LIMIT && slow_calls > 0,
          "actual synthetic callback cost triggers compute-wall cutoff");
    noSolution(r);
    std::size_t growth_calls = 0;
    const auto slow_growth = [&growth_calls](const p4::JointVector&) {
      if (++growth_calls == 3) std::this_thread::sleep_for(std::chrono::milliseconds(25));
      return freeEvidence();
    };
    r = p4::plan(start, goal, lower, upper, flat, native, slow_growth, exhausted);
    check(r.status == p4::PlannerStatus::TIME_LIMIT && growth_calls >= 3 &&
          r.start_tree.size() + r.goal_tree.size() == 2,
          "wall cutoff inside a growth attempt forbids insertion after callback overrun");
    noSolution(r);
    allTreeEdges(r, exhausted);

    auto no_progress = finite_budget;
    no_progress.raw_steer_range_rad = 1e-16;
    r = p4::plan(start, goal, lower, upper, flat, native, clear(), no_progress);
    check(r.status == p4::PlannerStatus::ITERATION_LIMIT && r.counters.no_progress_rejections > 0 &&
          r.start_tree.size() == 1 && r.goal_tree.size() == 1,
          "sub-progress candidates are rejected without duplicate tree nodes");
    noSolution(r);
    allTreeEdges(r, no_progress);

    auto invalid = opt;
    invalid.raw_steer_range_rad = 0.;
    r = p4::plan(start, goal, lower, upper, flat, native, clear(), invalid);
    check(r.status == p4::PlannerStatus::INVALID_OPTIONS && r.attempts.empty(), "invalid steering option fails before search");
    noSolution(r);
    invalid = opt;
    invalid.max_nodes = 1;
    r = p4::plan(start, goal, lower, upper, flat, native, clear(), invalid);
    check(r.status == p4::PlannerStatus::INVALID_OPTIONS, "node budget smaller than two roots is invalid");
    noSolution(r);
    auto reversed_bounds = lower;
    reversed_bounds(7) = upper(7) + .1;
    r = p4::plan(start, goal, reversed_bounds, upper, flat, native, clear(), opt);
    check(r.status == p4::PlannerStatus::INVALID_INPUT, "invalid native sampling box cannot be silently reordered");
    noSolution(r);
    std::cout << "TASK06 synthetic orchestration checks=" << checks
              << "; no FR3, native FCL, physics, or continuous-collision claim\n";
    return 0;
  }
  catch (const std::exception& e)
  {
    std::cerr << "TASK06 synthetic failure: " << e.what() << '\n';
    return 1;
  }
}
