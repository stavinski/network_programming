#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <unistd.h>

#include <sys/socket.h>
#include <arpa/inet.h>

#ifdef DEBUG
    #include "../includes/debugging.h"
#endif

#include "handshaking.h"

// handle to the socket
int32_t sockfd;

int main()
{
    int32_t daddr, result;
    daddr = inet_addr("192.168.161.2");
    
    sockfd = socket(AF_INET, SOCK_RAW, IPPROTO_TCP);
    if (sockfd < 0)
    {
        perror("connect");
        exit(EXIT_FAILURE);
    }
   
    result = syn(sockfd);
    
   
    close(sockfd);
    
    return EXIT_SUCCESS;
}