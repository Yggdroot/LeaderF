#ifndef MYSTDINT_H_
#define MYSTDINT_H_


#if defined(_MSC_VER) && (_MSC_VER < 1600) /* Visual C++ 2010 (10.0) is 1600 */

typedef signed char        int8_t;
typedef unsigned char      uint8_t;

typedef short              int16_t;
typedef unsigned short     uint16_t;

typedef int                int32_t;
typedef unsigned int       uint32_t;

typedef long long          int64_t;
typedef unsigned long long uint64_t;

#else

#include <stdint.h>

#endif

#endif
