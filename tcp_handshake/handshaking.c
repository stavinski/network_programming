#include "handshaking.h"

int32_t syn(int32_t sockfd)
{
    u_char packet[sizeof(tcphdr)];
    
    tcphdr *tcp = (tcphdr *)packet;
    sockaddr_in servaddr;
    int32_t bytes_sent;
    
    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(TCP_PORT);
    servaddr.sin_addr.s_addr = inet_addr("192.168.161.143");
    memset(&servaddr.sin_zero, 0, sizeof(servaddr.sin_zero));
    
    tcp->source = htons(inet_addr("192.168.161.143"));
    tcp->dest = htons(TCP_PORT);
    tcp->seq = 0;
    tcp->ack_seq = 0;
    tcp->doff = 5;
    
    // tcp flags
    tcp->fin = 0;
    tcp->syn = 1;
    tcp->rst = 0;
    tcp->psh = 0;
    tcp->ack = 0;
    tcp->urg = 0;
    
    tcp->window = htons(5840);
    tcp->check = 0;
    tcp->urg_ptr = 0;
    
    DBG_HEX_DUMP("tcp", tcp, sizeof(tcphdr));
    
    bytes_sent = sendto(sockfd, packet, sizeof(tcphdr), 0, (sockaddr*) &servaddr, sizeof(sockaddr_in));
    if (bytes_sent < 0)
    {
        perror("sendto");
        return -1;
    }
    
    return 0;
}