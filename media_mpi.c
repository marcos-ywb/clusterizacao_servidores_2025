#include <mpi.h>
#include <stdio.h>

int main(int argc, char** argv) {
    int rank, size;
    float media_local, max_local;
    float medias[100];
    float maximos[100];

    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank); 
    MPI_Comm_size(MPI_COMM_WORLD, &size); 

    if (size < 2) {
        if (rank == 0) {
            printf("Execute com pelo menos 2 processos.\n");
        }
        MPI_Finalize();
        return 0;
    }

    media_local = (rank + 1) * 1.5;
    max_local   = (rank + 1) * 10.0;

    MPI_Gather(&media_local, 1, MPI_FLOAT,
               medias, 1, MPI_FLOAT,
               0, MPI_COMM_WORLD);

    MPI_Gather(&max_local, 1, MPI_FLOAT,
               maximos, 1, MPI_FLOAT,
               0, MPI_COMM_WORLD);

    if (rank == 0) {
        printf("\n[Processo 0] Dados coletados:\n");
        for (int i = 0; i < size; i++) {
            printf("Processo %d -> Média: %.2f | Máximo: %.2f\n", i, medias[i], maximos[i]);
        }
    }

    MPI_Finalize(); 
    return 0;
}

