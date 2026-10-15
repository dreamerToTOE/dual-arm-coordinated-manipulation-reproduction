// Technical PQP controls only: no robot configuration, IK, sampler or planner.
#include <algorithm>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <string>
#include "PQP.h"

int main(int argc,char **argv) {
    if(argc!=2) return 64;
    std::ifstream in(argv[1]);int count;
    if(!(in>>count)||count<=0) return 65;
    double low[3],high[3];
    for(int k=0;k<3;k++){low[k]=std::numeric_limits<double>::infinity();high[k]=-low[k];}
    PQP_Model mesh;
    if(mesh.BeginModel(count)!=0)return 66;
    for(int i=0;i<count;i++) {
        PQP_REAL points[3][3];
        for(int j=0;j<3;j++)for(int k=0;k<3;k++){
            if(!(in>>points[j][k])||!std::isfinite(points[j][k]))return 67;
            low[k]=std::min(low[k],double(points[j][k]));high[k]=std::max(high[k],double(points[j][k]));
        }
        if(mesh.AddTri(points[0],points[1],points[2],i)!=0)return 68;
    }
    if(mesh.EndModel()!=0)return 69;
    PQP_REAL rotation[3][3]={{1,0,0},{0,1,0},{0,0,1}};
    PQP_REAL zero[3]={0,0,0},far[3]={0,0,0};double diagonal=0;
    for(int k=0;k<3;k++)diagonal+=(high[k]-low[k])*(high[k]-low[k]);
    diagonal=std::sqrt(diagonal);far[0]=2*diagonal+8+1;
    PQP_ToleranceResult same_result,far_result;
    int same_code=PQP_Tolerance(&same_result,rotation,zero,&mesh,rotation,zero,&mesh,8);
    int far_code=PQP_Tolerance(&far_result,rotation,zero,&mesh,rotation,far,&mesh,8);
    int same=same_result.CloserThanTolerance(),away=far_result.CloserThanTolerance();
    std::cout<<std::setprecision(17)<<"{\"triangles\":"<<count<<",\"tolerance_mm\":8,\"aabb_low\":[";
    for(int k=0;k<3;k++){if(k)std::cout<<",";std::cout<<low[k];}
    std::cout<<"],\"aabb_high\":[";for(int k=0;k<3;k++){if(k)std::cout<<",";std::cout<<high[k];}
    std::cout<<"],\"aabb_diagonal_mm\":"<<diagonal<<",\"far_translation_x_mm\":"<<far[0]
             <<",\"same_query_code\":"<<same_code<<",\"same_closer_than_tolerance\":"<<same
             <<",\"far_query_code\":"<<far_code<<",\"far_closer_than_tolerance\":"<<away
             <<",\"passed\":"<<((same_code==0&&far_code==0&&same==1&&away==0)?"true":"false")<<"}"<<std::endl;
    return same_code==0&&far_code==0&&same==1&&away==0?0:1;
}
