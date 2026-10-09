// [ENGINEERING] 合成数学单元测试；不是 FR3/Isaac 物理证据。
#include "baselines/p4_closed_chain/closure.hpp"
#include <iostream>
#include <limits>
#include <vector>

using common_geometry::pi;
namespace
{
int checks=0;
void check(bool ok,const char* name)
{
  if (!ok) throw std::runtime_error(name);
  ++checks;
}
template<class F> void rejected(F f,const char* name)
{
  bool threw=false;
  try { f(); } catch (const std::exception&) { threw=true; }
  check(threw,name);
}
Eigen::Isometry3d pose(const Eigen::Vector3d& p,const Eigen::Vector3d& axis,double angle)
{
  Eigen::Isometry3d t=Eigen::Isometry3d::Identity();
  t.translation()=p; t.linear()=Eigen::AngleAxisd(angle,axis.normalized()).toRotationMatrix();
  return t;
}
p4::ArmSample toy(const Eigen::Matrix<double,7,1>& q)
{
  // 明确的人工运动映射，不模仿/替换 FR3 模型。
  const Eigen::Matrix3d rx=Eigen::AngleAxisd(q(3),Eigen::Vector3d::UnitX()).toRotationMatrix();
  const Eigen::Matrix3d ry=Eigen::AngleAxisd(q(4),Eigen::Vector3d::UnitY()).toRotationMatrix();
  const Eigen::Matrix3d rz=Eigen::AngleAxisd(q(5),Eigen::Vector3d::UnitZ()).toRotationMatrix();
  p4::ArmSample s;
  s.world_tcp=Eigen::Isometry3d::Identity();
  s.world_tcp.translation()=q.head<3>()+q(6)*Eigen::Vector3d(.2,.1,-.3);
  s.world_tcp.linear()=rx*ry*rz;
  s.world_tcp_jacobian.setZero();
  s.world_tcp_jacobian.topLeftCorner<3,3>().setIdentity();
  s.world_tcp_jacobian.block<3,1>(0,6)=Eigen::Vector3d(.2,.1,-.3);
  s.world_tcp_jacobian.block<3,1>(3,3)=Eigen::Vector3d::UnitX();
  s.world_tcp_jacobian.block<3,1>(3,4)=rx*Eigen::Vector3d::UnitY();
  s.world_tcp_jacobian.block<3,1>(3,5)=rx*ry*Eigen::Vector3d::UnitZ();
  return s;
}
}

int main()
{
  try
  {
    const auto identity=Eigen::Isometry3d::Identity();
    const auto gl=pose({.1,-.2,.3},{1.,2.,3.},.3);
    const auto gr=pose({-.2,.1,-.1},{2.,-1.,1.},-.4);
    const auto obj=pose({.7,.2,.4},{1.,-2.,3.},1.2);
    check(p4::residual(obj*gl.inverse(),obj*gr.inverse(),gl,gr).norm()<1e-14,
      "zero closure with distinct nontrivial rigid grasps");
    auto moved=obj; moved.translation()+=Eigen::Vector3d(.01,-.02,.03);
    const p4::Residual translation=p4::residual(moved,obj,identity,identity);
    check((translation.head<3>()-Eigen::Vector3d(.01,-.02,.03)).norm()<1e-14,
      "translation direction/world frame");
    check(translation.tail<3>().norm()<1e-14,"translation not rotation");
    const Eigen::Vector3d axis=Eigen::Vector3d(1.,2.,-3.).normalized();
    auto rotated=obj;
    rotated.linear()=obj.linear()*Eigen::AngleAxisd(.08,axis).toRotationMatrix();
    const auto rotation=p4::residual(rotated,obj,identity,identity);
    check((rotation.tail<3>()-.08*axis).norm()<1e-14,"log in right object frame");
    const Eigen::Quaterniond quat(rotated.linear());
    const Eigen::Vector4d xyzw=quat.coeffs();
    const auto positive=common_geometry::fromXyzw(rotated.translation(),xyzw);
    const auto negative=common_geometry::fromXyzw(rotated.translation(),-xyzw);
    check((p4::residual(positive,obj,identity,identity)-
           p4::residual(negative,obj,identity,identity)).norm()<1e-14,
      "quaternion sign equivalence");
    for (double angle:{0.,1e-10,1e-6,.1,2.,pi-1e-5})
    {
      const Eigen::Matrix3d r=Eigen::AngleAxisd(angle,axis).toRotationMatrix();
      check((common_geometry::so3Log(r)-angle*axis).norm()<1e-12,
        "SO3 log identity/tiny/large/near-pi");
    }
    const Eigen::Matrix3d pi_rotation=Eigen::AngleAxisd(pi,axis).toRotationMatrix();
    const Eigen::Vector3d pi_log=common_geometry::so3Log(pi_rotation);
    check(std::abs(pi_log.norm()-pi)<1e-12 &&
      (Eigen::AngleAxisd(pi_log.norm(),pi_log.normalized()).toRotationMatrix()-pi_rotation).norm()<1e-12,
      "pi log is equivalent rotation, axis sign not uniquely defined");
    rejected([&]{common_geometry::so3LeftJacobianInverse(common_geometry::so3Log(pi_rotation));},
      "pi nondifferentiable Jacobian rejected");
    check((common_geometry::so3LeftJacobianInverse(Eigen::Vector3d::Zero())-
           Eigen::Matrix3d::Identity()).norm()<1e-15,"zero log derivative");

    double max_fd=0.;
    for (int trial=0;trial<12;++trial)
    {
      p4::JointVector q;
      for (int i=0;i<14;++i) q(i)=.25*std::sin(.73*i+.2*trial);
      const auto left=toy(q.head<7>()),right=toy(q.tail<7>());
      const auto actual=p4::evaluate(left,right,gl,gr);
      const auto fn=[&](const p4::JointVector& value)->p4::Residual {
        return p4::residual(toy(value.head<7>()).world_tcp,
          toy(value.tail<7>()).world_tcp,gl,gr);
      };
      for (double h:{1e-5,3e-6,1e-6})
      {
        const double error=(actual.jacobian-p4::centralDifference(q,fn,h)).cwiseAbs().maxCoeff();
        max_fd=std::max(max_fd,error);
        check(error<2e-7,"synthetic analytic-vs-FD Jacobian");
      }
      // 世界坐标规范变换：ep/Jp旋转，object-local eR/JR不变。
      const auto world=pose({-.4,.8,.2},{2.,3.,1.},.8);
      auto l=left,r=right;
      l.world_tcp=world*left.world_tcp; r.world_tcp=world*right.world_tcp;
      for (auto* s:{&l,&r})
      {
        s->world_tcp_jacobian.topRows<3>()=world.linear()*s->world_tcp_jacobian.topRows<3>().eval();
        s->world_tcp_jacobian.bottomRows<3>()=world.linear()*s->world_tcp_jacobian.bottomRows<3>().eval();
      }
      const auto changed=p4::evaluate(l,r,gl,gr);
      check((changed.residual.head<3>()-world.linear()*actual.residual.head<3>()).norm()<1e-13,
        "world transform residual position");
      check((changed.residual.tail<3>()-actual.residual.tail<3>()).norm()<1e-13,
        "world transform residual orientation");
      check((changed.jacobian.topRows<3>()-world.linear()*actual.jacobian.topRows<3>()).norm()<1e-13 &&
            (changed.jacobian.bottomRows<3>()-actual.jacobian.bottomRows<3>()).norm()<1e-13,
        "world transform Jacobian");
    }
    auto invalid=obj; invalid.matrix()(0,0)=std::numeric_limits<double>::quiet_NaN();
    rejected([&]{p4::residual(invalid,obj,gl,gr);},"nonfinite pose rejected");
    invalid=obj; invalid.linear() *= 2.;
    rejected([&]{p4::residual(invalid,obj,gl,gr);},"scaled/non-SO3 pose rejected");
    invalid=obj; invalid.matrix()(3,0)=.1;
    rejected([&]{p4::residual(invalid,obj,gl,gr);},"invalid homogeneous row rejected");
    rejected([&]{common_geometry::fromXyzw(Eigen::Vector3d::Zero(),Eigen::Vector4d::Zero());},
      "zero quaternion rejected");
    auto bad=toy(Eigen::Matrix<double,7,1>::Zero());
    bad.world_tcp_jacobian(0,0)=std::numeric_limits<double>::infinity();
    rejected([&]{p4::evaluate(bad,toy(Eigen::Matrix<double,7,1>::Zero()),gl,gr);},
      "invalid Jacobian rejected");
    const auto fn=[](const p4::JointVector&)->p4::Residual { return p4::Residual::Zero(); };
    rejected([&]{p4::centralDifference(p4::JointVector::Zero(),fn,0.);},"zero FD step rejected");
    rejected([&]{p4::centralDifference(p4::JointVector::Zero(),fn,-1.);},"negative FD step rejected");
    std::cout << "TASK03 SYNTHETIC MATH PASS checks=" << checks
              << " max_fd_entry_error=" << max_fd << '\n';
    return 0;
  }
  catch(const std::exception& e)
  {
    std::cerr << "TASK03 SYNTHETIC MATH FAIL: " << e.what() << '\n';
    return 1;
  }
}
