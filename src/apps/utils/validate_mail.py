import re


def validate_mail(mail):
    mail = mail.lower()
    pat = "^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$"
    if re.match(pat, mail):
        return True
    return False
