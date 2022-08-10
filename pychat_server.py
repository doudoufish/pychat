import select, sys, pdb
from pychat_util import Hall, Room, Player
import pychat_util
import pychat_client
from concurrent.futures import ThreadPoolExecutor
from socket import AF_INET, SOCK_STREAM, socket

READ_BUFFER = 4096
def pychat_client(sock, client_addr):
    while True:

        msg = sock.recv(READ_BUFFER)
        if not msg:
            break
        sock.sendall(msg)
        

host = sys.argv[1] if len(sys.argv) >= 2 else ''
listen_sock = pychat_util.create_socket((host, pychat_util.PORT))

hall = Hall()
connection_list = []
connection_list.append(listen_sock)
pool = ThreadPoolExecutor(128)


while True:
    ########################################################
    # Player.fileno()
    # select — Waiting for I/O completion
    ########################################################
    read_players, write_players, error_sockets = select.select(connection_list, [], [])
    for player in read_players:
        #####################################
        # new connection, player is a socket
        #####################################
        if player is listen_sock: 
            new_socket, add = player.accept()
            pool.submit(pychat_client,new_socket,add)
            new_player = Player(new_socket)
            connection_list.append(new_player)
            hall.welcome_new(new_player)

        #####################################
        # new message
        #####################################
        else:  
            msg = player.socket.recv(READ_BUFFER)
            if msg:
                msg = msg.decode().lower()
                hall.handle_msg(player, msg)
            else:
                player.socket.close()
                connection_list.remove(player)

    #####################################
    # close error sockets
    #####################################
    for sock in error_sockets: 
        sock.close()
        connection_list.remove(sock)
        
        
        
