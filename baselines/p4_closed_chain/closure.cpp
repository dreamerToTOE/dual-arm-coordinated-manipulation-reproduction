#include "baselines/p4_closed_chain/closure.hpp"

namespace p4
{
namespace
{
std::pair<Eigen::Isometry3d,Eigen::Isometry3d> objects(
  const Eigen::Isometry3d& left,const Eigen::Isometry3d& right,
  const Eigen::Isometry3d& gl,const Eigen::Isometry3d& gr)
{
  for (const auto* t:{&left,&right,&gl,&gr}) common_geometry::requireRigid(*t);
  return {left*gl,right*gr};
}

Residual difference(const Eigen::Isometry3d& left,const Eigen::Isometry3d& right)
{
  Residual out;
  out.head<3>()=left.translation()-right.translation();
  out.tail<3>()=common_geometry::so3Log(right.linear().transpose()*left.linear());
  if (!out.allFinite()) throw std::invalid_argument("nonfinite closure residual");
  return out;
}
}

Residual residual(const Eigen::Isometry3d& left,const Eigen::Isometry3d& right,
                  const Eigen::Isometry3d& gl,const Eigen::Isometry3d& gr)
{
  const auto predicted=objects(left,right,gl,gr);
  return difference(predicted.first,predicted.second);
}

ClosureSample evaluate(const ArmSample& left,const ArmSample& right,
                       const Eigen::Isometry3d& gl,const Eigen::Isometry3d& gr)
{
  if (!left.world_tcp_jacobian.allFinite() || !right.world_tcp_jacobian.allFinite())
    throw std::invalid_argument("nonfinite world geometric Jacobian");
  const auto predicted=objects(left.world_tcp,right.world_tcp,gl,gr);
  ClosureSample out;
  out.left_object=predicted.first; out.right_object=predicted.second;
  out.residual=difference(out.left_object,out.right_object);
  // 固定抓取的平移力臂：预测物体原点不是 TCP 原点。
  const Eigen::Vector3d rl=left.world_tcp.linear()*gl.translation();
  const Eigen::Vector3d rr=right.world_tcp.linear()*gr.translation();
  out.jacobian.topLeftCorner<3,7>()=left.world_tcp_jacobian.topRows<3>()-
    common_geometry::skew(rl)*left.world_tcp_jacobian.bottomRows<3>();
  out.jacobian.topRightCorner<3,7>()=-(right.world_tcp_jacobian.topRows<3>()-
    common_geometry::skew(rr)*right.world_tcp_jacobian.bottomRows<3>());
  // E=R_R^T R_L; dot(E)=[R_R^T(omega_L-omega_R)]_x E。
  const Eigen::Matrix3d rotation_map=
    common_geometry::so3LeftJacobianInverse(out.residual.tail<3>())*
    out.right_object.linear().transpose();
  out.jacobian.bottomLeftCorner<3,7>()=
    rotation_map*left.world_tcp_jacobian.bottomRows<3>();
  out.jacobian.bottomRightCorner<3,7>()=
    -rotation_map*right.world_tcp_jacobian.bottomRows<3>();
  if (!out.jacobian.allFinite()) throw std::invalid_argument("nonfinite constraint Jacobian");
  return out;
}

ConstraintJacobian centralDifference(
  const JointVector& q,const std::function<Residual(const JointVector&)>& function,double h)
{
  if (!q.allFinite() || !function || !std::isfinite(h) || h<=0.)
    throw std::invalid_argument("finite q, callback and positive FD step required");
  ConstraintJacobian j;
  for (int k=0;k<14;++k)
  {
    JointVector plus=q,minus=q; plus(k)+=h; minus(k)-=h;
    if (plus(k)==q(k) || minus(k)==q(k))
      throw std::invalid_argument("FD step not representable at input q");
    const Residual cp=function(plus),cm=function(minus);
    if (!cp.allFinite() || !cm.allFinite()) throw std::invalid_argument("nonfinite FD samples");
    j.col(k)=(cp-cm)/(2.*h);
  }
  return j;
}
}  // namespace p4
