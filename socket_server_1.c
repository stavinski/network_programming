#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>

#include <netinet/in.h>

#define BUF_SIZE 256

int main()
{
	int sock, port;
	port = 9002;
	char server_msg[BUF_SIZE] = "You have reached the server!";	
	
	sock = socket(AF_INET, SOCK_STREAM, 0);
	
	struct sockaddr_in server_address;
 	server_address.sin_family = AF_INET;
 	server_address.sin_port = htons(port);
 	server_address.sin_addr.s_addr = INADDR_ANY;
    	
   if (bind(sock, (struct sockaddr*)&server_address, sizeof(server_address)) == -1)
   {
   	perror("bind");
   	exit(EXIT_FAILURE);
   }
   
   if (listen(sock, 1) == -1)
   {
   	perror("listen");
   	exit(EXIT_FAILURE);
   }
   
   int client_socket = accept(sock, NULL, NULL);
	if (client_socket == -1)
	   {
   	perror("listen");
   	exit(EXIT_FAILURE);
   }
   
   send(client_socket, server_msg, sizeof(server_msg), 0);
	
	close(client_socket);
	close(sock);	
	
	return EXIT_SUCCESS;
}
