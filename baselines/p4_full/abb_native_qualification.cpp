// Independent test driver. Author classes are linked from immutable external sources.
// No author algorithm or mesh is redistributed here. No collision/planning claim.
#include "apc_class.h"
#include "kdl_class.h"
#include <algorithm>
#include <chrono>
#include <iomanip>
#include <random>
#include <stdexcept>

static void vec(std::ostream &o, const State &q) {
    o << '[';
    for (size_t i=0;i<q.size();++i) {if(i)o<<','; if(std::isfinite(q[i]))o<<q[i];else o<<"null";}
    o << ']';
}
static void mat(std::ostream &o,const Matrix &t){o<<'[';for(size_t i=0;i<t.size();++i){if(i)o<<',';vec(o,t[i]);}o<<']';}
static Matrix fk(two_robots &a,const State &q,int r){a.FKsolve_rob(q,r);return r==1?a.get_FK_solution_T1():a.get_FK_solution_T2();}
int main(int argc,char **argv){
    if(argc!=3)throw std::runtime_error("usage: driver II|III output.json");
    const bool ii=std::string(argv[1])=="II";
    if(!ii && std::string(argv[1])!="III")throw std::runtime_error("invalid environment");
    const double d=ii?900:1200, l=ii?300:500;
    const State base1={-d/2,0,0},base2={d/2,0,3.1416};
    two_robots a(base1,base2,l);kdl n(d,l);
    // Explicit initialization of diagnostic counters avoids reading author uninitialized counters.
    a.IK_counter=0;a.IK_time=0;n.IK_counter=0;n.IK_time=0;
    std::ofstream out(argv[2]);out<<std::setprecision(17);
    out<<"{\"schema\":\"P4_ABB_NATIVE_MATH_V1\",\"environment\":\""<<argv[1]<<"\",\"D_mm\":"<<d<<",\"L_mm\":"<<l<<",\"base1\":";vec(out,base1);out<<",\"base2\":";vec(out,base2);
    out<<",\"seed\":20261014,\"limits\":\"author default true\",\"rows\":[\n";
    bool first=true;auto row=[&](){if(!first)out<<",\n";first=false;};
    std::mt19937_64 rng(20261014);std::uniform_real_distribution<double> unif(-1,1);
    const State ranges={2.8,1.8,1.45,2.7,2.0,3.0};
    for(int i=0;i<100;++i){
        State q(6);for(int j=0;j<6;++j)q[j]=unif(rng)*ranges[j];q[2]=-.45+unif(rng)*1.4;
        int r=1+i%2;auto target=fk(a,q,r);
        row();out<<"{\"kind\":\"fk\",\"index\":"<<i<<",\"robot\":"<<r<<",\"q\":";vec(out,q);out<<",\"T\":";mat(out,target);out<<'}';
        if(i<10){
            for(int b=0;b<8;++b){
                const bool ok=a.IKsolve_rob(target,r,b);
                row();out<<"{\"kind\":\"ik\",\"index\":"<<i<<",\"robot\":"<<r<<",\"q\":";vec(out,q);out<<",\"target\":";mat(out,target);out<<",\"branch\":"<<b<<",\"success\":"<<(ok?"true":"false");
                if(ok){const State s=r==1?a.get_IK_solution_q1():a.get_IK_solution_q2();out<<",\"solution\":";vec(out,s);out<<",\"T_out\":";mat(out,fk(a,s,r));}
                out<<'}';
            }
        }
    }
    for(int r=1;r<=2;++r){auto target=fk(a,State(6,0),r);target[0][3]=100000000;
        for(int b=0;b<8;++b){bool ok=a.IKsolve_rob(target,r,b);row();out<<"{\"kind\":\"unreachable_ik\",\"robot\":"<<r<<",\"branch\":"<<b<<",\"target\":";mat(out,target);out<<",\"success\":"<<(ok?"true":"false")<<'}';}
    }
    std::vector<State> endpoints;
    if(ii)endpoints={{.5236,1.7453,-1.8326,-1.4835,1.5708,0,1.004278,.2729,.9486,-1.15011,1.81001,-1.97739},{.5236,.34907,.69813,-1.3963,1.5708,0,.7096,1.8032,-1.7061,-1.6286,1.9143,-2.0155}};
    else endpoints={{1.1,1.1,0,1.24,-1.5708,0,-.79567,.60136,.43858,-.74986,-1.0074,-.092294},{-1.1,1.35,-.2,-1,-1.9,0,.80875,.72363,-.47891,-1.0484,.73278,1.7491}};
    auto closed_row=[&](const char *kind,const State &q,int index){
        row();State q1(q.begin(),q.begin()+6),q2(q.begin()+6,q.end());out<<"{\"kind\":\""<<kind<<"\",\"index\":"<<index<<",\"q\":";vec(out,q);out<<",\"T1\":";mat(out,fk(a,q1,1));out<<",\"T2\":";mat(out,fk(a,q2,2));n.FK(q);out<<",\"T_chain\":";mat(out,n.get_FK_solution());out<<'}';
    };
    for(int i=0;i<2;++i)closed_row("raw_endpoint",endpoints[i],i);
    State perturbed=endpoints[0];perturbed[0]+=.1;closed_row("closure_negative",perturbed,0);
    for(int i=0;i<10;++i){State q=endpoints[i%2];q[i/2]+=(i%2?-.01:.01);auto t0=std::chrono::steady_clock::now();bool ok=n.GD(q);double dt=std::chrono::duration<double>(std::chrono::steady_clock::now()-t0).count();
        row();out<<"{\"kind\":\"nr\",\"index\":"<<i<<",\"input\":";vec(out,q);out<<",\"success\":"<<(ok?"true":"false")<<",\"wall_s\":"<<dt;if(ok){State s=n.get_GD_result();out<<",\"solution\":";vec(out,s);State q1(s.begin(),s.begin()+6),q2(s.begin()+6,s.end());out<<",\"T1\":";mat(out,fk(a,q1,1));out<<",\"T2\":";mat(out,fk(a,q2,2));n.FK(s);out<<",\"T_chain\":";mat(out,n.get_FK_solution());}out<<'}';out.flush();
    }
    const State author_elbow={.37,.21,-3.1416/2,.48,.71,-.31};
    std::vector<State> fixtures={author_elbow,author_elbow,author_elbow};fixtures[1][4]=0;fixtures[2][2]=0;
    const char *names[]={"author_elbow_only","wrist_zero","regular"};
    for(int k=0;k<3;++k){row();out<<"{\"kind\":\"jacobian_fixture\",\"name\":\""<<names[k]<<"\",\"robot\":2,\"q\":";vec(out,fixtures[k]);out<<",\"T\":";mat(out,fk(a,fixtures[k],2));out<<",\"Tplus\":[";
        for(int j=0;j<6;++j){if(j)out<<',';auto q=fixtures[k];q[j]+=1e-6;mat(out,fk(a,q,2));}out<<"],\"Tminus\":[";for(int j=0;j<6;++j){if(j)out<<',';auto q=fixtures[k];q[j]-=1e-6;mat(out,fk(a,q,2));}out<<"]}";
    }
    out<<"\n]}\n";return out.good()?0:2;
}
