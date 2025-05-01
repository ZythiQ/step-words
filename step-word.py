import os, json, nltk, argparse
from nltk.corpus import words


def map_signatures(words:list) -> dict[str, list[str]]:
    print('[~] Generating corpus signatures')

    map = {}
    for word in words:
        if word.isalpha():
            if (key := ''.join(sorted(word.lower()))) in map:
                map[key].append(word)
            else:
                map[key] = [word]

    return map


def parse_nltk_corpus(out_file:str) -> dict[str, list[str]]:
    print('[~] Parsing NLTK corpus')

    try:
        nltk.data.find('corpora/words')
    except LookupError:
        nltk.download('words')
    
    cleaned = list(set([w.lower() for w in words.words() if w.isalpha()]))
    signatures = map_signatures(cleaned)

    with open(out_file, 'w') as file:
        json.dump(signatures, file, indent=1)

    return signatures


def parse_signatures(in_file:str) -> dict[str, list[str]]:
    with open(in_file, 'r') as file:
        return json.load(file)
    

def get_signatures(processed_out:str = 'resources/processed_words.json') -> dict[str, list[str]]:
    if os.path.exists(processed_out):
        return parse_signatures(processed_out)
    else:
        return parse_nltk_corpus(processed_out)


def find_step_words(word:str, letter:str) -> list[str]:
    signatures = get_signatures()
    print(f'[~] Finding step-words for "{word}" + "{letter}"')

    cleaned = ''.join(sorted((word + letter).lower()))
    return signatures.get(cleaned, [])


def find_unstepped(count:int, descending:bool = True) -> list[tuple[int, list[tuple[str, list[str]]]]]:
    signatures = get_signatures()
    analyzed = {}
    result = []

    print(f'[~] Finding the {"top" if descending else "worst"} {count} step combos')

    # Score by # of step-words:
    scored = sorted(
        [(sig, len(words)) for sig, words in signatures.items()],
        key=lambda x: x[1],
        reverse=True
    )
    
    # Find all combinations:
    for sig, score in scored:
        for i in range(len(sig)):
            rm_letter = sig[i]
            new_sig = sig[:i] + sig[i+1:]
            
            if new_sig in signatures:
                words = signatures[new_sig]
                
                if score not in analyzed:
                    analyzed[score] = {}
                
                if rm_letter not in analyzed[score]:
                    analyzed[score][rm_letter] = set()
                
                analyzed[score][rm_letter].update(words)

    # Sort and limit:
    scored_analysis = sorted(analyzed.keys(), reverse=descending)
    
    for score in scored_analysis[:min(count, len(scored_analysis))]:
        combos = [(letter, sorted(list(words))) for letter, words in analyzed[score].items()]
        result.append((score, combos))
    
    return result


def find_unstepped_letters(word:str, count:int, descending:bool = True):
    letters = 'abcdefghijklmnopqrstuvwxyz'
    signatures = get_signatures()
    analyzed = {}
    result = []

    print(f"[~] Finding the {'top' if descending else 'worst'} {count} letters to combine with '{word}'")

    for letter in letters:
        sorted_combo = ''.join(sorted(word.lower() + letter))
        words = signatures.get(sorted_combo, [])
        score = len(words)

        if score == 0:
            continue

        if score not in analyzed:
            analyzed[score] = []

        analyzed[score].append((letter, words))

    for score, letter_words_pairs in analyzed.items():
        result.append((score, letter_words_pairs))
        
    result.sort(key=lambda x: x[0], reverse=descending)
    return result[:count]


def main():
    parser = argparse.ArgumentParser(description='*** Step Word Finder and Analyzer ***')
    subparsers = parser.add_subparsers(dest='command', help='Commands:')
    
    # Step command:
    step_parser = subparsers.add_parser('step', help='Find step words.')
    step_parser.add_argument('--word', '-w', required=True, help='Word to step.')
    step_parser.add_argument('--letter', '-l', required=True, help='Letter to step with.')
    
    # Unstep command:
    unstep_parser = subparsers.add_parser('unstep', help='Find top/worst unstepped word + letter combos.')
    unstep_parser.add_argument('--word', '-w', help='Specific word to unstep.')
    unstep_parser.add_argument('--count', '-c', type=int, default=5, help='N results to show.')
    unstep_parser.add_argument('--reverse', action='store_true', default=False, help='Sort in reverse (ascending) order.')
    
    # Work:
    args = parser.parse_args()
    max_words = 25
    
    if args.command == 'step':
        step_words = find_step_words(args.word, args.letter)
        
        if len(step_words):
            for word in step_words:
                print(f'[+] {word}')
            print()
        else:
            print('[-] None found...')
            
    elif args.command == 'unstep':
        if args.word is not None:
            unstepped = find_unstepped_letters(args.word, args.count, not args.reverse)

        else:
            unstepped = find_unstepped(args.count, not args.reverse)

        if unstepped:
            for score, combos in unstepped:
                print(f'[+] Score: {score}')
                
                for letter, words in combos:
                    if len(words) > max_words:
                        display_words = words[:max_words]
                        print(f"    └─ Letter '{letter}' → {', '.join(display_words)} (+{len(words) - max_words} more)")
                    else:
                        print(f"    └─ Letter '{letter}' → {', '.join(words)}")
                print()
        else:
            print('[-] None found...')
            
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
