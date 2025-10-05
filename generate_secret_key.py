import secrets
import string

def generate_secret_key(length=50):
    """Generate a random secret key for Django"""
    alphabet = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
    return ''.join(secrets.choice(alphabet) for _ in range(length))

if __name__ == '__main__':
    print("Generated Django secret key:")
    print(generate_secret_key())
