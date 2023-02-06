import re
from urllib.parse import urlparse
from urllib.parse import urljoin
from urllib.parse import urldefrag
from bs4 import BeautifulSoup
import fingerprint
from tokenizer import *
from collections import defaultdict


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
    
    hyperlink_list = []        # initialize empty list
    hyperlink_set = set()      # initialize empty set (to remove duplicates)
    if resp.status == 200:
        # print("Status code: {}, success.".format(resp.status))   # PRINT CHECK
        page_soup = BeautifulSoup(resp.raw_response.content, "html.parser")         # Create the BeautifulSoup object
        
        previous_absolute = resp.url                                                # First url should be absolute since it's in frontier
        

        # Update uniquePages.txt count
        try:
            with open("uniquePages.txt", "r") as unique_file:
                count = int(unique_file.readline())
        except FileNotFoundError:
            with open("uniquePages.txt", "x") as unique_file:
                count = 0

        count += 1

        with open("uniquePages.txt", "w") as unique_file:
                unique_file.write(str(count))

        try:
            with open("SubdomainCount.txt", "r") as sub_file:
                subdomains = defaultdict(int)
                for line in sub_file:
                    (key, value) = line.split()
                    subdomains[key] = int(value)
        except FileNotFoundError:
            with open("SubdomainCount.txt", "x") as sub_file:
                subdomains = defaultdict(int)
        
        url_host = urlparse(resp.url).hostname
        if re.match(r"^.*\.ics\.uci\.edu$", url_host):
            if not re.match(r"^w{3}\.ics\.uci\.edu$", url_host):
                subdomains[url_host] += 1
            

        sub_list = sorted(subdomains.items(), key=lambda x:(x[0]))           
        with open("SubdomainCount.txt", "w") as sub_file:
            for elem in sub_list:
                sub_file.write("{} {}\n".format(elem[0], elem[1]))


        # CREATE DICT
        try:
            with open("wordFrequencies.txt", "r") as token_file:
                freq = dict()

                for line in token_file:
                    (key, value) = line.split()
                    freq[key] = int(value)
        except FileNotFoundError:
            with open("wordFrequencies.txt", "x") as token_file:
                freq = dict()

        # CALL TOKENIZE, initialize current_text
        text = page_soup.find_all(["p", "pre"])
        token_list = tokenize(text)
        current_text = ""
        for chunk in text:
            current_text += chunk.get_text()        
        
        # Compare word limits
        if len(token_list) < 100 or len(token_list) > 700:
            print("NOT ENOUGH WORDS. NOT EXTRACTING LINKS")
            return []
        
        # Open longest page
        try:
            long_file = open("longestPage.txt", "r")
            number = int(long_file.readline())
        except FileNotFoundError:
            long_file = open("longestPage.txt", "x")
            number = 0

        long_file.close()
        
        # Write to longestPage.txt
        if number < len(token_list):
            with open("longestPage.txt", "w") as long_file:
                long_file.write(str(len(token_list)))
                long_file.write("\n")
                long_file.write(resp.raw_response.url)

        # Call compute freq
        computeFrequencies(token_list, freq)

        # Print dict back to file
        freq_list = sorted(freq.items(), key=lambda x:((-x[1]), (x[0])))             # Sort dict and overwrite file

        with open("wordFrequencies.txt", "w") as token_file:
            for elem in freq_list:
                token_file.write("{} {}\n".format(elem[0], elem[1]))

        ##
        #current_text = ""                                                           # Extract the text of the page we are currently scraping
        #for text in page_soup.find_all("p"):
         #   current_text += text.get_text()
        
        #if len(current_text.split()) < 100:                                         # Checking if amount of words is less than specified number
         #   print("NOT ENOUGH WORDS. NOT EXTRACTING LINKS")
         #   return []

        ##
    



        try:
            with open("PreviousPage.txt", "r") as prev:                             # Read PreviousPage file for previous text stored in it
                previous_text = prev.read()

        except FileNotFoundError:
            with open("PreviousPage.txt", "x") as prev:                             # If it doesn't exist, make a new empty one
                previous_text = ""

        if len(previous_text) == 0:                                                 # Write current text to PreviousPage if PreviousPage empty. There will be no similarity    
            similarity = 0                                                              # and the links will be extracted
            with open("PreviousPage.txt", "w") as new:
                new.write(current_text)
        else:
            hash_prev = fingerprint.create_ngrams(previous_text, 3)
            hash_current = fingerprint.create_ngrams(current_text, 3)
            similarity = fingerprint.compute_similarity(hash_prev, hash_current)
            if similarity < .8:                                                     # Replace PreviousPage text with current text if they aren't near duplicates
                with open("PreviousPage.txt", "w") as new:
                    new.write(current_text)
        
        print(f"SIMILARITY: {similarity}")

        if similarity < .8:                                                         # Only extract links if page isn't near duplicate. Else, ignore by not extracting its links.
            for link in page_soup.find_all("a"): 
                hyperlink = link.get('href')
                if (not is_absolute(hyperlink)):
                    hyperlink = urljoin(previous_absolute, hyperlink)
                else:
                    previous_absolute = hyperlink

                if (urldefrag(hyperlink)[0] != ""):
                    hyperlink = urldefrag(hyperlink)[0]
                
                hyperlink_set.add(hyperlink)
        else:
            print("IS A NEAR DUPLICATE. NOT EXTRACTING LINKS")

    else:
        print("Status code: {}, error, {}.".format(resp.status,url))   # PRINT CHECK
    
    hyperlink_list = list(hyperlink_set)

    return hyperlink_list

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

        # check if url is within domain
        if (isinstance(parsed.hostname, str) and parsed.hostname != "" and 
            not re.match(r".*\.(ics\.uci\.edu|cs\.uci\.edu|informatics\.uci\.edu|stat\.uci\.edu)", parsed.hostname)):
            return False

        if r"/pdf/" in url:
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
