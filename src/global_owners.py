from src.data_store import data_store

def get_num_global_owners():
    store = data_store.get()
    return store['num_global_owners']

def reset_num_global_owners():
    store = data_store.get()
    store['num_global_owners'] = 0
    data_store.set(store)

def increment_num_global_owners():
    store = data_store.get()
    store['num_global_owners'] += 1
    data_store.set(store)

def decrement_num_global_owners():
    store = data_store.get()
    store['num_global_owners'] -= 1
    data_store.set(store)