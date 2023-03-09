http://127.0.0.1:9191/clear/v1

http://127.0.0.1:9191/auth/register/v2

{
    "email": "groupcamel123@gmail.com",
    "password": "password",
    "name_first": "Test",
    "name_last": "Name"
}

http://127.0.0.1:9191/auth/passwordreset/request/v1

{
    "email": "groupcamel123@gmail.com"
}

http://127.0.0.1:9191/auth/passwordreset/reset/v1

{
    "reset_code": "8fcb0631f1afc36cb21f",
    "new_password": "new_password"
}

http://127.0.0.1:9191/auth/login/v2

{
    "email": "groupcamel123@gmail.com",
    "password": "new_password"
}
