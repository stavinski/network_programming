#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <errno.h>
#include <signal.h>

#include <unistd.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/ip.h>
#include <netinet/ip_icmp.h>

#include "networking.h"

#define PACKET_SIZE 1024

void usage(char *ctx)
{
    printf("usage: %s <destination_ip>\n", ctx);
}

int32_t sockfd;

void handle_signal(int signalno)
{
    if (signalno == SIGINT)
    {
        close(sockfd);
        exit(EXIT_SUCCESS);
    }
}

int main(int argc, char *argv[])
{
    uint32_t daddr;
    icmphdr icmp;
    sockaddr_in servaddr;

    if (argc < 2)
    {
        usage(argv[0]);
        exit(EXIT_SUCCESS);
    }

    if (signal(SIGINT, handle_signal) == SIG_ERR)
    {
        perror("signal");
        exit(EXIT_FAILURE);
    }

    daddr = inet_addr(argv[1]);
    sockfd = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP);

    if (sockfd < 0)
    {
        perror("socket");
        exit(EXIT_FAILURE);
    }

    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = daddr;
    memset(&servaddr.sin_zero, 0, sizeof(servaddr.sin_zero));

    icmp.type = ICMP_ECHO;
    icmp.code = 0;
    icmp.checksum = 0;
    icmp.un.echo.id = htons(rand());

    uint32_t seq;

    // infinite loop handled via SIGINT
    for (seq = 0;;seq++)
    {
        icmp.un.echo.sequence = htons(seq);
        icmp.checksum = 0;
        icmp.checksum = checksum((uint16_t *)&icmp, sizeof(icmphdr));

        int32_t bytes_sent = sendto(sockfd, &icmp, ICMP_ECHO_LEN, 0, (sockaddr*)&servaddr, sizeof(sockaddr_in));

        if (bytes_sent < 0)
        {
            perror("sendto");
            exit(EXIT_FAILURE);
        }

        printf("ping to %s\tbytes sent: %d\n", argv[1], bytes_sent);
        fflush(stdout);
        sleep(2);
    }

    return EXIT_SUCCESS;
}
