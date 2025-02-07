#include <iostream>
#include <string>

#include "dim/dis.hxx"
#include "server.hpp"

int main()
{
    Server server("CEAN/RPC");
    
    DimServer::start("CEAN");
    
    while(true)
    {
        pause();
    }
        
}
