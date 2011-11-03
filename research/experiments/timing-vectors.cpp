#include <stdio.h>
#include <ctime>  // extra include
#include <stdlib.h>
#include <gsl/gsl_vector.h>

const int VECTOR_SIZE = 50;
const long int TIMING_LOOPS = 1e8;

double getRand() {
    return rand() / (RAND_MAX+1.0);
}

double sum_for_hardcoded(double dvec[]) {
    double sum = 0.0;
    for (int i=VECTOR_SIZE-1; i >= 0; --i) {
        sum += dvec[i];
    }
    return sum;
}

double sum_for_variable(double dvec[], int size) {
    double sum = 0.0;
    for (int i=size-1; i >= 0; --i) {
        sum += dvec[i];
    }
    return sum;
}




int main () {
    // init random
    srand( time(NULL) );
    getRand();

    // init vector
    double dvec[VECTOR_SIZE];
    gsl_vector *gvec;
    gvec = gsl_vector_alloc(VECTOR_SIZE);
    for (int i=VECTOR_SIZE-1; i >= 0; --i) {
        //printf("init index %i\n", i);
        double r = getRand();
        dvec[i] = r;
        gsl_vector_set(gvec, i, r);
    }
    double sum1, sum2, sum3, sum4;

    // init timing
    std::clock_t before, after;
    long int for_hardcoded, for_variable, gsl_hard, gsl_variable;

    // do timing tests
    printf("Timing runs:\n");
    before = std::clock();
    for (long int i=TIMING_LOOPS-1; i >= 0; --i) {
        sum1 = sum_for_hardcoded(dvec);
    }
    after = std::clock();
    for_hardcoded = after-before;
    printf("for_har     \t%li\n", for_hardcoded/1000);

    int size = VECTOR_SIZE;
    before = std::clock();
    for (long int i=TIMING_LOOPS-1; i >= 0; --i) {
        sum2 = sum_for_variable(dvec, size);
    }
    after = std::clock();
    for_variable = after-before;
    printf("for_variable\t%li\n", for_variable/1000);




    gsl_vector_free(gvec);
    printf("\n\n\nignore this: %g %g %g %g\n", sum1, sum2, sum3, sum4);
}
