from django import forms
from .models import Usuarios

class UsuarioCreationForm(forms.ModelForm):
    contrasena = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    confirmar_contrasena = forms.CharField(widget=forms.PasswordInput, label="Confirmar Contraseña")

    class Meta:
        model = Usuarios
        fields = ['nombre_usuario', 'nombre_completo', 'correo', 'rol', 'contrasena']
        widgets = {
            'nombre_usuario': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'rol': forms.Select(attrs={'class': 'form-select'}),
            'contrasena': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        contrasena = cleaned_data.get("contrasena")
        confirmar_contrasena = cleaned_data.get("confirmar_contrasena")

        if contrasena and confirmar_contrasena and contrasena != confirmar_contrasena:
            self.add_error('confirmar_contrasena', "Las contraseñas no coinciden")

        if contrasena:
            import re
            if len(contrasena) < 8:
                self.add_error('contrasena', "La contraseña debe tener al menos 8 caracteres.")
            if not re.search(r'\d', contrasena):
                self.add_error('contrasena', "La contraseña debe contener al menos un número.")
            if not re.search(r'[A-Z]', contrasena):
                self.add_error('contrasena', "La contraseña debe contener al menos una letra mayúscula.")
            if not re.search(r'[a-z]', contrasena):
                self.add_error('contrasena', "La contraseña debe contener al menos una letra minúscula.")
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', contrasena):
                self.add_error('contrasena', "La contraseña debe contener al menos un símbolo.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["contrasena"])
        if commit:
            user.save()
        return user
