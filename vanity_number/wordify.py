import os
from typing import List
from collections import deque # For Queue
import heapq # For Priority Queue - Min Heap

from helper import *
from t9_graph_node import *

def find_words_from_numbers(number: str, max_number_results_to_output):
    """
    Args: Phone Number and max_number_results_to_output
    Returns: Wordified Numbers

    Example Input (number: "7246874", max_number_results_to_output=1)
    Example Output wordified String "PAINTER"

    Example Input (number: "2665233", max_number_results_to_output=10)
    Example Output wordified String ["COOLBED", "BOOKBEE", "COOKADD", "BOOLADD", ......]

    Returns [] or "" if No word can be formed, based on max_number_results_to_output > 1 or = 1
    """
    number_of_digits = len(number)

    digit_to_chars_list_map = get_digit_to_chars_list_mapping()

    # Performing Breadth-first Search
    queue = deque([])
    queue.append(T9_Graph_Node(number, 0, 0, 0, 0))

    # Create an empty Max Heap
    words_from_numbers_pq = []
    # https://docs.python.org/2/library/heapq.html

    while(queue):
        curr_wordified_node = queue.popleft()
        curr_wordified = curr_wordified_node.wordified_so_far
        curr_index = curr_wordified_node.index_so_far

        # If the graph search reached the end of the number, then validate and push to results heap
        if curr_index == number_of_digits:

            (is_valid_wordified_phone_number, max_number_of_continous_chars_in_word, max_length_word_substring) = \
                evaluate_wordified_number(curr_wordified)

            if not is_valid_wordified_phone_number:
                continue

            curr_wordified_node.max_number_of_continous_chars_in_word = max_number_of_continous_chars_in_word
            curr_wordified_node.max_length_word_substring = max_length_word_substring

            # Push the current element into priority queue
            heapq.heappush(words_from_numbers_pq, curr_wordified_node)
            # Have only total N elements in Priority Queue / Heap, and Remove other elements
            while len(words_from_numbers_pq) > max_number_results_to_output:
                heapq.heappop(words_from_numbers_pq)
            continue

        curr_digit = number[curr_index]
        curr_number_of_chars_in_word = curr_wordified_node.number_of_chars_in_word

        # For finding Partial Wordification (1-800-724-BEER)
        # Calculate character prefix length ending at the index so far
        char_prefix = find_char_prefix(curr_wordified, curr_index - 1)
        len_char_prefix = len(char_prefix)

        for char in (digit_to_chars_list_map[curr_digit] + [curr_digit]):
             # If the current letter is a DIGIT either there should be only digits running till this point,
             # or a valid word formed till this point,
             # only then we replace the next index of a running word to a digit

            if ((char.isdigit() and (len_char_prefix == 0 or is_valid_word(char_prefix))) or
                (char.isalpha() and (curr_index != number_of_digits - 1 and is_valid_word_or_prefix(char_prefix+char))) or
                (char.isalpha() and (curr_index == number_of_digits - 1 and is_valid_word(char_prefix+char)))):
                # Or if the current letter is a character, then the prefix so far should be present in the Trie,
                # only then we search one level down

                # Only if the prefix exists in the Trie are we going deeper in the Search
                # If there does NOT exist ANY word with the prefix so far
                # the search will NOT go to the next level.

                next_wordified_number = replace_string_with_char_at_index(curr_wordified, curr_index, char)
                # print(next_wordified_number)
                next_number_chars_in_word = curr_number_of_chars_in_word + (1 if char.isalpha() else 0)
                (is_valid_wordified_phone_number, max_number_of_continous_chars_in_word, max_length_word_substring) = \
                    evaluate_wordified_number(next_wordified_number)

                queue.append(T9_Graph_Node(next_wordified_number, curr_index + 1, \
                    next_number_chars_in_word, max_number_of_continous_chars_in_word, max_length_word_substring))

    # Returning the maximum T9_Graph_Node having most number of contigous letters, defined as the comparator function
    if len(words_from_numbers_pq) > 0:
        words_from_numbers_result = []

        nlargest_ = heapq.nlargest(max_number_results_to_output, words_from_numbers_pq)

        for wordified in nlargest_:
            words_from_numbers_result.append(wordified.wordified_so_far)

        return words_from_numbers_result[:max_number_results_to_output]
    else:
        return []