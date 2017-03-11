#include <stdint.h>
#include <netinet/ip_icmp.h>
#include <netinet/tcp.h>
#include <netinet/in.h>

#ifndef NETWORKING_HEADER_H_
#define NETWORKING_HEADER_H_

#define ICMP_ECHO_LEN 8

struct pseudohdr
{
    uint32_t saddr;
    uint32_t daddr;
    uint8_t reserved;
    uint8_t protocol;
    uint16_t len;
};

// saves typing
typedef struct pseudohdr pseudohdr;
typedef struct iphdr iphdr;
typedef struct icmphdr icmphdr;
typedef struct tcphdr tcphdr;
typedef struct sockaddr sockaddr;
typedef struct sockaddr_in sockaddr_in;

uint16_t checksum(uint16_t *data, size_t size);

#endif // NETWORKING_HEADER_H_
