#include "listener.h"

uint32_t icmp_listen(uint32_t saddr)
{
    uint32_t sockfd;
    sockaddr_in servaddr;

    sockfd = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP);

    if (sockfd < 0)
    {
        perror("icmp_listen:sockfd");
        return -1;
    }

    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = INADDR_ANY;
    memset(&servaddr.sin_zero, 0, sizeof(servaddr.sin_zero));

    if (bind(sockfd, (sockaddr*)&servaddr, sizeof(servaddr)) < 0)
    {
        perror("icmp_listen:bind");
        close(sockfd);
        return -1;
    }

    if (listen(sockfd, 1) < 0)
    {
        perror("icmp_listen:listen");
        close(sockfd);
        return -1;
    }

    return sockfd;
}

uint32_t icmp_stop(uint32_t hndl_listener)
{

}
