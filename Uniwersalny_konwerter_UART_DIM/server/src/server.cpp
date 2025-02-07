#include <iostream>
#include <string>
#include <fcntl.h>
#include <errno.h>
#include <termios.h>
#include <unistd.h>
#include <cstring>
#include <vector>

#include "server.hpp"

Server::Server(std::string name) : DimRpc(name.c_str(), "C", "C")
{
    _serial_port = open("/dev/ttyGS0", O_RDWR);
    if (_serial_port < 0)
    {
        throw std::runtime_error("Error from open " + std::string(strerror(errno)));
    }
    
    if (tcgetattr(_serial_port, &_tty) != 0)
    {
        throw std::runtime_error("Error from tcgetattr " + std::string(strerror(errno)));
    }
    _tty.c_cflag &= ~PARENB;
    _tty.c_cflag &= ~CSTOPB;
    _tty.c_cflag &= ~CSIZE;
    _tty.c_cflag |= CS8;
    _tty.c_cflag |= CREAD | CLOCAL;
    _tty.c_iflag |= IXON | IXOFF | IXANY;
    _tty.c_lflag &= ~(ICANON | ECHO | ECHOE | ECHONL | ISIG);
    _tty.c_iflag &= ~(IGNBRK | BRKINT | PARMRK | ISTRIP | INLCR | IGNCR | ICRNL);
    _tty.c_oflag &= ~OPOST;
    _tty.c_oflag &= ~ONLCR;
    _tty.c_cc[VTIME] = 10;
    _tty.c_cc[VMIN] = 0;

    cfsetispeed(&_tty, B9600);
    cfsetospeed(&_tty, B9600);
    
    if (tcsetattr(_serial_port, TCSANOW, &_tty) != 0)
    {
        throw std::runtime_error("Error from tcsetattr " + std::string(strerror(errno)));
    }
    
    std::cout << "Server created!" << std::endl;
}

Server::~Server()
{
    close(_serial_port);
}

void Server::sendMessage(std::string& message)
{
    std::vector<char> inBuff(message.begin(), message.end());
    inBuff.push_back('\r');
    inBuff.push_back('\n');
    
    ssize_t bytesW = write(_serial_port, inBuff.data(), inBuff.size());
    if (bytesW < 0)
    {
        throw std::runtime_error("Error writing to serial port: " + std::string(strerror(errno)));
    }
}

std::string Server::readMessage()
{
    std::vector<char> outBuff(BUFFER_SIZE);
    
    ssize_t bytesR = read(_serial_port, outBuff.data(), outBuff.size());
    if (bytesR < 0)
    {
        throw std::runtime_error("Error reading from serial port: " + std::string(strerror(errno)));
    }
    
    outBuff[bytesR] = '\0';
    return std::string(outBuff.data());
}


void Server::rpcHandler()
{
    std::string message = std::string(getString());
    sendMessage(message);
    std::cout << "received from client: " << message << std::endl;
    
    std::string response;
    try {
        response = readMessage();
    } catch (const std::runtime_error& e) {
        response = "ERR:\"" + std::string(e.what()) + "\"";
    }
    
    std::cout << "received " << response << '\n';
    
    char* buffer = new char[response.size() + 1];
    std::strcpy(buffer, response.c_str());
    
    setData(buffer);
    
    delete[] buffer;
}
