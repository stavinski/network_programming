#include "sender.h"

int32_t icmp_open(uint32_t daddr, sockaddr_in *servaddr)
{
    int32_t sockfd;

    sockfd = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP);

    // could not open socket
    if (sockfd < 0)
        return -1;

    // server address settings
    servaddr->sin_family = AF_INET;
    servaddr->sin_addr.s_addr = daddr;
    memset(&servaddr->sin_zero, 0, sizeof(servaddr->sin_zero));

    return sockfd;
}

int32_t icmp_send(int32_t sockfd, sockaddr_in *servaddr, icmp_send_packet send_packet)
{
    int32_t payload_size = send_packet.payload_size;
    const u_char *payload = send_packet.payload;
    int32_t seq = send_packet.sequence;
    char packet[payload_size + ICMP_ECHO_LEN];
    icmphdr *icmp = (icmphdr *)packet;

    // fill payload
    memcpy(packet + ICMP_ECHO_LEN, payload, payload_size);

#ifdef DEBUG
    DBG_HEX_DUMP("payload", packet + ICMP_ECHO_LEN, payload_size)
#endif

    icmp->type = ICMP_ECHO;
    icmp->code = 0;
    icmp->checksum = 0;
    icmp->un.echo.id = htons(rand());
    icmp->un.echo.sequence = htons(seq);
    icmp->checksum = checksum((uint16_t *)packet, ICMP_ECHO_LEN + payload_size);

#ifdef DEBUG
    DBG_HEX_DUMP("icmp header", icmp, ICMP_ECHO_LEN)
#endif // DEBUG

    return sendto(sockfd, packet, ICMP_ECHO_LEN + payload_size, 0, (sockaddr*)servaddr, sizeof(sockaddr_in));
}
