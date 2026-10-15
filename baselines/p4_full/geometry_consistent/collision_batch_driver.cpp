// Our transport/instrumentation only. Author collision code remains external.
#include <cmath>
#include <ctime>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>
#include "PQP.h"

static std::vector<std::vector<double>> p4_poses;
static std::vector<int> p4_query_codes;
void p4_pose(PQP_REAL r[3][3], PQP_REAL t[3], double tool=0) {
    std::vector<double> p;
    for(int i=0;i<3;i++) {
        for(int j=0;j<3;j++) p.push_back(r[i][j]);
        p.push_back(t[i]+tool*r[i][0]);
    }
    p4_poses.push_back(p);
}
int p4_query(PQP_ToleranceResult *res, PQP_REAL r1[3][3], PQP_REAL t1[3],
             PQP_Model *o1, PQP_REAL r2[3][3], PQP_REAL t2[3], PQP_Model *o2,
             PQP_REAL tolerance, int qsize=2) {
    int code=PQP_Tolerance(res,r1,t1,o1,r2,t2,o2,tolerance,qsize);
    p4_query_codes.push_back(code);
    return code;
}
#include "collisionDetection.cpp"

int main(int argc,char **argv) {
    if(argc!=2) return 64;
    std::string env=argv[1];
#if P4_MODEL == 0
    collisionDetection checker(env=="II"?900.:1200.,0,0,0,env=="II"?1:2);
#else
    collisionDetection checker;
#endif
    // These fields are observational counters, uninitialized in upstream.
    checker.collisionCheck_counter=0; checker.collisionCheck_time=0;
    std::cout<<std::setprecision(17);
    std::string line;
    while(std::getline(std::cin,line)) {
        std::istringstream input(line); std::vector<double> q;
        double value; while(input>>value) q.push_back(value);
        const size_t n=P4_MODEL==6?18:12;
        if(q.size()!=n) {std::cout<<"P4_COLLISION_RESULT {\"error\":\"DIMENSION\"}"<<std::endl;continue;}
        bool finite=true; for(double x:q) finite=finite&&std::isfinite(x);
        if(!finite) return 65;
        p4_poses.clear(); p4_query_codes.clear(); clock_t start=clock();
#if P4_MODEL == 0
        Matrix points;
        int length=env=="II"?300:500;
        // Exact source PCS::setP, including its collinear triangle policy.
        for(int i=0;i<=length/20;i++) points.push_back({double(i*20),0,0});
        State a(q.begin(),q.begin()+6),b(q.begin()+6,q.end());
        int result=checker.collision_state(points,a,b);
#else
        int result=checker.collision_state(q);
#endif
        double cpu=double(clock()-start)/CLOCKS_PER_SEC;
        std::cout<<"P4_COLLISION_RESULT {\"native_result\":"<<result<<",\"cpu_s\":"<<cpu<<",\"poses\":[";
        for(size_t i=0;i<p4_poses.size();i++) {
            if(i) std::cout<<",";std::cout<<"[";
            for(size_t j=0;j<12;j++){if(j)std::cout<<",";std::cout<<p4_poses[i][j];}std::cout<<"]";
        }
        std::cout<<"],\"query_codes\":[";
        for(size_t i=0;i<p4_query_codes.size();i++){if(i)std::cout<<",";std::cout<<p4_query_codes[i];}
        std::cout<<"]}"<<std::endl;
    }
}
