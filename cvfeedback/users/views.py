from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect

# Registro
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # inicia sesión automáticamente
            return redirect('analizar_cv')  # redirige a página principal
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})

# Inicio de sesión
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('analizar_cv')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

# Cierre de sesión
def logout_view(request):
    logout(request)
    return redirect('login')
