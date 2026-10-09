#pragma once
// [ENGINEERING] 纯 Eigen 刚体数学；不依赖 ROS/Isaac，不访问机器人。
#include <Eigen/Geometry>
#include <cmath>
#include <stdexcept>

namespace common_geometry
{
inline constexpr double pi = 3.14159265358979323846;

inline Eigen::Matrix3d skew(const Eigen::Vector3d& v)
{
  if (!v.allFinite()) throw std::invalid_argument("nonfinite vector");
  Eigen::Matrix3d k;
  k << 0., -v.z(), v.y(), v.z(), 0., -v.x(), -v.y(), v.x(), 0.;
  return k;
}

inline void requireRotation(const Eigen::Matrix3d& r)
{
  // 格式/算术精度，非 Benchmark 姿态成功门限；不投影或修复无效输入。
  if (!r.allFinite() || (r.transpose()*r-Eigen::Matrix3d::Identity()).norm()>1e-10 ||
      std::abs(r.determinant()-1.)>1e-10)
    throw std::invalid_argument("rotation must be a finite proper SO(3) matrix");
}

inline void requireRigid(const Eigen::Isometry3d& t)
{
  if (!t.matrix().allFinite() ||
      (t.matrix().row(3)-Eigen::RowVector4d(0.,0.,0.,1.)).norm()>1e-12)
    throw std::invalid_argument("invalid homogeneous transform");
  requireRotation(t.linear());
}

inline Eigen::Isometry3d fromXyzw(const Eigen::Vector3d& p, const Eigen::Vector4d& xyzw)
{
  if (!p.allFinite() || !xyzw.allFinite() || std::abs(xyzw.norm()-1.)>1e-10)
    throw std::invalid_argument("finite translation and unit xyzw quaternion required");
  Eigen::Quaterniond q(xyzw.w(),xyzw.x(),xyzw.y(),xyzw.z());
  // 仅消除有效单位四元数的编码舍入；q 与 -q 构造同一旋转矩阵。
  q.normalize();
  Eigen::Isometry3d t=Eigen::Isometry3d::Identity();
  t.translation()=p; t.linear()=q.toRotationMatrix();
  return t;
}

inline Eigen::Vector3d so3Log(const Eigen::Matrix3d& r)
{
  requireRotation(r);
  Eigen::Quaterniond q(r);
  q.normalize();
  // 最短 SO(3) chart；不用欧拉角差或符号敏感的 quaternion component 差。
  if (q.w()<0.) q.coeffs() *= -1.;
  if (q.w()==0.)
  {
    Eigen::Index index; q.vec().cwiseAbs().maxCoeff(&index);
    if (q.vec()(index)<0.) q.coeffs() *= -1.;
  }
  const double s=q.vec().norm();
  if (s<1e-12) return 2.*q.vec();
  return (2.*std::atan2(s,std::abs(q.w()))/s)*q.vec();
}

inline Eigen::Matrix3d so3LeftJacobianInverse(const Eigen::Vector3d& phi)
{
  if (!phi.allFinite()) throw std::invalid_argument("nonfinite rotation log");
  const double theta=phi.norm();
  // pi 处分支不可微。显式拒绝，而不是给出伪全局 Jacobian。
  if (theta>=pi-1e-8) throw std::domain_error("SO(3) log Jacobian at pi branch is undefined");
  const Eigen::Matrix3d k=skew(phi);
  const double t2=theta*theta;
  const double a=theta<1e-4 ? 1./12.+t2/720.+t2*t2/30240. :
    (1.-.5*theta/std::tan(.5*theta))/t2;
  return Eigen::Matrix3d::Identity()-.5*k+a*k*k;
}
}  // namespace common_geometry
