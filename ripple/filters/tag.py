from functools import partial

def build_tag_filter(args):
    remaining_args = []
    tags = set()
    for arg in args:
        if arg.startswith('+'):
            tags.add(arg[1:])
        else:
            remaining_args.append(arg)

    filter = partial(get_entries_with_tags, tags)
    return filter, remaining_args

def get_entries_with_tags(tags, entries):
    """
    Returns all entries which match all of the given tags.

    @param iterable tags
    @return generator[Entry]
    """
    for entry in entries:
        skip = False
        for wanted_tag in tags:
            if wanted_tag.lower() not in entry.get_tags():
                skip = True
                break
        if not skip:
            yield entry
