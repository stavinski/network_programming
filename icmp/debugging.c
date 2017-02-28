
#include "debugging.h"

void hex_dump(const char *prefix, u_char *ptr, size_t size)
{
    uint32_t i;
    u_char *p = (u_char*)ptr;
    printf("%s hex:\n", prefix);

    for (i = 0; i < size; i++)
    {
        printf("0x%02x ", p[i]);

        if (i % 8 == 0)
        {
            printf("\n");
        }
    }

    printf(("\n"));
}
