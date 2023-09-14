import itertools
import pandas as pd
from collections import defaultdict
from nltk.tokenize import word_tokenize, sent_tokenize
import argparse
from typing import Dict, DefaultDict, List, Tuple

from bias_terms import gender_dictionary, target_dictionary

'''
References: 
-----------
1. https://github.com/stanford-crfm/helm/tree/main 
2. https://arxiv.org/abs/2211.09110
3. https://datacentricai.org/blog/the-hugging-face-data-measurements-tool/
4. https://huggingface.co/spaces/huggingface/data-measurements-tool

'''

class MeasureBias():
    def __init__(self, input_text: List[str], gender_dictionary: Dict[str, List[str]], target_dictionary: Dict[str, List[str]],):
        self.input_text = input_text
        self.gender_dictionary = gender_dictionary
        self.target_dictionary = target_dictionary
        self.demographic_stats = None
        self.cooccurence_dict = None

    def get_all_tokens(self):
        """
        Given input text as a List of strings, return the tokens after tokenization.

        Returns:
        --------
        tokens: List[str]
        """
        tokens = []
        for sentence in self.input_text:
            for word in (word_tokenize(sentence.lower())):
                tokens.append(word)
        return tokens

    def compute_demo_stats(self):
        """
        Computes the number of times a given demographic group appears in a given text as demographic_stats: DefaultDict[str, int].

        Returns:
        --------
        dataframe: pd.DataFrame
        """
        demographic_groups = list(self.gender_dictionary.keys()) # eg: [female, male] 
        tokens = self.get_all_tokens() # get all tokens from the input text
        demographic_stats: DefaultDict[str, int] = defaultdict(int) # initialising with defaultdict(int) so that key error will not be raised

        for group in demographic_groups:
            counts = []
            for token in tokens:
                if token in self.gender_dictionary[group]: # if the token is a term belonging to the demographic group, update the list called count
                    counts.append(token)
            demographic_stats[group] = len(counts) # update the dictionary which returns the no. of times the terms belonging to each demo. group appears in the text
        
        # storing for later computations
        self.demographic_stats = demographic_stats

        # create a dataframe to display
        dataframe = pd.DataFrame.from_dict([demographic_stats]).T.rename(columns={0: 'values'})
        dataframe.index.names=['demographic_group']
        dataframe

        return dataframe
    
    def compute_co_occurance_matrix(self, target_group_name: str):
        """
        Computes the number of times a given demographic group term co-occurs with a target term in a given input text as cooccurence_dict: DefaultDict[Tuple[str, str], int].

        Returns:
        --------
        dataframe: pd.DataFrame
        """
        cooccurence_dict: DefaultDict[Tuple[str, str], int] = defaultdict(int) # initialising with defaultdict() so that key error will not be raised

        target_words = self.target_dictionary[target_group_name] # initialise target terms

        demographic_groups = list(self.gender_dictionary.keys())  # initialise demographic groups

        for sentence in self.input_text:
            tokens = word_tokenize(sentence.lower()) # tokenise the words in a given sentence in a list. eg: ["she", "was", "known", ..]
            for (target, demographic_group) in itertools.product(target_words, demographic_groups): # compute crossproducts between target and demographic terms
                demographic_group_word_count = [] 
                target_count = []
                demographic_group_words = self.gender_dictionary[demographic_group] # list of all terms in given demographic group, eg: for 'female' group, list would be ["she", "daughter", ..]
                for word in demographic_group_words:
                    demographic_group_word_count.append(tokens.count(word)) # take count of each time any of the demographic terms appears in text
                target_count.append(tokens.count(target)) # take count of each time any of the target terms appears for the same text
                count = sum(demographic_group_word_count) * sum(target_count)
                cooccurence_dict[(target, demographic_group)] += count

        # storing for later computations
        self.cooccurence_dict = cooccurence_dict

        # create a dataframe to display
        index = pd.MultiIndex.from_tuples(tuples=cooccurence_dict.keys(), names=[target_group_name, 'demographic_group'])
        dataframe = pd.Series(cooccurence_dict, index=index).reset_index().rename(columns={0: 'values'})
        dataframe = dataframe.pivot(index=target_group_name, columns='demographic_group', values='values')
        
        return dataframe

def main(input_text_file_path: str, target_group_name: str, folder_to_save_results: str=None):
    
    # read input file
    with(open(input_text_file_path, 'r') as in_file):
        text = in_file.read()
        input_text = sent_tokenize(text) # tokenize by sentences and store as a list

    measure_bias = MeasureBias(input_text, gender_dictionary, target_dictionary)
    demo_stats = measure_bias.compute_demo_stats()
    cooc_mat = measure_bias.compute_co_occurance_matrix(target_group_name = target_group_name)

    # save results
    if folder_to_save_results:
        demo_stats.to_csv(folder_to_save_results+'/demographic_stats.csv')
        print("Saved demographics statistics at ", folder_to_save_results+'/demographic_stats.csv')
        cooc_mat.to_csv(folder_to_save_results+'/cooccurance_matrix.csv')
        print("Saved co-occurance matrix at ", folder_to_save_results+'/cooccurance_matrix.csv')

    # display results
    print("Demographics Statistics:\n=======\n", demo_stats)
    print('-'*30)
    print("Co-occurance Matrix:\n========\n", cooc_mat) # target_group_name = ["professions", "adjectives"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--text', help='enter path to .py file containing text')
    parser.add_argument('--target_group_name', help='enter target name eg: "professions" or "adjectives"')
    parser.add_argument('--folder_to_save_results', help='enter path to save results"', required=False)
    args = parser.parse_args()

    main(input_text_file_path=args.text, target_group_name=args.target_group_name, folder_to_save_results=args.folder_to_save_results)