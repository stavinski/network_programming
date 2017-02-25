/*
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 */

#include <arpa/inet.h>
#include <linux/if_packet.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <net/if.h>
#include <netinet/ether.h>
#include <netinet/ip.h>
#include <netinet/udp.h>

#define MY_DEST_MAC0	0xFF
#define MY_DEST_MAC1	0xFF
#define MY_DEST_MAC2	0xFF
#define MY_DEST_MAC3	0xFF
#define MY_DEST_MAC4	0xFF
#define MY_DEST_MAC5	0xFF

#define DEFAULT_IF	"eth0"
#define BUF_SIZ		1024
#define PAYLOAD_SIZ	16

void hex_dump(u_char *ptr, int size)
{
	printf("HEX: ");

	while (size > 0)
	{
		printf("%2x ", (u_char)*ptr);
		size--;
		ptr++;
	}

	printf("\n");
}

// the pseudo header required for checksum for UDP/TCP
struct pseudohdr
{
	u_int32_t saddr;
	u_int32_t daddr;
	u_int8_t reserved;
	u_int8_t protocol;
	u_int16_t len;
};

ushort csum(ushort *ptr, int bytes)
{
	long sum;
  	ushort oddbyte;
  	short answer;

  sum=0;
  while(bytes>1) {
    sum+=*ptr++;
    bytes-=2;
  }
  if(bytes==1) {
    oddbyte=0;
    *((u_char*)&oddbyte)=*(u_char*)ptr;
    sum+=oddbyte;
  }

  sum = (sum>>16)+(sum & 0xffff);
  sum = sum + (sum>>16);
  answer=(short)~sum;

  return(answer);
}

int main(int argc, char *argv[])
{
	int sockfd;
	struct ifreq if_idx;
	struct ifreq if_mac;
	int tx_len = 0;
	
	// buffer packet to send
	char sendbuf[BUF_SIZ];

	// headers
	struct ether_header *eh = (struct ether_header *) sendbuf;
	struct iphdr *iph = (struct iphdr *) (sendbuf + sizeof(struct ether_header));
	struct udphdr *udp = (struct udphdr*) (sendbuf + sizeof(struct ether_header) + sizeof(struct iphdr));
	
	struct sockaddr_ll socket_address;
	char ifName[IFNAMSIZ];
	
	/* Get interface name */
	if (argc > 1)
		strcpy(ifName, argv[1]);
	else
		strcpy(ifName, DEFAULT_IF);

	/* Open RAW socket to send on */
	if ((sockfd = socket(AF_PACKET, SOCK_RAW, IPPROTO_RAW)) == -1) {
	    perror("socket");
	}

	/* Get the index of the interface to send on */
	memset(&if_idx, 0, sizeof(struct ifreq));
	strncpy(if_idx.ifr_name, ifName, IFNAMSIZ-1);
	if (ioctl(sockfd, SIOCGIFINDEX, &if_idx) < 0)
	    perror("SIOCGIFINDEX");
	    
	/* Get the MAC address of the interface to send on */
	memset(&if_mac, 0, sizeof(struct ifreq));
	strncpy(if_mac.ifr_name, ifName, IFNAMSIZ-1);
	if (ioctl(sockfd, SIOCGIFHWADDR, &if_mac) < 0)
	    perror("SIOCGIFHWADDR");

	/* Construct the Ethernet header */
	memset(sendbuf, 0, BUF_SIZ);
	/* Ethernet header */
	eh->ether_shost[0] = ((uint8_t *)&if_mac.ifr_hwaddr.sa_data)[0];
	eh->ether_shost[1] = ((uint8_t *)&if_mac.ifr_hwaddr.sa_data)[1];
	eh->ether_shost[2] = ((uint8_t *)&if_mac.ifr_hwaddr.sa_data)[2];
	eh->ether_shost[3] = ((uint8_t *)&if_mac.ifr_hwaddr.sa_data)[3];
	eh->ether_shost[4] = ((uint8_t *)&if_mac.ifr_hwaddr.sa_data)[4];
	eh->ether_shost[5] = ((uint8_t *)&if_mac.ifr_hwaddr.sa_data)[5];
	eh->ether_dhost[0] = MY_DEST_MAC0;
	eh->ether_dhost[1] = MY_DEST_MAC1;
	eh->ether_dhost[2] = MY_DEST_MAC2;
	eh->ether_dhost[3] = MY_DEST_MAC3;
	eh->ether_dhost[4] = MY_DEST_MAC4;
	eh->ether_dhost[5] = MY_DEST_MAC5;
	
	/* Ethertype field */
	eh->ether_type = htons(ETH_P_IP);
	tx_len += sizeof(struct ether_header);

	/* IP header */
	iph->ihl = 5;
	iph->version = 4;
	iph->tos = 0;
	iph->id = htons(54321);
	iph->frag_off = 0x00;
	iph->ttl = 255;
	iph->protocol = IPPROTO_UDP;
	iph->check = 0;
	iph->saddr = inet_addr("127.0.0.1");
	iph->daddr = inet_addr("255.255.255.255");
	
	tx_len += sizeof(struct iphdr);
	tx_len += sizeof(struct udphdr);

	iph->tot_len = htons(tx_len + PAYLOAD_SIZ);
	iph->check = csum((ushort*)iph, sizeof(struct iphdr));
	printf("ip header checksum: %x\n", iph->check);
	
	// UDP header
	udp->source = htons(INADDR_ANY);
	udp->dest = htons(9002);
	udp->check = 0; // set to zero before checksum performed
	udp->len = htons(sizeof(struct udphdr) + PAYLOAD_SIZ); // header and payload
		
	// set the payload
	memset(sendbuf + tx_len, 1, PAYLOAD_SIZ);

	// pseudo header for checksum, allocate enough buffer on the stack
	char pbuf[sizeof(struct pseudohdr) + sizeof(struct udphdr) + PAYLOAD_SIZ];

	// point to first block of memory
	struct pseudohdr *phdr = (struct pseudohdr*)pbuf;
		
	// fill with values
	phdr->saddr = iph->saddr;
	phdr->daddr = iph->daddr;
	phdr->reserved = 0;
	phdr->protocol = iph->protocol;
	phdr->len = udp->len;
		
	// copy the udp header after pseudo header
	memcpy((u_char*)phdr + sizeof(struct pseudohdr), udp, sizeof(struct udphdr));

	// then the payload after udp header
	memcpy((u_char*)phdr + sizeof(struct pseudohdr) + sizeof(struct udphdr), sendbuf + tx_len, PAYLOAD_SIZ);
	
	//hex_dump((u_char*)phdr, sizeof(struct pseudohdr) + sizeof(struct udphdr) + PAYLOAD_SIZ);

	udp->check = csum((ushort*)phdr, sizeof(struct pseudohdr) + sizeof(struct udphdr) + PAYLOAD_SIZ);
	printf("udp header checksum: %x\n", udp->check);
	
	/* Index of the network device */
	socket_address.sll_ifindex = if_idx.ifr_ifindex;
	/* Address length*/
	socket_address.sll_halen = ETH_ALEN;
	/* Destination MAC */
	socket_address.sll_addr[0] = MY_DEST_MAC0;
	socket_address.sll_addr[1] = MY_DEST_MAC1;
	socket_address.sll_addr[2] = MY_DEST_MAC2;
	socket_address.sll_addr[3] = MY_DEST_MAC3;
	socket_address.sll_addr[4] = MY_DEST_MAC4;
	socket_address.sll_addr[5] = MY_DEST_MAC5;

	/* Send packet */
	if (sendto(sockfd, sendbuf, tx_len + PAYLOAD_SIZ, 0, (struct sockaddr*)&socket_address, sizeof(struct sockaddr_ll)) < 0)
	{	    
	    perror("sendto");
	    exit(EXIT_FAILURE);
	}
	
	puts("send succeeded");
	
	// cleanup	
	close(sockfd);	
	
	return 0;
}