// P2 continuous equations and user-approved coupled implicit Lie midpoint.
// Eigen is a system dependency (3.4.0); no author simulator is claimed.
// Canonical contact_geometry.py/mechanics.py remain the qualification oracle.
#include <Eigen/Dense>
#include <unsupported/Eigen/AutoDiff>
#include <boost/multiprecision/cpp_dec_float.hpp>
#include <array>
#include <cmath>
#include <algorithm>
#include <stdexcept>

using namespace Eigen;
using Big=boost::multiprecision::cpp_dec_float_50;
template<class S> using M3=Matrix<S,3,3>;
template<class S> using M4=Matrix<S,4,4>;
template<class S> using M6=Matrix<S,6,6>;
template<class S> using V3=Matrix<S,3,1>;
template<class S> using V6=Matrix<S,6,1>;
template<class S> using V42=Matrix<S,42,1>;
template<class S> struct State {std::array<M4<S>,6> T; V6<S> V;};
struct Physics {double mass; Vector3d I,g; std::array<VectorXd,2>K; VectorXd B,Ba;};
struct Inputs {std::array<Vector<double,6>,2> U; std::array<int,2> mode;};
double val(double x){return x;}
double val(const Big&x){return x.convert_to<double>();}
template<class D> double val(const AutoDiffScalar<D>& x){return x.value();}
template<class S> M3<S> crossmat(const V3<S>& x){M3<S>a;a<<S(0),-x(2),x(1),x(2),S(0),-x(0),-x(1),x(0),S(0);return a;}
template<class S> M4<S> inv(const M4<S>& x){M4<S> y=M4<S>::Identity();y.template block<3,3>(0,0)=x.template block<3,3>(0,0).transpose();y.template block<3,1>(0,3)=-y.template block<3,3>(0,0)*x.template block<3,1>(0,3);return y;}
template<class S> M4<S> expse3(const V6<S>& x){
    using std::sin;using std::cos;using std::sqrt;
    V3<S>w=x.template tail<3>();M3<S>W=crossmat(w);S q=w.squaredNorm(),a,b,c;
    if(val(q)<1e-8){a=S(1)-q/S(6)+q*q/S(120)-q*q*q/S(5040);b=S(.5)-q/S(24)+q*q/S(720)-q*q*q/S(40320);c=S(1./6)-q/S(120)+q*q/S(5040)-q*q*q/S(362880);}
    else {S t=sqrt(q);a=sin(t)/t;b=(S(1)-cos(t))/q;c=(t-sin(t))/(q*t);}
    M4<S> T=M4<S>::Identity();T.template block<3,3>(0,0)=M3<S>::Identity()+a*W+b*(W*W);
    T.template block<3,1>(0,3)=(M3<S>::Identity()+b*W+c*(W*W))*x.template head<3>();return T;
}
template<class S> V6<S> logse3(const M4<S>& T){
    using std::sqrt;using std::atan2;using std::sin;using std::cos;
    M3<S>R=T.template block<3,3>(0,0);V3<S>s;s<<(R(2,1)-R(1,2))/S(2),(R(0,2)-R(2,0))/S(2),(R(1,0)-R(0,1))/S(2);
    S q=s.squaredNorm();V3<S>w;
    if(val(q)<1e-8)w=s*(S(1)+q/S(6)+S(3./40)*q*q+S(5./112)*q*q*q);
    else {S n=sqrt(q),c=(R.trace()-S(1))/S(2),theta=atan2(n,c);w=(theta/n)*s;}
    q=w.squaredNorm();if(val(q)>.30*.30)throw std::runtime_error("PAD_ROTATION_OUTSIDE_FAST_KERNEL_DOMAIN");
    S beta;if(val(q)<1e-6)beta=S(1./12)+q/S(720)+q*q/S(30240)+q*q*q/S(1209600);
    else {S t=sqrt(q);beta=S(1)/q-(S(1)+cos(t))/(S(2)*t*sin(t));}
    M3<S>W=crossmat(w);V6<S> x;x.template tail<3>()=w;x.template head<3>()=(M3<S>::Identity()-S(.5)*W+beta*(W*W))*T.template block<3,1>(0,3);return x;
}
template<class S> V6<S> adapply(const V6<S>& x,const V6<S>& y){V6<S>z;V3<S>v=x.template head<3>(),w=x.template tail<3>(),a=y.template head<3>(),b=y.template tail<3>();z.template head<3>()=w.cross(a)+v.cross(b);z.template tail<3>()=w.cross(b);return z;}
template<class S> V6<S> adjapply(const M4<S>& T,const V6<S>& x){M3<S>R=T.template block<3,3>(0,0);V3<S>p=T.template block<3,1>(0,3);V6<S>z;z.template tail<3>()=R*x.template tail<3>();z.template head<3>()=R*x.template head<3>()+p.cross(V3<S>(z.template tail<3>()));return z;}
template<class S> M3<S> left_rot_log_jac(const V3<S>& w){
    using std::sqrt;using std::sin;using std::cos;S q=w.squaredNorm(),c;
    if(val(q)<1e-6)c=S(1./12)+q/S(720)+q*q/S(30240)+q*q*q/S(1209600);
    else {S t=sqrt(q);c=S(1)/q-(S(1)+cos(t))/(S(2)*t*sin(t));}
    M3<S>W=crossmat(w);return M3<S>::Identity()-S(.5)*W+c*(W*W);
}
template<class S> V6<S> left_log_apply(const V6<S>& tau,const V6<S>& b){
    // Same inverse-Jacobian analytic function, evaluated as ad-vector powers.
    V6<S>p=b,z=b;const double coefficients[13]={1,-.5,1./12,0,-1./720,0,1./30240,0,-1./1209600,0,1./47900160,0,-691./1307674368000.};
    for(int k=1;k<=12;k++){p=adapply(tau,p);if(coefficients[k]!=0)z+=S(coefficients[k])*p;}return z;
}
template<class S> V6<S> free_grasp(const M4<S>& D,const M4<S>& G,const V6<S>& tau,const V6<S>& V,const V6<S>& U,int mode){
    if(mode==0)return V6<S>::Zero();
    M4<S> DGi=D*inv(G);V6<S>b=adjapply(DGi,V)-U;M3<S>L=left_rot_log_jac(V3<S>(tau.template tail<3>()));
    V6<S> spatial=V6<S>::Zero();
    if(mode==1){S a=L(2,2);if(!std::isfinite(val(a))||val(a)==0)throw std::runtime_error("FREE_CONSTRAINT_SINGULAR");spatial(5)=-(L.row(2)*b.template tail<3>())(0)/a;}
    else {V6<S>y=left_log_apply(tau,b);S a=L(0,0),bb=L(0,1),c=L(1,0),d=L(1,1),det=a*d-bb*c;
        Matrix2d Av;Av<<val(a),val(bb),val(c),val(d);auto sv=Av.jacobiSvd().singularValues();if(sv(1)<=1e-12*sv(0))throw std::runtime_error("FREE_CONSTRAINT_SINGULAR");
        spatial(0)=-(d*y(0)-bb*y(1))/det;spatial(1)=-(-c*y(0)+a*y(1))/det;}
    return adjapply(inv(D),spatial);
}
bool transmitted(int mode,int i){return mode==0||(mode==1&&i<5)||(mode==2&&i>=2);}
template<class S> struct RawContact {std::array<M4<S>,2>D,A;std::array<V6<S>,2>tau,hK,hB,h;V6<S>external;};
template<class S> RawContact<S> contact(const State<S>& X,const Inputs& u,const Physics& p){
    RawContact<S>c;c.external=V6<S>::Zero();std::array<M4<S>,2>E={X.T[1],inv(X.T[3])*X.T[2]};
    for(int r=0;r<2;r++){const M4<S>&G=X.T[4+r];c.D[r]=inv(E[r])*X.T[0]*G;c.tau[r]=logse3(c.D[r]);c.A[r]=inv(X.T[0])*E[r];
        V6<S>gv=adjapply(inv(G),X.V);V6<S>relative;M3<S>R=c.D[r].template block<3,3>(0,0);relative.template head<3>()=R*gv.template head<3>();relative.template tail<3>()=R*gv.template tail<3>();
        for(int i=0;i<6;i++){c.hK[r](i)=-S(p.K[r](i))*c.tau[r](i);c.hB[r](i)=-S(p.B(i))*(relative(i)-S(u.U[r](i)));c.h[r](i)=c.hK[r](i)+c.hB[r](i);}
        V6<S>h=c.h[r];for(int i=0;i<6;i++)if(!transmitted(u.mode[r],i))h(i)=S(0);
        M3<S>Arot=c.A[r].template block<3,3>(0,0);V3<S>ap=c.A[r].template block<3,1>(0,3),force=Arot*h.template head<3>();c.external.template head<3>()+=force;c.external.template tail<3>()+=Arot*h.template tail<3>()+ap.cross(force);
    }return c;
}
template<class S> V42<S> field(const State<S>& X,const Inputs& u,const Physics& p){
    RawContact<S>c=contact(X,u,p);V42<S> f=V42<S>::Zero();f.template segment<6>(0)=X.V;
    V3<S>v=X.V.template head<3>(),w=X.V.template tail<3>(),momlin=S(p.mass)*v,momang;
    for(int i=0;i<3;i++)momang(i)=S(p.I(i))*w(i);
    V3<S>lin=c.external.template head<3>()-w.cross(momlin),ang=c.external.template tail<3>()-v.cross(momlin)-w.cross(momang),grav=X.T[0].template block<3,3>(0,0).transpose()*p.g.template cast<S>();
    for(int i=0;i<3;i++){f(6+i)=(lin(i)-S(p.Ba(i))*v(i))/S(p.mass)+grav(i);f(9+i)=(ang(i)-S(p.Ba(3+i))*w(i))/S(p.I(i));}
    for(int r=0;r<2;r++){f.template segment<6>(12+6*r)=u.U[r].template cast<S>();f.template segment<6>(30+6*r)=free_grasp(c.D[r],X.T[4+r],c.tau[r],X.V,V6<S>(u.U[r].template cast<S>()),u.mode[r]);}
    return f;
}
State<double> unpack(const double* a){State<double>x;for(int j=0;j<6;j++)for(int i=0;i<16;i++)x.T[j](i/4,i%4)=a[16*j+i];for(int i=0;i<6;i++)x.V(i)=a[96+i];return x;}
void pack(const State<double>&x,double*a){for(int j=0;j<6;j++)for(int i=0;i<16;i++)a[16*j+i]=x.T[j](i/4,i%4);for(int i=0;i<6;i++)a[96+i]=x.V(i);}
Physics params(const double*a){Physics p;p.mass=a[0];p.I=Map<const Vector3d>(a+1);for(int r=0;r<2;r++)p.K[r]=Map<const VectorXd>(a+4+6*r,6);p.B=Map<const VectorXd>(a+16,6);p.Ba=Map<const VectorXd>(a+22,6);p.g=Map<const Vector3d>(a+28);return p;}
Inputs inputs(const double*a,const int*m){Inputs u;for(int r=0;r<2;r++){u.U[r]=Map<const Vector<double,6>>(a+6*r);u.mode[r]=m[r];if(m[r]<0||m[r]>2)throw std::runtime_error("UNKNOWN_MODE");}return u;}
const std::array<int,6>pose_offsets={0,12,18,24,30,36};
const std::array<int,24>unknown={0,1,2,3,4,5,6,7,8,9,10,11,30,31,32,33,34,35,36,37,38,39,40,41};
State<double> retract(const State<double>&x,const Vector<double,42>&d){State<double>y;for(int i=0;i<6;i++)y.T[i]=x.T[i]*expse3(Vector<double,6>(d.segment<6>(pose_offsets[i])));y.V=x.V+d.segment<6>(6);return y;}
template<int N> using AD=AutoDiffScalar<Matrix<double,N,1>>;
template<int N> State<AD<N>> seeded(const State<double>&x,const std::array<int,N>&cols){
    State<AD<N>>y;std::array<AD<N>,42>d;for(auto&a:d)a=AD<N>(0.);for(int k=0;k<N;k++)d[cols[k]].derivatives()(k)=1.;
    for(int i=0;i<6;i++){V6<AD<N>>v;for(int j=0;j<6;j++)v(j)=d[pose_offsets[i]+j];y.T[i]=x.T[i].template cast<AD<N>>()*expse3(v);}
    for(int j=0;j<6;j++)y.V(j)=AD<N>(x.V(j))+d[6+j];return y;
}
M6<double> right_jac(const Vector<double,6>&x){M6<double>ad=M6<double>::Zero();ad.block<3,3>(0,0)=crossmat(Vector3d(x.tail<3>()));ad.block<3,3>(0,3)=crossmat(Vector3d(x.head<3>()));ad.block<3,3>(3,3)=ad.block<3,3>(0,0);M6<double>J=M6<double>::Identity(),term=J;for(int k=1;k<=18;k++){term=term*(-ad)/double(k+1);J+=term;}return J;}
void validate(const State<double>&x,const RawContact<double>&c){
    if(!x.V.allFinite()||!c.external.allFinite())throw std::runtime_error("NONFINITE_STATE");
    for(auto&T:x.T){Matrix3d R=T.block<3,3>(0,0);if(!T.allFinite()||(R.transpose()*R-Matrix3d::Identity()).cwiseAbs().maxCoeff()>1e-10||std::abs(R.determinant()-1)>1e-10||(T.row(3)-RowVector4d(0,0,0,1)).cwiseAbs().maxCoeff()>1e-10)throw std::runtime_error("SE3_INVALID");}
    for(auto&t:c.tau)if(t.head<3>().cwiseAbs().maxCoeff()>.005||t.tail<3>().cwiseAbs().maxCoeff()>.15)throw std::runtime_error("PAD_DOMAIN_INVALID");
}
thread_local std::string error_message;
extern "C" const char* p2_last_error(){return error_message.c_str();}
extern "C" int p2_field(const double*x,const double*u,const int*m,const double*p,double*f,double*A){
    try {auto s=unpack(x);auto in=inputs(u,m);auto ph=params(p);
        if(A){std::array<int,42>cols;for(int i=0;i<42;i++)cols[i]=i;auto y=field(seeded<42>(s,cols),in,ph);for(int i=0;i<42;i++){f[i]=y(i).value();for(int j=0;j<42;j++)A[i*42+j]=y(i).derivatives()(j);}}
        else {auto y=field(s,in,ph);for(int i=0;i<42;i++)f[i]=y(i);}return 0;
    }catch(const std::exception&e){error_message=e.what();return 1;}
}
extern "C" int p2_field_fd50(const double*x,const double*u,const int*m,const double*p,double eps,double*A){
    try {auto base=unpack(x);auto in=inputs(u,m);auto ph=params(p);Big e(eps);
        for(int col=0;col<42;col++){
            std::array<V42<Big>,2>ys;
            for(int sign=0;sign<2;sign++){State<Big> s;V42<Big>delta=V42<Big>::Zero();delta(col)=sign?e:-e;
                for(int j=0;j<6;j++)s.T[j]=base.T[j].cast<Big>()*expse3(V6<Big>(delta.segment<6>(pose_offsets[j])));
                s.V=base.V.cast<Big>()+delta.segment<6>(6);ys[sign]=field(s,in,ph);}
            for(int row=0;row<42;row++)A[row*42+col]=((ys[1](row)-ys[0](row))/(Big(2)*e)).convert_to<double>();
        }return 0;
    }catch(const std::exception&e){error_message=e.what();return 1;}
}
extern "C" int p2_contact(const double*x,const double*u,const int*m,const double*p,double*out){
    try {auto s=unpack(x);auto in=inputs(u,m);auto c=contact(s,in,params(p));int n=0;for(int r=0;r<2;r++)for(int i=0;i<16;i++)out[n++]=c.D[r](i/4,i%4);
        for(auto*arrays:{&c.tau,&c.hK,&c.hB,&c.h})for(auto&v:*arrays)for(int i=0;i<6;i++)out[n++]=v(i);
        for(int i=0;i<6;i++)out[n++]=c.external(i);
        int k=0;MatrixXd W(6,12);VectorXd ht(12);std::array<int,12>ids;
        for(int r=0;r<2;r++){Matrix<double,6,6>map=Matrix<double,6,6>::Zero();Matrix3d R=c.A[r].block<3,3>(0,0);map.block<3,3>(0,0)=R;map.block<3,3>(3,3)=R;map.block<3,3>(3,0)=crossmat(Vector3d(c.A[r].block<3,1>(0,3)))*R;
            for(int j=0;j<6;j++)if(transmitted(in.mode[r],j)){W.col(k)=map.col(j);ht(k)=c.h[r](j);ids[k++]=6*r+j;}}
        W.conservativeResize(6,k);ht.conservativeResize(k);JacobiSVD<MatrixXd>svd(W,ComputeThinU|ComputeThinV);VectorXd coeff=svd.matrixU().transpose()*c.external;
        for(int i=0;i<6;i++)coeff(i)=svd.singularValues()(i)>1e-12*svd.singularValues()(0)?coeff(i)/svd.singularValues()(i):0.;
        VectorXd internal=ht-svd.matrixV()*coeff;Vector<double,12>lift=Vector<double,12>::Zero();for(int i=0;i<k;i++)lift(ids[i])=internal(i);for(int i=0;i<12;i++)out[n++]=lift(i);for(int i=0;i<6;i++)out[n++]=svd.singularValues()(i);
        for(int i=0;i<6;i++)for(int j=0;j<12;j++)out[n++]=j<k?W(i,j):0.;return 0;
    }catch(const std::exception&e){error_message=e.what();return 1;}
}
extern "C" int p2_advance(double*packed,const double*u,const int*m,const double*p,double dt,int steps,double*diag,double*last_delta,double*last_residual){
    try {auto x=unpack(packed);auto in=inputs(u,m);auto ph=params(p);int maximum_iterations=0,completed=0;double residualmax=0;
        for(int step=0;step<steps;step++){
            Vector<double,42>d=dt*field(x,in,ph);d.segment<6>(12)=dt*in.U[0];d.segment<6>(18)=dt*in.U[1];d.segment<6>(24).setZero();bool converged=false;int iteration=0;
            for(;iteration<=12;iteration++){
                auto mid=retract(x,Vector<double,42>(.5*d));auto f=field(mid,in,ph);Vector<double,24>res;for(int i=0;i<24;i++)res(i)=d(unknown[i])-dt*f(unknown[i]);
                for(int i=0;i<42;i++)last_delta[i]=d(i);for(int i=0;i<24;i++)last_residual[i]=res(i);
                double norm=res.cwiseAbs().maxCoeff();if(!std::isfinite(norm))throw std::runtime_error("NONFINITE_NEWTON_RESIDUAL");
                if(norm<=1e-12){converged=true;residualmax=std::max(residualmax,norm);break;}
                if(iteration==12)break;
                auto a=field(seeded<24>(mid,unknown),in,ph);Matrix<double,24,24>J;
                for(int i=0;i<24;i++)for(int j=0;j<24;j++)J(i,j)=a(unknown[i]).derivatives()(j);
                Matrix<double,24,24>transport=Matrix<double,24,24>::Identity()*.5;
                for(int b:{0,12,18})transport.block<6,6>(b,b)=.5*right_jac(Vector<double,6>(.5*d.segment<6>(unknown[b])));
                Matrix<double,24,24>system=Matrix<double,24,24>::Identity()-dt*J*transport;
                FullPivLU<Matrix<double,24,24>>lu(system);lu.setThreshold(1e-12);if(lu.rank()!=24)throw std::runtime_error("NEWTON_JACOBIAN_SINGULAR");
                Vector<double,24>correction=lu.solve(res);if(!correction.allFinite())throw std::runtime_error("NONFINITE_NEWTON_DELTA");for(int i=0;i<24;i++)d(unknown[i])-=correction(i);
            }
            maximum_iterations=std::max(maximum_iterations,iteration);
            if(!converged){diag[0]=completed;diag[1]=maximum_iterations;diag[2]=last_residual[0];throw std::runtime_error("IMPLICIT_SOLVER_NONCONVERGED");}
            auto y=retract(x,d);validate(y,contact(y,in,ph));x=y;pack(x,packed);completed++;
            diag[0]=completed;diag[1]=maximum_iterations;diag[2]=residualmax;
        }return 0;
    }catch(const std::exception&e){error_message=e.what();return 1;}
}
