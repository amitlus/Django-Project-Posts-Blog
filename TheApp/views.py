from django.shortcuts import render, get_object_or_404, redirect
from TheApp.forms import UserForm, UserProfileInfoForm
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.views.generic import (View, TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView)
from. import models
from TheApp.models import Post, Comment, UserProfileInfo
from django.contrib.auth.mixins import LoginRequiredMixin
from TheApp.forms import PostForm, CommentForm
from django.urls import reverse_lazy
from django.utils import timezone
import random
from django.db.models import Q


# Create your views here.
def index(request):
    return render(request, 'TheApp/index.html')


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('TheApp:index'))


def register(request):

    registered = False

    if request.method == "POST":
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileInfoForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():

            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'profile_pic' in request.FILES:
                profile.profile_pic = request.FILES['profile_pic']

            profile.save()

            registered = True
        else:
            print(user_form.errors, profile_form.errors)

    else:
        user_form = UserForm()
        profile_form = UserProfileInfoForm()

    return render(request, 'TheApp/registration.html', {'user_form':user_form, 'profile_form':profile_form, 'registered':registered})

def user_login(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('TheApp:index'))

            else:
                return HttpResponse('ACCOUNT NOT ACTIVE')
        else:
            print("Someone tried to login and failed")
            print("Username: {} and password {}".format(username, password))
            return HttpResponse('invalid login details supplied')
    else:
        return render(request, 'TheApp/login.html',)



class PostListView(LoginRequiredMixin, ListView):
    model = Post
    context_object_name = 'thelist'
    template_name = 'TheApp/explore.html'


    def get_queryset(self):
        return Post.objects.order_by('?')
# בעצם מחזיר לי את הערכים כLIST שמסודר לפי תאריך היצירה מהחדש לישן.. בלי המינוס זה היה הפו


class PostDetailView(LoginRequiredMixin, DetailView):

    model = Post

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        obj = self.get_object()
        obj.post_views = obj.post_views + 1
        obj.save()
        return context



class CreatePostView(LoginRequiredMixin, CreateView):
    form_class = PostForm  #במקום לציין fields
    model = Post

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.author= self.request.user #מכניס לו את המופע של User
        obj.save()
        return HttpResponseRedirect(obj.get_absolute_url())

#הפונקציה נקראת כש valid form ב-post.
#היא צריכה להחזיר HttpResponse
#בעצם הפונקציה הזו מגדירה את הערך של הauthor ובגלל שהורדתי אותו מה-Form אז הוא לא נראה לעין כשיוצרים פוסט חדש.
# אבל אוטומטית הערך שנכנס לauthor הוא היוזר המחובר.
#כשאני אסתכל ברשימת הפוסטים יהיה רשום מי יצר אותו



class PostUpdateView(LoginRequiredMixin, UpdateView):
    form_class = PostForm
    model = Post

    def get_queryset(self):
        author = self.request.user
        return self.model.objects.filter(author=author) #הפונקציה הזו בעצם מאפשרת רק למי שהוא בעל הפוסט להיכנס לערוך אותו. גם אם למישהו תהיה הכתובת זה לא יעזור ל



class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('TheApp:post_list')

    def delete(self, request, *args, **kwargs):#עשיתי אובררייד לקלאס בייסד ויו של הדיליט ככה שרק מי שיצר את הפוסט יוכל למחוק אותו
        if (Post.author == request.user.username):
            return super().delete(request, *args, **kwargs)
        else:
            return HttpResponse('You are not the owner of this Post! You can not delete it!')


############################################################################################



############################################################################################

@login_required
def add_comment_to_post(request,pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user.username
            comment.save()
            return redirect('TheApp:post_detail', pk=post.pk)
    else:
        form = CommentForm()
        return render(request, 'TheApp/comment_form.html', {'form':form})




@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if (request.user.username == comment.author or request.user == comment.post.author): #רק אם המשתמש המחובר זה המשתמש שיצר את התגובה
        post_pk = comment.post.pk #מוסיפים את השורה הזו כי אחרי שנמחק את התגובה כבר לא נדע מה הPK שלה היה..
        comment.delete()
        return redirect('TheApp:post_detail', pk=post_pk)
    else:
         return HttpResponse('You are not the author of this comment. Access denied')

@login_required
def personalposts(request, username):
    if username == request.user.username:#כדי לוודא שמה שהכנסנו בכתובת במקום <username> שווה לשם המשתמש המחובר ושרק הוא יוכל לעבור לדף הרתוי
        items = Post.objects.filter(author__username=username)
        return render(request, 'TheApp/personalposts.html', {'items':items})
    else:
        return HttpResponse('You are not {}. Access denied'.format(username))


def top(request):
    top_posts = Post.objects.order_by('-post_views')# מסדר לפי צפיות מהגדול לקטן, בלי המינוס זה יהיה הפוך
    return render(request, 'TheApp/top.html', {'top_posts':top_posts})


def search(request):
    query_list = Post.objects.all()
    query = request.GET.get("q")
    if query:
        query_list = query_list.filter(
        Q(title__icontains=query)|
        Q(text__icontains=query)
        ).distinct()
    else:
        query_list = []
    return render(request, 'TheApp/results.html' , {'query_list':query_list})
