#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <signal.h>

#include <unistd.h>
#include <sys/socket.h>
#include <arpa/inet.h>

#include "sender.h"

#ifdef DEBUG
    #include "debugging.h"
#endif

#define PAYLOAD_SIZE 56

#define HR(code, s) \
    if (code < 0) { \
        perror(s); \
        exit(EXIT_FAILURE); \
    }

void usage(char *ctx)
{
    printf("usage: %s <destination_ip>\n", ctx);
}

// handle to the socket
int32_t sockfd;

// controls when quit via SIGINT siglnal
volatile sig_atomic_t quit = 0;

// handle sigint
void handle_signal(int signalno)
{
    quit = 1;
}

int main(int argc, char *argv[])
{
    int32_t daddr;
    sockaddr_in servaddr;
    const u_char payload[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890ABCDEFGHIJKLMNOPQR";

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

    if (daddr == -1)
    {
        printf("destination address %s is not a valid IP address\n", argv[1]);
        exit(EXIT_FAILURE);
    }

    sockfd = icmp_open(daddr, &servaddr);
    HR(sockfd, "icmp_open");

    icmp_send_packet packet;
    packet.payload = payload;
    packet.payload_size = PAYLOAD_SIZE;

    int32_t seq, bytes_sent;
    for (seq = 1; ; seq++)
    {
        packet.sequence = seq;
        bytes_sent = icmp_send(sockfd, &servaddr, packet);

        if (bytes_sent < 0)
        {
            perror("icmp_sent");
            exit(EXIT_FAILURE);
        }

        printf("ping to %s\t bytes sent: %d\n", inet_ntoa(servaddr.sin_addr), bytes_sent);
        fflush(stdout);

        sleep(1);

        // if we have had a SIGINT quit and do cleanup
        if (quit == 1)
        {
            close(sockfd);
            exit(EXIT_FAILURE);
        }
    }

    return EXIT_SUCCESS;
}
