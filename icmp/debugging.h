#ifndef DEBUGGING_H_INCLUDED
#define DEBUGGING_H_INCLUDED

#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>

#define DBG_SIZE_OF(x) printf("%d", sizeof(x));
#define DBG_HEX_DUMP(prefix, ptr, size) hex_dump((const char*)prefix, (u_char*)ptr, (size_t)size);

void hex_dump(const char *prefix, u_char *ptr, size_t size);

#endif // DEBUGGING_H_INCLUDED
