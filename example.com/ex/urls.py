from staticgen import site, urls


def home():
    j = site.get_jinja()
    t = j.get_template('home.html')
    return t.render()


def article(slug):
    j = site.get_jinja()
    t = j.get_template(f'{slug}.html')
    return t.render()


urls = [
    urls.url('/', home, name='home'),
    urls.url('/{slug}', article, name='article', generators={
            'slug': lambda: ('intro', 'guide'),
        },
    ),
]
