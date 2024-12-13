from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .models import User, Todo, SubTodo
from django.urls import reverse

def register(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        password = make_password(request.POST['password'])
        gender = request.POST['gender']
        age = request.POST['age']
        profession = request.POST['profession']

        if User.objects.filter(email=email).exists():
            messages.error(request, f"The email '{email}' is already registered. Please use a different email.")
            return render(request, 'base/register.html', {'name': name, 'phone': phone, 'gender': gender, 'age': age, 'profession': profession})

        User.objects.create(
            name=name, email=email, phone=phone, password=password,
            gender=gender, age=age, profession=profession
        )
        return redirect('login')

    return render(request, 'base/register.html')

# This function handles the user login process
def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        try:
            user = User.objects.get(email=email)
            if check_password(password, user.password):
                request.session['user_id'] = user.id
                request.session['user_name'] = user.name
                return redirect('todo_list')
            else:
                messages.error(request, "Incorrect password.", extra_tags="password_error")
        except User.DoesNotExist:
            messages.error(request, "Email is not registered.", extra_tags="email_error")

    return render(request, 'base/login.html')

# This function handles user logout
def logout(request):
    request.session.flush()
    return redirect('login')

# This function displays the to-do list for the logged-in user
def todo_list(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session['user_id']
    todos = Todo.objects.filter(user_id=user_id)

    try:
        user = User.objects.get(id=user_id)
        name = user.name
    except User.DoesNotExist:
        return redirect('login')

    for todo in todos:
        todo.subtodo_count = SubTodo.objects.filter(todo_id=todo.id).count()

    if any(todo.user_id != user_id for todo in todos):
        messages.warning(request, "You are trying to access to-do items from another user.")

    return render(request, 'base/todo_list.html', {'todos': todos, 'name': name})

# This function handles adding a new task for the logged-in user
def addTask(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session['user_id']

    if request.method == 'POST':
        title = request.POST.get('title')
        desc = request.POST.get('desc')
        status = request.POST.get('status')
        completion_date = request.POST.get('completion_date') if status == 'Complete' else None
        dropdown_submit = request.POST.get('dropdown_submit', False)
        if dropdown_submit:
            return render(request, 'base/add_todo.html', {
                'task': {'title': title, 'desc': desc, 'status': status, 'completion_date': completion_date}
            })
        if Todo.objects.filter(title=title, user_id=user_id).exists():
            return redirect('addtask')

        Todo.objects.create(
            title=title, desc=desc, status=status,
            completion_date=completion_date, user_id=user_id
        )
        return redirect('todo_list')

    return render(request, 'base/add_todo.html')

# This function handles the deletion of a specific task
def delete_task(request, id):
    # item = Todo.objects.get(id=id)
    try:
        item = Todo.objects.get(id=id)
    except Todo.DoesNotExist:
        messages.error(request, f"Todo with ID {id} does not exist.")
        return redirect('todo_list')

    if item.user_id != request.session.get('user_id'):
        messages.warning(request, "You cannot delete a task that doesn't belong to you.")
        return redirect('todo_list')
    
    if request.method == "POST":
        if request.POST.get("confirm") == "Yes":
            item.delete()  
            return redirect('todo_list')
        return redirect('todo_list')

    return render(request, 'base/delete_todo.html', {'item': item})

# This function handles editing an existing task
def editTask(request, id):
    # task = Todo.objects.get(id=id)
    try:
        task = Todo.objects.get(id=id)
    except Todo.DoesNotExist:
        messages.error(request, f"Todo with ID {id} does not exist.")
        return redirect('todo_list')

    if task.user_id != request.session.get('user_id'):
        messages.warning(request, "You cannot edit a task that doesn't belong to you.")
        # return redirect(reverse('edit_todo', args=[task.id]))
        return redirect('todo_list')

    if request.method == 'POST':
        title = request.POST.get('title')
        desc = request.POST.get('desc')
        status = request.POST.get('status')
        completion_date = request.POST.get('completion_date')

        dropdown_submit = request.POST.get('dropdown_submit', False)

        task.title = title
        task.desc = desc
        task.status = status

        if status == 'Complete':
            task.completion_date = completion_date or task.completion_date
        else:
            task.completion_date = None

        if not dropdown_submit:
            task.save()
            return redirect(reverse('todo_list'))

    return render(request, 'base/edit_todo.html', {'task': task})

# This function handles adding a new sub-task for the to-do
def subtodo_list_and_add(request, todo_id):
    try:
        todo = Todo.objects.get(id=todo_id)
    except Todo.DoesNotExist:
        messages.error(request, f"Todo with ID {todo_id} does not exist.")
        return redirect('todo_list')
    
    subtodos = SubTodo.objects.filter(todo_id=todo_id)
    form = request.GET.get('add', False)

    if todo.user_id != request.session.get('user_id'):
        messages.warning(request, "You cannot add sub-tasks to a todo that doesn't belong to you.")
        return redirect('todo_list')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        desc = request.POST.get('desc')
        status = request.POST.get('status')
        completion_date = request.POST.get('completion_date') if status == 'Complete' else None
        dropdown_submit = request.POST.get('dropdown_submit', False)
        
        if dropdown_submit:
            return render(request, 'base/subtodo_list.html', {
                'task': {'title': title, 'desc': desc, 'status': status, 'completion_date': completion_date},
                'subtodos': subtodos,
                'todo_id': todo_id,
                'title': todo.title,
                'form': form
            })

        SubTodo.objects.create(
            title=title,
            desc=desc,
            status=status,
            completion_date=completion_date,
            todo_id=todo_id,
        )
        return redirect('subtodo_list', todo_id=todo_id)

    return render(request, 'base/subtodo_list.html', {'subtodos': subtodos, 'todo_id': todo_id, 'title': todo.title, 'form': form,})

# This function handles editing an existing sub-task
def editSubTask(request, todo_id):
    tasks = SubTodo.objects.get(id=todo_id)

    if tasks.todo.user_id != request.session.get('user_id'):
        messages.warning(request, "You cannot edit a sub-task that doesn't belong to you.")
        return redirect('todo_list')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        desc = request.POST.get('desc')
        status = request.POST.get('status')
        completion_date = request.POST.get('completion_date')

        dropdown_submit = request.POST.get('dropdown_submit', False)

        tasks.title = title
        tasks.desc = desc
        tasks.status = status

        if status == 'Complete':
            tasks.completion_date = completion_date or tasks.completion_date
        else:
            tasks.completion_date = None

        if not dropdown_submit:
            tasks.save()
            todo_id = tasks.todo.id
            return redirect(reverse('subtodo_list', args=[todo_id]))

    return render(request, 'base/edit_subtodo.html', {'tasks': tasks})

# This function handles the deletion of a specific task
def deleteSubtask(request, todo_id):
    try:
        # Retrieve the subtask using the todo_id
        item = SubTodo.objects.get(id=todo_id)
    except SubTodo.DoesNotExist:
        # Handle case where subtask does not exist
        messages.error(request, f"Subtask with ID {todo_id} does not exist.")
        return redirect(reverse('subtodo_list', args=[todo_id]))

    if request.method == "POST":
        # Handle confirmation for deletion
        if request.POST.get("confirm") == "Yes":
            todo_id = item.todo.id  # Get the parent Todo ID
            item.delete()  # Delete the subtask
            messages.success(request, "Subtask deleted successfully.")
            return redirect(reverse('subtodo_list', args=[todo_id]))

        return redirect(reverse('subtodo_list', args=[item.todo.id]))

    # Render the confirmation page if the request method is GET
    return render(request, 'base/delete_todo.html', {'item': item})