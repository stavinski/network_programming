#ifndef LISTENER_INCLUDED_H_
#define LISTENER_INCLUDED_H_

#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>

#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <netinet/ip_icmp.h>

#include "networking.h"

uint32_t icmp_listen(uint32_t saddr);
uint32_t icmp_stop();

#endif // LISTENER_INCLUDED_H_
