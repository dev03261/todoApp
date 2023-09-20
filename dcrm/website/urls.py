from django.urls import path
from website.views import (
    delete_todo,
    home,
    login,
    signUp,
    add_todo,
    user_logout,
    change_todo,  # Import the change_todo view
)
from . import views

urlpatterns = [
    path('', home, name='home'),
    path('login/', login, name='login'),
    path('SignUp/', signUp, name='signUp'),
    path('add-todo/', add_todo),
    path('logout/', user_logout, name='logout'),
    path('delete-todo/<int:id>/', delete_todo, name='delete_todo'),
    path('mark-as-done/<int:id>/', change_todo, {'status': 'C'},
         name='mark-as-done'),
    path('mark-as-pending/<int:id>/', change_todo, {'status': 'P'},
         name='mark-as-pending'),
    path('edit-details/<int:id>/<str:status>/', views.edit_details,
         name='edit-details'),
]
