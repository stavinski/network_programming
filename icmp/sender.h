#ifndef SENDER_H_INCLUDED
#define SENDER_H_INCLUDED

#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <stdio.h>
#include <unistd.h>

#include <arpa/inet.h>
#include <netinet/ip_icmp.h>

#include "networking.h"

#ifdef DEBUG
    #include "debugging.h"
#endif // DEBUG

typedef struct icmp_send_packet
{
    const u_char *payload;
    size_t payload_size;
    int32_t sequence;
} icmp_send_packet;

// opens a socket connection and populates the sockaddr_in if socket was opened socket handle is returned
int32_t icmp_open(uint32_t daddr, sockaddr_in *servaddr);

// sends ICMP packet with deails supplied and returns bytes sent
int32_t icmp_send(int32_t sockfd, sockaddr_in *servaddr, icmp_send_packet send_packet);

#endif // SENDER_H_INCLUDED
