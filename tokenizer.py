import re


def tokenize(soup_text: list) -> list
    token_list = []
    
    for elem in soup_text:                              # Tags p and pre from Beautiful Soup object
        elem = elem.get_text()
        elem = re.sub("[^a-zA-Z0-9:-]", " ", elem)      # Replace non-alphanumeric chars
        text_list = re.split("\s", elem)

        for word in text_list:
            if word:
                if re.findall(r"^-\d+", word):          # Negative numbers are words
                    token_list.append(word)
                else:
                    word = re.sub("[-]", " ", word)     # Else remove -

                    if re.findall(r"\d+:\w+", word):     # Time (4:00pm) are words
                        pass
                    else:
                        word = re.sub("[:]", " ", word)     # Else remove :

                    word = re.split("\s", word)

                    for subword in word:
                        token_list.append(subword)
            else:
                pass

def computeFrequencies(the_list: list, the_dict: dict):     # Update dictionary values
    for elem in the_list:
        elem = elem.lower()

        with open("stopwords.txt", "r") as stop_list:       # Compare with stop file
            stop = stop_list.read()

            if elem not in stop:
                if elem in the_dict:
                    the_dict[elem] += 1
                else:
                    the_dict[elem] = 1

