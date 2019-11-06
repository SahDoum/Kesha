import config

class User:
    def __init__(self, markup, synonyms=(), id=None):
        self.markup = markup
        self.synonyms = synonyms
        self.id = id


alextours_users = []
for markup, synonyms in config.alextours_users.items():
    alextours_users.append(User(markup, synonyms))


def generate_alextours_names():
    names = set()
    for user in alextours_users:
        names.update(user.synonyms)

    return names


def get_alextours_markup():
    names = [user.markup for user in alextours_users]
    return ', '.join(names)
