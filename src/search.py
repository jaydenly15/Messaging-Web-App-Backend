import pytest
from src.error import InputError
from src.data_store import data_store
from src.token import generate_token, get_user_from_token
from typing import Dict, Union, List

def search_v1(token: str, query_str: str) -> Dict[str, List[str]]:
    """Given a query string, return a collection of messages in all of the channels/DMs
        that the user has joined that contain the query.

    Args:
        token (str): The token of the user making the search request
        query_str (str): The string that is being searched

    Raises:
        InputError: Length of the query string is less than 1 or over 1000 characters

    Returns:
    Dict:   {
            'messages': List of messages
            }
    """
    store = data_store.get()
    user_id = get_user_from_token(token)['u_id']

    if len(query_str) < 1 or len(query_str) > 1000:
        raise InputError(description="Length of query_str must be between 1 and 1000 characters.")

    messages_list = []

    for channel in store['channels']:
        for message in channel['messages']:
            # if query_str is a substring of the message
            if query_str in message['message']:
                # check that user is in the channel
                if user_id in channel['users']:
                    messages_list.append(message)

    for dm in store['dms']:
        for message in dm['messages']:
            # if query_str is a substring of the message
            if query_str in message['message']:
                # check that user is in the dm
                if user_id in dm['members']:
                    messages_list.append(message)

    return {
        'messages': messages_list
    }