from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse

# Create your models here.
class UserProfileInfo(models.Model):
    user = models.OneToOneField(User, models.PROTECT)
# mode ls.PROTECT is an on_delete value which protect the source model and if he is not existed or having a problem he raises an Error to alert us

    # additional
    portfolio_site = models.URLField(blank=True)
    profile_pic = models.ImageField(upload_to='TheApp/profile_pics',blank=True)

    def __str__(self):
        return self.user.username


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    #כדי שרק משתמשים רשומים יוכלו ליצור פוסט
    title = models.CharField(max_length=200)
    text = models.TextField()
    create_date = models.DateTimeField(default=timezone.now)
    post_views = models.IntegerField(default=0)



    def get_absolute_url(self):
        return reverse("TheApp:post_detail", kwargs={'pk':self.pk})
        #פונקציה שאחרי שניצור פוסט או תגובה תעביר אותנו לדף מסוים

    def __str__(self):
            return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete = models.CASCADE)
    author = models.CharField(max_length=200)
    text = models.TextField()
    create_date = models.DateTimeField(default=timezone.now)
    approved_comment = models.BooleanField(default=False)# הסיבה שלא מחקתי את השדה הזה היא כי אני לא רוצה להרוס את כל הקוד כי הבסיס נתונים כבר נוצר

    def approve(self):
        self.approved_comment = True
        self.save()

    def get_absolute_url(self):
        return reverse("TheApp:post_list")
        #פונקציה שאחרי שניצור פוסט או תגובה תעביר אותנו לדף מסוים

    def __str__(self):
        return self.text
