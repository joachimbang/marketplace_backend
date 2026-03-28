from accounts.models import User
from rest_framework_simplejwt.tokens import RefreshToken

def generate_tokens(user):
    refresh = RefreshToken.for_user(user)

    # --- LA CORRECTION EST ICI ---
    # On récupère l'objet access_token à partir du refresh
    access = refresh.access_token

    # On injecte manuellement les claims (données) dans l'ACCESS token
    access["role"] = user.role
    access["email"] = user.email
    # ------------------------------

    return {
        "refresh": str(refresh),
        "access": str(access) # On renvoie le token qui contient maintenant le rôle
    }

def login_user(email, password):
    print(f"email recu: {email}")  # Debug print
    print(f"password recu: {password}")  # Debug print

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        print("Aucun utilisateur trouvé avec cet email")  # Debug print
        return None
    if not user.check_password(password):
        print("Mot de passe incorrect")  # Debug print
        return None

    tokens = generate_tokens(user)

    return {
        "user": user,
        "tokens": tokens
    }