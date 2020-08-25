from datetime import datetime
import requests, json

from webapp import config

#создание доски, получение id
def get_trello_id(name):
    url = "https://api.trello.com/1/boards/"

    query = {
        'key': config.TRELLO_KEY,
        'token': config.TRELLO_TOKEN,
        'name': name
    }

    response = requests.post(
        url,
        params=query
    )

    trello_id = response.json().get('id')
    return trello_id


def delete_trello_board(id):
    url = f"https://api.trello.com/1/boards/{id}"

    query = {
        'key': config.TRELLO_KEY,
        'token': config.TRELLO_TOKEN
    }

    response = requests.delete(
        url,
        params=query
    )
    return response


def create_list(id, name):
    url = "https://api.trello.com/1/lists"

    query = {
        'key': config.TRELLO_KEY,
        'token': config.TRELLO_TOKEN,
        'name': name,
        'idBoard': id
    }

    response = requests.post(
        url,
        params=query
    )

    trello_list_id = response.json().get('id')
    return trello_list_id


def delete_list(id):
    url = f"https://api.trello.com/1/lists/{id}/closed"
    print(url)
    query = {
        'key': config.TRELLO_KEY,
        'token': config.TRELLO_TOKEN
    }

    response = requests.request(
        "PUT",
        url,
        params=query
    )
    print(response.text)


def get_trello_lists(id):
    url = f"https://api.trello.com/1/boards/{id}/lists"

    query = {
        'key': config.TRELLO_KEY,
        'token': config.TRELLO_TOKEN
    }

    response = requests.request(
        "GET",
        url,
        params=query
    )
    data = response.json()
    todo_id = data[0].get('id')
    inprocess_id = data[1].get('id')
    done_id = data[2].get('id')
    return todo_id, inprocess_id, done_id


def add_trello_task(id, name, desc, due):
    url = "https://api.trello.com/1/cards"

    query = {
        'key': config.TRELLO_KEY,
        'token': config.TRELLO_TOKEN,
        'idList': id,
        'name': name,
        'desc': desc,
        'due': due
    }

    response = requests.request(
        "POST",
        url,
        params=query
    )

    return response.json().get('id')


def get_trello_task(id):
    url = f"https://api.trello.com/1/cards/{id}"

    headers = {
        "Accept": "application/json"
    }

    query = {
        'key': config.TRELLO_KEY,
        'token': config.TRELLO_TOKEN
    }

    response = requests.request(
        "GET",
        url,
        headers=headers,
        params=query
    )

    data = response.json()
    name = data.get('name')
    desc = data.get('desc')
    due_date = data.get('due')
    idList = data.get('idList')
    if due_date:
        due = datetime.strptime(due_date, "%Y-%m-%dT%H:%M:%S.%f%z").strftime('%d.%m.%y')
    else:
        due = 'не установлен'
    return name, desc, due, idList



#if __name__ == '__main__':
    #create_list('5f077ba601614b4e13cb85e5', 'test')
    #delete_list('5f07827d5dc4364b54333097')
    #get_trello_lists('5f01dc11514c40360a578e3e')
    #add_trello_task('5f01dc11514c40360a578e40', 'test card 4')
    #add_trello_task('5f01dc11514c40360a578e41', 'test card 5')
    #print(get_trello_task('5f0f6655482be96636dac906'))

