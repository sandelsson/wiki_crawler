
import signal
from socketserver import ThreadingMixIn
import sys
from xmlrpc.server import SimpleXMLRPCServer
from  concurrent.futures import ThreadPoolExecutor, as_completed
import requests



WIKI = 'https://en.wikipedia.org/w/api.php'


class Loop:
    def __init__(self, path, found):
        self.path = path
        self.found = found


#https://www.mediawiki.org/wiki/API:Search#Python 
def find_searches(inputlist):
    A1 = inputlist[0]
    A2 = inputlist[1]
    search1 = []
    search2 = []
    search1 = find_searches_parse(A1, search1)
    search2 = find_searches_parse(A2, search2)

    return search1, search2


def find_searches_parse(SEARCHPAGE1, results):
    PARAMS = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": SEARCHPAGE1
    }

    R = requests.get(url=WIKI, params=PARAMS)
    DATA = R.json()


    if DATA['query']['search'] == []:
        print("no results")
        return results
    

    if len(DATA['query']['search']) < 8:

        for x in DATA['query']['search']:
            results.append(x["title"])

    else:
        c = 0
        while ( c < 8):
            results.append(DATA['query']['search'][c]["title"])
            c += 1
    

    
            

    #print(results)
    return results




def start_workers(a1, a2):
    path = {
    }

    path[a1] = [a1]


    queue = []
    queue.append(a1)

    print(queue)
    
    loop = Loop([], False)

    try:
        while loop.found == False:
            #https://docs.python.org/3/library/concurrent.futures.html
            with ThreadPoolExecutor(max_workers=50) as executor:

                if not loop.found:
                    results = {executor.submit(linkfinder, i, loop): i for i in queue}
            
                for future in as_completed(results):
                    page = results[future]
                    links = future.result()

                    if links != []:
                        for l in links:
                            if (l == a2):
                                loop.found = True
                                loop.path = path[page] + [l]
                                print(f"Path found: {loop.path}\n")
                                return loop.path
                                
                            if l not in path and l != page:
                                path[l] = path[page] + [l]
                                queue.append(l)
    except Exception as e:
        print(f"{e}")  

#https://www.mediawiki.org/wiki/API:Links#Example_1:_Fetch_all_the_links_in_a_page
def linkfinder(page, loop):

    if loop.found:
        return

    links = []

    PARAMS = {
    "action": "query",
    "format": "json",
    "titles": page,
    "prop": "links"
}

    r = requests.get(url=WIKI, params=PARAMS)
    DATA = r.json()

    PAGES = DATA["query"]["pages"]
    try:
        for k, v in PAGES.items():
            for l in v["links"]:
                #https://en.wikipedia.org/w/api.php?action=query&prop=revisions&titles=Iitti&prop=links&pllimit=max
                if(l["ns"] == 0):
                    links.append(l["title"])

            #https://stackoverflow.com/questions/14882571/how-to-get-all-urls-in-a-wikipedia-page
            #https://www.mediawiki.org/wiki/API:Links
            while 'continue' in DATA:
                PARAMS = {
                "action": "query",
                "format": "json",
                "titles": page,
                "prop": "links",
                "pllimit": "max",
                "plcontinue": DATA["continue"]["plcontinue"]
            }
            
                R = requests.get(url=WIKI, params=PARAMS)
                DATA = R.json()
                PAGES = DATA["query"]["pages"]
            
                for k, v in PAGES.items():
                    for l in v["links"]:
                        if(l["ns"] == 0):
                            links.append(l["title"])
    
    except:
        pass
    




    return links


    




# https://stackoverflow.com/questions/53621682/multi-threaded-xml-rpc-python3-7-1
# creates threads for clients
class SimpleThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
   pass

# registering all the functions to server
def run_server(host="127.0.0.1", port=8000):                   
    server_addr = (host, port)
    server = SimpleThreadedXMLRPCServer(server_addr)

    server.register_function(find_searches_parse)
    server.register_function(find_searches)
    server.register_function(start_workers)
    server.register_function(linkfinder)

    print(f'\nServer started...')
    print(f'Listening on {host} port {port}.\n')

    server.serve_forever()


#https://docs.python.org/3/library/signal.html


def signal_handler(signal, frame):                              
    sys.exit(0)



signal.signal(signal.SIGINT, signal_handler)


#running server on init
if __name__ == '__main__':
    run_server()

