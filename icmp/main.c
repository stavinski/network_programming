#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <signal.h>

#include <unistd.h>
#include <sys/socket.h>
#include <arpa/inet.h>

#include "pinger.h"

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

// handle to the sockets
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

    int32_t sockfd = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP);
    HR(sockfd, "socket")

    echo icmp_echo;
    icmp_echo.id = getpid();

    int32_t seq, bytes_sent, bytes_received;
    for (seq = 1;; seq++)
    {
        icmp_echo.sequence = seq;
        bytes_sent = icmp_send(sockfd, &icmp_echo, daddr, payload, PAYLOAD_SIZE);
        HR(bytes_sent, "icmp_send")

        bytes_received = icmp_receive(sockfd, &icmp_echo);
        if ((bytes_received < 0) && (bytes_received != -RECEIVE_TIMEOUT))
        {
            perror("icmp_send");
            exit(EXIT_FAILURE);
        }

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
