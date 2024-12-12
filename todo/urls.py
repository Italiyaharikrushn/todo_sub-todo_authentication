from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
    path('todo_list/', views.todo_list, name='todo_list'),
    path('AddTask/',views.addTask,name='add'),
    path('delete/<int:id>/', views.delete_task, name='delete_task'),
    path('update/<int:id>/', views.editTask, name='edit_task'),
    path('subtasks/<int:todo_id>/', views.subtodo_list_and_add, name='subtodo_list'),
    path('subtasks/delete/<int:todo_id>/', views.deleteSubtask, name='deleteSubtask'),
    path('subtasks/edit/<int:todo_id>/', views.editSubTask, name='sub_edit'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)