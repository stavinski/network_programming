#include "pinger.h"

int32_t icmp_send(int32_t sockfd, echo *icmp_echo, uint32_t daddr, const u_char *payload, size_t payload_size)
{
    int32_t bytes_sent;
    struct timespec sent_ts;
    sockaddr_in servaddr;
    char packet[payload_size + ICMP_ECHO_LEN];
    icmphdr *icmp = (icmphdr*)packet;

    // server address settings
    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = daddr;
    memset(&servaddr.sin_zero, 0, sizeof(servaddr.sin_zero));

    // fill payload
    memcpy(packet + ICMP_ECHO_LEN, payload, payload_size);

#ifdef DEBUG
    DBG_HEX_DUMP("payload", packet + ICMP_ECHO_LEN, payload_size)
#endif

    icmp->type = ICMP_ECHO;
    icmp->code = 0;
    icmp->checksum = 0;
    icmp->un.echo.id = htons(icmp_echo->id);
    icmp->un.echo.sequence = htons(icmp_echo->sequence);
    icmp->checksum = checksum((uint16_t *)packet, ICMP_ECHO_LEN + payload_size);

#ifdef DEBUG
    DBG_HEX_DUMP("icmp header", icmp, ICMP_ECHO_LEN)
#endif // DEBUG

    bytes_sent = sendto(sockfd, packet, ICMP_ECHO_LEN + payload_size, 0, (sockaddr*)&servaddr, sizeof(sockaddr_in));
    
    if (bytes_sent < 0)
    {
      perror("sendto");
      return -SEND_FAILURE;
    }
    
    if (clock_gettime(CLOCK_MONOTONIC, &sent_ts) < 0)
    {
      perror("clock_gettime");
      return -SEND_FAILURE;
    }

    // record timestamp was sent at
    icmp_echo->sent = sent_ts;
    
    return bytes_sent;
}

int32_t icmp_receive(int32_t sockfd, echo *icmp_echo)
{
    struct timespec received_ts;
    struct timeval timeout_tv;
    u_char packet[PACKET_SIZE];
    icmphdr *icmp = NULL;
    iphdr *iph = NULL;
    int32_t bytes_received;
    socklen_t client_len = sizeof(sockaddr_in);
    sockaddr_in servaddr, clientaddr;

    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = INADDR_ANY;
    memset(&servaddr.sin_zero, 0, sizeof(servaddr.sin_zero));

    // set timeout for receive
    timeout_tv.tv_sec = 2;
    timeout_tv.tv_usec = 0;
    
    if (setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, (char *)&timeout_tv, sizeof(timeout_tv)) < 0)
    {
        perror("setsockopt");
        return -RECEIVE_FAILURE;
    }
    
    bytes_received = recvfrom(sockfd, packet, PACKET_SIZE, 0, (sockaddr*)&clientaddr, &client_len);
    int32_t last_errno = errno;
    
    if (bytes_received < 0)
    {        
       // check if it is a timeout
       if (last_errno == EAGAIN)
       {
           puts("response timed out");
           return -RECEIVE_TIMEOUT;
       }
       
       perror("icmp_listen:recvfrom");
       return -RECEIVE_FAILURE;
    }
    
    if (clock_gettime(CLOCK_MONOTONIC, &received_ts) < 0)
    {
        perror("clock_gettime");
        return -RECEIVE_FAILURE;
    }
    
#ifdef DEBUG
    DBG_HEX_DUMP("packet", packet, PACKET_SIZE)
#endif // DEBUG

    iph = (iphdr*)packet;
    icmp = (icmphdr*) ((u_char*)packet + sizeof(iphdr));

#ifdef DEBUG
    DBG_HEX_DUMP("ip header", iph, sizeof(iphdr))
    DBG_HEX_DUMP("icmp", icmp, sizeof(icmphdr))
#endif // DEBUG

    if (icmp->type == ICMP_ECHOREPLY)
    {
        uint16_t id = ntohs(icmp->un.echo.id);
        uint16_t seq = ntohs(icmp->un.echo.sequence);

        // correlate using supplied echo fields
        if ((id == icmp_echo->id) && (seq == icmp_echo->sequence))
        {
            char *srcaddr = inet_ntoa(clientaddr.sin_addr);                        
            double diff =  (((double)received_ts.tv_nsec - (double)icmp_echo->sent.tv_nsec) / 1000000);
            printf("%d bytes from %s: icmp_seq=%d ttl=%d time=%.3lfms\n", bytes_received, srcaddr, seq, iph->ttl, diff);
        }
    }

    return bytes_received;
}