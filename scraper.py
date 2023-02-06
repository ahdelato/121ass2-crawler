import re
from urllib.parse import urlparse
from urllib.parse import urljoin
from urllib.parse import urldefrag
from bs4 import BeautifulSoup
import fingerprint

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
        try:
            with open("PreviousPage.txt", "r") as prev:                             # Read PreviousPage file for previous text stored in it
                previous_text = prev.read()

        except FileNotFoundError:
            with open("PreviousPage.txt", "x") as prev:                             # If it doesn't exist, make a new empty one
                previous_text = ""

        current_text = ""                                                           # Extract the text of the page we are currently scraping
        for text in page_soup.find_all("p"):
            current_text += text.get_text()
        
        if len(current_text.split()) < 100:                                         # Checking if amount of words is less than specified number
            print("NOT ENOUGH WORDS. NOT EXTRACTING LINKS")
            return []

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
