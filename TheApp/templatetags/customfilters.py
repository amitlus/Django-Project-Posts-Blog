from django import template
register = template.Library()

@register.filter(name='addclass')
def addclass(value,arg):
        return value.as_widget(attrs={'class':arg})
#יצרתי פילטר שיאפשר לי להכיל קלאסים שיצרתי ולהשתמש בהם על טמפךייט טאגס
#Did not use it.. just made it for trying
#I just added css to the label before the widjet itself
