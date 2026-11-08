
from datetime import datetime

def get_current_time():
    """Return the current date and time."""
    
    return datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")


def roll_dice():
    """Simulate rolling a six-sided die and return the result."""
    
    import random
    return random.randint(1, 6)

def generate_password(length=12):
    """Generate a random password of specified length."""
    
    import string
    import secrets

    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    
    return password