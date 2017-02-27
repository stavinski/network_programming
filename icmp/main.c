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

#define PAYLOAD_SIZE 56

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
    sockaddr_in servaddr;
    char packet[PAYLOAD_SIZE + ICMP_ECHO_LEN];
    char payload[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890ABCDEFGHIJKLMNOPQR";
    icmphdr *icmp = (icmphdr *)packet;

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

    // server address settings
    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = daddr;
    memset(&servaddr.sin_zero, 0, sizeof(servaddr.sin_zero));

    // fill payload
    memcpy(packet + ICMP_ECHO_LEN, payload, sizeof(PAYLOAD_SIZE));

    // constant ICMP fields
    icmp->type = ICMP_ECHO;
    icmp->code = 0;
    icmp->checksum = 0;
    icmp->un.echo.id = htons(rand());

    uint32_t seq;

    // infinite loop handled via SIGINT
    for (seq = 0;;seq++)
    {
        // dynamic ICMP fields
        icmp->checksum = 0;
        icmp->un.echo.sequence = htons(seq);
        icmp->checksum = checksum((uint16_t *)packet, ICMP_ECHO_LEN + PAYLOAD_SIZE);

        int32_t bytes_sent = sendto(sockfd, packet, ICMP_ECHO_LEN + PAYLOAD_SIZE, 0, (sockaddr*)&servaddr, sizeof(sockaddr_in));

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
