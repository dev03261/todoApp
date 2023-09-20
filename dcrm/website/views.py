from django.shortcuts import render, redirect
from .forms import EditTaskForm
from django.shortcuts import HttpResponse
from django.contrib.auth import authenticate, login as loginUser, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from website.forms import TODOForm
from website.models import TODO
from django.contrib import messages


def home(request):
    if request.user.is_authenticated:
        # print("User is authenticated")
        user = request.user
        form = TODOForm()
        todos = TODO.objects.filter(user=user)
        return render(request, 'index.html', context={'form': form, 'todos':
                                                      todos})
    else:
        return redirect('login')
        # return HttpResponseRedirect('/login/')


def login(request):
    context = {}

    if request.method == 'GET':
        form = AuthenticationForm()
        context["form"] = form
        return render(request, 'login.html', context=context)
    else:
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                loginUser(request, user)
                messages.success(request, 'You have logged in successfully')
                return redirect('home')
        else:
            context = {
                "form": form
            }
            return render(request, 'login.html', context=context)


def signUp(request):
    if request.method == 'GET':
        print('get found..........')
        form = UserCreationForm()
        context = {
            "form": form
        }
        return render(request, 'signUp.html', context=context)
    else:
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user is not None:
                return redirect('login')
        else:
            context = {
                "form": form
            }
            return render(request, 'signUp.html', context=context)


def add_todo(request):
    print("Entering add_todo view")

    if request.user.is_authenticated:
        user = request.user

        if request.method == 'POST':
            form = TODOForm(request.POST)
            if form.is_valid():
                todo = form.save(commit=False)
                todo.user = user
                todo.save()
                return redirect("home")
        else:
            form = TODOForm()

        return render(request, 'index.html', context={'form': form})
    else:
        return redirect("login")


def user_logout(request):
    logout(request)
    return redirect("home")

    # If not confirmed or GET request, render the confirmation page


def delete_todo(request, id):
    todo = TODO.objects.get(pk=id)
    if todo.user == request.user:
        TODO.objects.get(pk=id).delete()
        return redirect("home")
    return HttpResponse('You can not delete this task.')


def change_todo(request, id, status):
    todo = TODO.objects.get(pk=id)
    print(f"Before update - Status: {todo.status}")
    todo.status = status
    todo.save()
    print(f"After update - Status: {todo.status}")
    return redirect("home")


def edit_details(request, id, status):
    todo = TODO.objects.get(pk=id)
    print(todo.user, '******************', request.user)
    if todo.user == request.user:
        form = EditTaskForm(request.POST, instance=todo)
        print("in edit")
        if form.is_valid():
            form.save()
            print("in valid")
            return redirect("home")
        else:
            print("in invalid")
            form = EditTaskForm(instance=todo)
        return render(request, 'edit_details.html', {'form': form, 'todo':
                                                     todo})
    return HttpResponse('You do not have access to this task.')
