# import pytest
# from src.auth import auth_register_v1
# from src.user import user_profile_v1, user_profile_setname_v1, user_profile_setemail_v1, user_profile_sethandle_v1
# from src.other import clear_v1
# from src.token import generate_token
# from src.error import InputError

# def get_token_from_u_id(u_id):
#     token = generate_token(u_id)
#     return token

# def test_invalid_u_id():
#     # test if invalid u_id raises InputError 
#     clear_v1()
#     answers = auth_register_v1('example@mail.com','password','123455555555','human')
#     invalid_id = answers['auth_user_id'] + 10000000000
    
#     with pytest.raises(InputError):
#         user_profile_v1(answers['token'], invalid_id)
#     clear_v1()
    
# '''def test_invalid_token():
#     There is no invalid token error type in interface, So we assume that all token passing
#     in user_all_v1 and user_profile_sethandle_v1 are correct and will not raise an error
# '''
# def test_correct_user_profile():
#     # user_profile matchs
#     clear_v1()
#     answers = auth_register_v1('example@mail.com', 'password', '1234555555', 'human')
#     output = user_profile_v1(answers['token'], answers['auth_user_id'])
#     assert len(output['user']) == 5
#     assert output['user']['email'] == 'example@mail.com'
#     assert output['user']['name_first'] == '1234555555'
#     assert output['user']['name_last'] == 'human'
#     assert output['user']['handle_str'] == '1234555555human'
#     clear_v1()
    
# def test_invalid_first_name():
#     clear_v1()
#     answers = auth_register_v1('example@mail.com', 'password', '1234', 'human')
#     token = get_token_from_u_id(answers['auth_user_id'])
#     with pytest.raises(InputError):
#         user_profile_setname_v1(token, 'querty1234567890aasfibuisbaiuuvhguiasdguashoashfiashuashfoshagoihsghauhoshgoahoishgosahiofha', 'name')
#     clear_v1()
    
# def correct_set_name():
#     clear_v1()
#     answers = auth_register_v1('example@mail.com', 'password', '1234', 'human')
#     token = get_token_from_u_id(answers['auth_user_id'])
#     out = user_profile_v1(token, answers['auth_user_id'])
#     assert out['user']['name_first'] == '1234'
#     assert out['user']['name_last'] == 'human'
#     clear_v1()

# def test_invalid_email():
#     clear_v1()
#     answers = auth_register_v1('example@mail.com', 'password', '1234', 'human')
#     token = get_token_from_u_id(answers['auth_user_id'])
#     with pytest.raises(InputError):
#         user_profile_setemail_v1(token, 'fairytellmail.com')

# def test_email_in_use():
#     clear_v1()
#     answers = auth_register_v1('first@mail.com', 'password', '1234', 'human')
#     answers2 = auth_register_v1('second@mail.com', 'password', '12345', 'insect')
#     token = get_token_from_u_id(answers['auth_user_id'])
#     with pytest.raises(InputError):
#         user_profile_setemail_v1(token, 'second@gmail.com')
#     clear_v1()
    
# def test_correct_setemail():
#     clear_v1()
#     answers = auth_register_v1('example@mail.com', 'password', '1234', 'human')
#     token = get_token_from_u_id(answers['auth_user_id'])
#     out = user_profile_v1(token, answers['auth_user_id'])
#     assert out['user']['email'] == 'example@mail.com'
#     clear_v1() 

# def test_handle_in_use():
#     clear_v1()
#     answers = auth_register_v1('first@mail.com', 'password', '1234', 'aaa')
#     answers2 = auth_register_v1('second@mail.com', 'password', '1000', 'bbb')
#     token = get_token_from_u_id(answers['auth_user_id'])
#     with pytest.raises(InputError):
#         user_profile_sethandle_v1(token, '1000bbb')
#     clear_v1()

# def test_invalid_handle():
#     clear_v1()
#     answers = auth_register_v1('example@mail.com', 'password', '1234', 'abc')
#     token = get_token_from_u_id(answers['auth_user_id'])
#     with pytest.raises(InputError):
#         user_profile_sethandle_v1(token, '')
#     with pytest.raises(InputError):
#         user_profile_sethandle_v1(token, 'abcdefghijklmnopqrstuvwxyz')
#     clear_v1()

# def test_assumptions_handle():
#     clear_v1()
#     answers = auth_register_v1('example@mail.com', 'password', 'one', 'aye')
#     token = get_token_from_u_id(answers['auth_user_id'])
#     with pytest.raises(InputError):
#         user_profile_sethandle_v1(token, 'blah blah')