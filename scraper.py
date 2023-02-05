import re

from urllib.parse import urlparse
from urllib.parse import urljoin
from urllib.parse import urldefrag
from bs4 import BeautifulSoup

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    

    hyperlink_set = set()      # initialize empty set (to remove duplicates)

    if resp.status == 200:
#print("Status code: {}, success.".format(resp.status))   # PRINT CHECK
        page_soup = BeautifulSoup(resp.raw_response.content, "html.parser")         # Create the BeautifulSoup object
        
        previous_absolute = resp.url                                                # First url should be absolute since it's in frontier



        # IMPPLEMENT HIGH TEXT CONTENT CHECK
        with open("wordFrequencies.txt", "r") as token_file:        # Using text file to store token data
            
            freq = dict()

            for line in token_file:                                 # Transfer file info to dict object
                (key, value) = line.split()
                freq[key] = int(value)

        
        # TOKENIZER
        token_list = []   
        text = page_soup.find_all(["p", "pre"])                     # Find all "paragraphs", definition of high information content
        
        for elem in text:
            elem = elem.get_text()
            elem = re.sub("[^a-zA-Z0-9:-]", " ", elem)              # Replace non-alphanumeric chars
            text_list = re.split("\s", elem)
                
            for word in text_list:
                if word:
                    if re.findall(r"^-\d+", word):                  # Token ex. -2329
                        token_list.append(word)
                    else:
                        word = re.sub("[-]", " ", word)             # Else remove -

                        if re.findall(r"\d+:\w+", word):            # Token ex. 4:00pm              
                            pass
                        else:
                            word = re.sub("[:]", " ", word)         # Else remove :
                        
                        word = re.split("\s", word)
                        for subword in word:
                            token_list.append(subword)
                else:
                    pass

        if len(token_list) < 50 or len(token_list) > 700:            # Webpage max = 700 words, min = 50
            print("Skip page, bad content.")    # PRINT CHECK
            return []

        long_file = open("longestPage.txt", "r")
        number = int(long_file.readline())
        long_file.close()

        if number < len(token_list):
            with open("longestPage.txt", "w") as long_file:
                long_file.write(str(len(token_list)))
                long_file.write("\n")
                long_file.write(resp.raw_response.url)

        
        # COMPUTE FREQ
        for elem in token_list:                                     # Update dictionary values
            elem = elem.lower()

            with open("stopwords.txt", "r") as stop_list:
                stop = stop_list.read()

                if elem not in stop:                                # Compare element with stop word file

                    if elem in freq:
                        freq[elem] += 1
                    else:
                        freq[elem] = 1

        
        # PRINT DICT BACK TO TXT
        freq_list = sorted(freq.items(), key=lambda x:((-x[1]), (x[0])))        # Sort dictionary and overwrite file
        
        with open("wordFrequencies.txt", "w") as token_file:
            for elem in freq_list:
                token_file.write("{} {}\n".format(elem[0], elem[1]))
        
# print("Words frequencies DONE")       # PRINT CHECK




        num_links = len(page_soup.find_all("a"))
        print(f"{num_links} hyperlinks found")

        for link in page_soup.find_all("a"): 
            hyperlink = link.get('href')

            if (not is_absolute(hyperlink)):
                hyperlink = urljoin(previous_absolute, hyperlink)           # Join page url to make absolute
            else:
                previous_absolute = hyperlink

            if (urldefrag(hyperlink)[0] != ""):
                hyperlink = urldefrag(hyperlink)[0]
            
            hyperlink_set.add(hyperlink)

    else:
        print("Status code: {}, ERROR.".format(resp.status))   # PRINT CHECK
    
    hyperlink_list = list(hyperlink_set)            # Assign to list object

    # return hyperlink_list
    return []           # TEMP LOCAL TEST

def is_absolute(url):
    # Determines if a url is absolute by checking if it has a scheme and a domain
    parsed = urlparse(url)
    if parsed.scheme != "" and parsed.hostname != "":
        return True
    else:
        return False 

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        contains_domain = False
        for domain in ["ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu"]: #iterates through every mentioned domain name
            if domain in parsed.hostname:  #check if domain is in url domain
                contains_domain = True             
        
        if not contains_domain:
            return False
            
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
