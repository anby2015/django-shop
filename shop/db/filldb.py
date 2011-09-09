from goods.models import Product, Category
from users.models import Profile

flist = open('db/filmlist', 'r')
fdesc = open('db/filmdesc', 'r')

films, created = Category.objects.get_or_create(slug='films', defaults={
    'name': 'Films',
    'inheritance': '',
})

qqq, created = Profile.objects.get_or_create(username='qqq')
if created:
    qqq.set_password('qqq')
i = 0
for l in flist:
    i+=1
    print i
    rating, name, url = l.split('||||')
    desc, imgurl, genre = fdesc.readline().strip().split('||||')
    
    cat, created = Category.objects.get_or_create(slug=genre.lower(), defaults={
        'name': genre,
        'inheritance': films.as_parent()
    })
    
    p = Product.objects.create(
        name=name, description=desc, cost=rating, owner=qqq, category=cat
    )
