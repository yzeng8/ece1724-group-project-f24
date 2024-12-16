#include <mpi.h>
#include <stdio.h>
#include <unistd.h> // Include this for gethostname

int main(int argc, char** argv) {
    MPI_Init(&argc, &argv);

    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    char hostname[256];
    gethostname(hostname, 256); // Retrieves the hostname of the node

    printf("Hello from Rank %d out of %d on Host %s\n", rank, size, hostname);

    MPI_Finalize();
    return 0;
}
