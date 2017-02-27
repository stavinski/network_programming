#include <stdlib.h>

#include "networking.h"

uint16_t checksum(uint16_t *ptr, size_t bytes)
{
    long sum;
    ushort oddbyte;
    short answer;

    sum = 0;
    while(bytes > 1)
    {
        sum += *ptr++;
        bytes -= 2;
    }
    if(bytes == 1) {
        oddbyte = 0;
        *((u_char*)&oddbyte) = *(u_char*)ptr;
        sum += oddbyte;
    }

    sum = (sum >> 16) + (sum & 0xffff);
    sum = sum + (sum >> 16);
    answer = (short)~sum;

    return(answer);
}
