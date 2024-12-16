// /*
// Copyright (c) 2015-2016 Xiaowei Zhu, Tsinghua University

//    Licensed under the Apache License, Version 2.0 (the "License");
//    you may not use this file except in compliance with the License.
//    You may obtain a copy of the License at

//        http://www.apache.org/licenses/LICENSE-2.0

//    Unless required by applicable law or agreed to in writing, software
//    distributed under the License is distributed on an "AS IS" BASIS,
//    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//    See the License for the specific language governing permissions and
//    limitations under the License.
// */

// #ifndef MPI_HPP
// #define MPI_HPP

// #include <stdio.h>
// #include <stdlib.h>
// #include <assert.h>
// #include <mpi.h>

// template <typename T>
// MPI_Datatype get_mpi_data_type() {
//   if (std::is_same<T, char>::value) {
//     return MPI_CHAR;
//   } else if (std::is_same<T, unsigned char>::value) {
//     return MPI_UNSIGNED_CHAR;
//   } else if (std::is_same<T, int>::value) {
//     return MPI_INT;
//   } else if (std::is_same<T, unsigned>::value) {
//     return MPI_UNSIGNED;
//   } else if (std::is_same<T, long>::value) {
//     return MPI_LONG;
//   } else if (std::is_same<T, unsigned long>::value) {
//     return MPI_UNSIGNED_LONG;
//   } else if (std::is_same<T, float>::value) {
//     return MPI_FLOAT;
//   } else if (std::is_same<T, double>::value) {
//     return MPI_DOUBLE;
//   } else {
//     printf("type not supported\n");
//     exit(-1);
//   }
// }

// class MPI_Instance {
//   int partition_id;
//   int partitions;
// public:
//   MPI_Instance(int * argc, char *** argv) {
//     int provided;
//     MPI_Init_thread(argc, argv, MPI_THREAD_MULTIPLE, &provided);
//     MPI_Comm_rank(MPI_COMM_WORLD, &partition_id);
//     MPI_Comm_size(MPI_COMM_WORLD, &partitions);
//     #ifdef PRINT_DEBUG_MESSAGES
//     if (partition_id==0) {
//       printf("thread support level provided by MPI: ");
//       switch (provided) {
//         case MPI_THREAD_MULTIPLE:
//           printf("MPI_THREAD_MULTIPLE\n"); break;
//         case MPI_THREAD_SERIALIZED:
//           printf("MPI_THREAD_SERIALIZED\n"); break;
//         case MPI_THREAD_FUNNELED:
//           printf("MPI_THREAD_FUNNELED\n"); break;
//         case MPI_THREAD_SINGLE:
//           printf("MPI_THREAD_SINGLE\n"); break;
//         default:
//           assert(false);
//       }
//     }
//     #endif
//   }
//   ~MPI_Instance() {
//     MPI_Finalize();
//   }
//   void pause() {
//     if (partition_id==0) {
//       getchar();
//     }
//     MPI_Barrier(MPI_COMM_WORLD);
//   }
// };

// #endif
#ifndef MPI_HPP
#define MPI_HPP

#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <mpi.h>
#include <iostream>
#include <fstream>
#include <sstream>
#include <chrono>
#include <string>
#include <type_traits>

// Utility to log MPI call details
#define LOG_MPI_CALL(rank, func, details, duration) \
  do { \
    std::ofstream log_file; \
    log_file.open("mpi_logs.log", std::ios::app); \
    log_file << "Rank " << rank << " - " << func << ": " << details << " - Time: " << duration << "s\n"; \
    log_file.close(); \
  } while (0)

// Get MPI Data Type
template <typename T>
MPI_Datatype get_mpi_data_type() {
  if (std::is_same<T, char>::value) {
    return MPI_CHAR;
  } else if (std::is_same<T, unsigned char>::value) {
    return MPI_UNSIGNED_CHAR;
  } else if (std::is_same<T, int>::value) {
    return MPI_INT;
  } else if (std::is_same<T, unsigned>::value) {
    return MPI_UNSIGNED;
  } else if (std::is_same<T, long>::value) {
    return MPI_LONG;
  } else if (std::is_same<T, unsigned long>::value) {
    return MPI_UNSIGNED_LONG;
  } else if (std::is_same<T, float>::value) {
    return MPI_FLOAT;
  } else if (std::is_same<T, double>::value) {
    return MPI_DOUBLE;
  } else {
    printf("type not supported\n");
    exit(-1);
  }
}

// Wrapped MPI Send function
int MPI_Send_Wrapped(const void *buf, int count, MPI_Datatype datatype, int dest, int tag, MPI_Comm comm) {
  int rank;
  MPI_Comm_rank(MPI_COMM_WORLD, &rank);

  double start_time = MPI_Wtime();
  int result = MPI_Send(buf, count, datatype, dest, tag, comm);
  double end_time = MPI_Wtime();

  std::ostringstream details;
  details << "Dest=" << dest << ", Count=" << count << ", Tag=" << tag;
  LOG_MPI_CALL(rank, "MPI_Send", details.str(), end_time - start_time);

  return result;
}

// Wrapped MPI Recv function
int MPI_Recv_Wrapped(void *buf, int count, MPI_Datatype datatype, int source, int tag, MPI_Comm comm, MPI_Status *status) {
  int rank;
  MPI_Comm_rank(MPI_COMM_WORLD, &rank);

  double start_time = MPI_Wtime();
  int result = MPI_Recv(buf, count, datatype, source, tag, comm, status);
  double end_time = MPI_Wtime();

  std::ostringstream details;
  details << "Source=" << source << ", Count=" << count << ", Tag=" << tag;
  LOG_MPI_CALL(rank, "MPI_Recv", details.str(), end_time - start_time);

  return result;
}

// MPI Instance class
class MPI_Instance {
  int partition_id;
  int partitions;
public:
  MPI_Instance(int * argc, char *** argv) {
    int provided;
    MPI_Init_thread(argc, argv, MPI_THREAD_MULTIPLE, &provided);
    MPI_Comm_rank(MPI_COMM_WORLD, &partition_id);
    MPI_Comm_size(MPI_COMM_WORLD, &partitions);
    #ifdef PRINT_DEBUG_MESSAGES
    if (partition_id==0) {
      printf("thread support level provided by MPI: ");
      switch (provided) {
        case MPI_THREAD_MULTIPLE:
          printf("MPI_THREAD_MULTIPLE\n"); break;
        case MPI_THREAD_SERIALIZED:
          printf("MPI_THREAD_SERIALIZED\n"); break;
        case MPI_THREAD_FUNNELED:
          printf("MPI_THREAD_FUNNELED\n"); break;
        case MPI_THREAD_SINGLE:
          printf("MPI_THREAD_SINGLE\n"); break;
        default:
          assert(false);
      }
    }
    #endif
  }
  ~MPI_Instance() {
    MPI_Finalize();
  }
  void pause() {
    if (partition_id==0) {
      getchar();
    }
    MPI_Barrier(MPI_COMM_WORLD);
  }
};

#endif
