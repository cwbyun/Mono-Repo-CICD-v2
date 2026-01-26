def parse_by_lengths( data_string: str, length_grammar: str ) -> tuple | None:
    try:
        if '-' in length_grammar:
            lengths = [int(l) for l in length_grammar.split('-')]
        else:
            lengths = [int(l) for l in length_grammar]


    except ValueError:
        return None

    expected_length = sum(lengths)

    if len(data_string) != expected_length:
        return None

    chunks = []

    current_pos = 0

    for length in lengths:
        end_pos = current_pos + length
        chunks.append( data_string [current_pos:end_pos])
        current_pos = end_pos

    return tuple(chunks)



