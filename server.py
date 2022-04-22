
from asyncio import FIRST_COMPLETED
import copy
from datetime import date, datetime
import signal
from socketserver import ThreadingMixIn
import sys
import xml.etree.ElementTree as ET
from xmlrpc.client import ServerProxy
from xmlrpc.server import SimpleXMLRPCServer
import wikipedia
from concurrent.futures import ThreadPoolExecutor, as_completed, thread



proxy = ServerProxy('http://localhost:5000')
port = 5000
address = '127.0.0.1'


class Page:
    def __init__(self, title, previous_page):
        self.title = title
        self.prev = previous_page

class Loop:
    def __init__(self, loop, visited):
        self.loop = loop
        self.visited = visited




def find_articles(inputlist):
    results = []
    try:
        for x in inputlist:
            results.append(wikipedia.search(x))
        
        return results

    except Exception as e:
        return e

def find_shortest_path(a1, a2):
    try:
        visited_pages = []
        q = []

        first_page = Page(a1, [])
        visited_pages.append(a1)
        q.append(first_page)

        loop = Loop(True, visited_pages)

        path = get_path(q,a2,True,loop)

        return path

    except Exception as e:
        return e


# I'm using breadth first search algorithm: https://www.geeksforgeeks.org/breadth-first-search-or-bfs-for-a-graph/
# Used multiple sources but this is the main one


def get_path(q, end, threading, loop):                               
    while loop.loop:                                                     
        try:
            current_node = q.pop(0)                   
        except Exception as e:
            pass
        try: #check if there's a match on the first page, if not -> threading     
            #https://www.mediawiki.org/wiki/API:Links                                          
            page = wikipedia.page(title=current_node.title, auto_suggest=False) 
            links = page.links                                          
            if (end in links):                                                 
                loop.loop = False                                      
                current_node.prev.append(current_node.title)                            
                current_node.prev.append(end)                                   
                return current_node.prev                                       
                                                                        
            for i in links:
                if i not in loop.visited:
                    loop.visited.append(i)
                    previous_node = copy.deepcopy(current_node.prev)
                    previous_node.append(current_node.title)
                    a = Page(i, previous_node)
                    q.append(a)
        except Exception as e:                                          
            pass
        
        #copied and modified from below sources
        #https://docs.python.org/3/library/concurrent.futures.html
        #https://superfastpython.com/threadpoolexecutor-in-python/#Step_2_Submit_Tasks_to_the_Thread_Pool
        
        if threading:                                           
            threading = False
            exec = ThreadPoolExecutor(max_workers=20)
            results = {exec.submit(get_path, [i],end, False, loop): i for i in q}  

            return_path = []
            for f in as_completed(results):
                result = f.result()
                if result != None:                              
                    if return_path == []:
                        return_path = result
                    
            print("Completed\n")
            if return_path != []:
                return return_path
            else:
                return Exception



# https://stackoverflow.com/questions/53621682/multi-threaded-xml-rpc-python3-7-1
class SimpleThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass

# registering all the functions to server
def run_server(host=address, port=port):                   
    server_addr = (host, port)
    server = SimpleThreadedXMLRPCServer(server_addr)

    server.register_function(find_articles)
    server.register_function(find_shortest_path)

    print('Listening on {} port {}'.format(host, port))

    server.serve_forever()


#https://docs.python.org/3/library/signal.html


def signal_handler(signal, frame):                              
    sys.exit(0)



signal.signal(signal.SIGINT, signal_handler)


#running server on init
if __name__ == '__main__':                              
    run_server()