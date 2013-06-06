import django.db.models as m

class Author(m.Model):
    name = m.TextField()

    def __str__(self):
        return self.name

class Book(m.Model):
    isbn = m.TextField(primary_key=True)
    title = m.TextField()
    author = m.ForeignKey(Author)

    def __str__(self):
        return '{} by {}'.format(self.title, self.author)


class Person(m.Model):
    name = m.TextField()
    age = m.IntegerField()

class Tag(m.Model):
    name = m.TextField()

class Image(m.Model):
    title = m.TextField()
    url = m.URLField()
    owner = m.ForeignKey(Person)
    tags = m.ManyToManyField(Tag)
    timestamp = m.DateTimeField(auto_now_add=True)

class Comment(m.Model):
    image = m.ForeignKey(Image)
    person = m.ForeignKey(Person)
    text = m.TextField()
    timestamp = m.DateTimeField(auto_now_add=True)
