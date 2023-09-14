# Measuring Bias

Current implementation has two measures:
1. **Demographic statistics**: Computes the number of times a given demographic group appears in a given text (eg: `{'female': 7, 'male': 6}`).
2. **Co-occurance matrix**: Computes the number of times a given demographic group term (eg: `"she"`) co-occurs with a target term (eg: `"caring"`) in a given input text (eg: `{'('female', 'caring')': 2, ('male', 'caring'): 0, ..}`).

## To run the program:

`python3 bias_measure.py --text example_text.txt --target_group_name professions`

- Values for `--target_group_name` can be currently chosen from `professions` or `adjectives`. 
- `--text` should be set to path to the .txt file containing the text to be evaluated. (eg: `example_text.txt`)

## To save the results:

`python3 bias_measure.py --text example_text.txt --target_group_name professions --folder_to_save_results "."`

- `folder_to_save_results` must contain the path to the **folder** to save the results to as a .csv file. This is an optional argument. (eg: `./src`)

## To update the Target Terms:

1. Update `bias_terms.py` with:
    1. `List` containing target terms (eg: `adjectives = ["reactive", "sweet", .. ]`)
    2. Update `target_dictionary` with the new `List` containing target terms (eg: `target_dictionary = {"adjectives": adjectives, .. }`)

## To update the Demographic Terms:

1. Update `bias_terms.py` with:
    1. `List` containing demographic terms (eg: `female_terms = ["her", "she", "wife", .. ]`)
    2. Update/Create `gender_dictionary` with the new `List` containing demographic terms (eg: `gender_dictionary = {"female": female_terms, "male": male_terms}`)

## Requirements:
`itertools`
`pandas`
`collections`
`nltk`
