#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>

#include <sys/ioctl.h>
#include <sys/socket.h>
#include <linux/if_packet.h>
#include <arpa/inet.h>
#include <netinet/ether.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <netinet/tcp.h>

#include "../includes/debugging.h"
#include "../includes/networking.h"

#define TCP_PORT 9002
#define TCP_PACKET_SIZE 1024

// exposed TCP functions
int32_t syn(int32_t sockfd);
int32_t synack(int32_t sockfd);
int32_t ack(int32_t sockfd);
int32_t data(int32_t sockfd, const char *payload);