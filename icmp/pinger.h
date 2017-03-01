#ifndef PINGER_INCLUDED_H_
#define PINGER_INCLUDED_H_

#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <stdbool.h>

#include <arpa/inet.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <netinet/ip_icmp.h>

#include "networking.h"

#ifdef DEBUG
    #include "debugging.h"
#endif

#define PACKET_SIZE 1024

// the icmp echo specific correlation fields
typedef struct echo
{
    uint16_t id;
    uint16_t sequence;
} echo;

int32_t icmp_open();
int32_t icmp_send(int32_t sockfd, echo icmp_echo, uint32_t daddr, const u_char *payload, size_t payload_size);
int32_t icmp_receive(int32_t sockfd, echo icmp_echo);
int32_t icmp_close(int32_t sockfd);

#endif // PINGER_INCLUDED_H_
