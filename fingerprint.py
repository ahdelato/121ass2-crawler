def create_ngrams(webpage_doc, grams):
    # Returns list of hash values derived from hash set of each sum of ASCII values from n-grams of size grams.
    # Assumes that the text from web page is at least size grams
    webpage_words = webpage_doc.split()
    hash_values = []
    for i in range(len(webpage_words)):
        gram_sum = 0
        for num in range(grams):
            gram_sum += sum([ord(char) for char in webpage_words[i + num]])            # Or it could be len(webpage_words[i + num]) if it's not efficient enough

        hash_values.append(gram_sum)

        if i == len(webpage_words) - grams:
            break    

    result_values = []
    for value in hash_values:                                   # Derives hash values where value mod 4 equals 0
        if value % 4 == 0:
            result_values.append(value)

    return result_values

def compute_similarity(hash1, hash2):
    # Computes the similarity between the two hash values by dividing the cardinality of their intersection
    # with the cardinality of their union.
    if len(hash1) > len(hash2):
        intersection = set(hash1).intersection(hash2)

    elif len(hash2) > len(hash1):
        intersection = set(hash2).intersection(hash1)
    
    else:
        intersection = set(hash1).intersection(hash2)

    union_hash = set(hash1 + hash2)

    return len(intersection) / len(union_hash)

if __name__ == "__main__":      # Main branch for local testing
    hash1 = create_ngrams("This is a sentence that is cool to see\nthere are values to make, and in large quantity", 3)
    hash2 = create_ngrams("This no antity", 3)

    print(compute_similarity(hash1, hash2))