#include <stdlib.h>
#include <stdio.h>

#include <sys/types.h>
#include <sys/socket.h>

#include <netinet/in.h>

#define BUF_SIZE 256

int main()
{
  int sock, port, conn_status;
  port = 9002;
  sock = socket(AF_INET, SOCK_STREAM, 0);
  
  struct sockaddr_in server_address;
  server_address.sin_family = AF_INET;
  server_address.sin_port = htons(port);
  server_address.sin_addr.s_addr = INADDR_ANY;
  
  conn_status = connect(sock, (struct sockaddr *)&server_address, sizeof(server_address)); 

  if (conn_status == -1)
  {
    perror("connect");
    exit(EXIT_FAILURE);
	}
	
	char response[BUF_SIZE]; 
	recv(sock, &response, sizeof(response), 0);
	
	printf("RESP:\n\n%s\n", response);
	
	close(sock);

  return EXIT_SUCCESS;
}
