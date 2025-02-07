#ifndef SERVER_HPP
#define SERVER_HPP

#include <termios.h>

#include "dim/dis.hxx"

class Server : public DimRpc
{
private:
    void rpcHandler() override;
    int _serial_port;
    termios _tty;
    static constexpr std::size_t BUFFER_SIZE = 256; 

public:
    Server(std::string name);
    ~Server();
    void sendMessage(std::string& message);
    std::string readMessage();
};


#endif //SERVER_HPP
