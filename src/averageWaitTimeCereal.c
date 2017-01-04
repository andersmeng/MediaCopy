#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#define MAXITER 1000000

/* This little program estimates the average wait time for receiving arrival of four different subject when the subjects are chosen uniformly at random. This can also be calculated with pencil.*/
int main(){
  int i,c,n,j;
  time_t t;
  srand((unsigned) time(&t));
  int success=1;
  unsigned int res=0;
  unsigned int b=1;
  double avg = 0;
  c=0;

  for(j=0; j<MAXITER;j++){
  while(success){  
    i = rand() % 4 + 1;
    res = res | b << (i-1);
    /*printf("i=%d, res=%d\n", i, res);*/
    if(res==15){
      success=0;
      avg = avg + c;
      c=0;
      res=0;
    };
    c++;
  };
  success=1;
  };

  printf("Average is = %1.5f\n",avg/MAXITER);
  return 0;
}
