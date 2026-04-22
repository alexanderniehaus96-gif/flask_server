import uuid

from flask import Flask, render_template, request, jsonify, abort

# initialize Flask server
app = Flask(__name__)

# create fixed IDs for sample lists
todo_list_1_id = '1318d3d1-d979-47e1-a225-dab1751dbe75'
todo_list_2_id = '3062dc25-6b80-4315-bb1d-a7c86b014c65'
todo_list_3_id = '44b02e00-03bc-451d-8d01-0c67ea866fee'

# define internal data structures with sample data
todo_lists = [
    {'id': todo_list_1_id, 'name': 'Einkaufsliste'},
    {'id': todo_list_2_id, 'name': 'Arbeit'},
    {'id': todo_list_3_id, 'name': 'Privat'},
]
todo_entries = [
    {'id': str(uuid.uuid4()), 'name': 'Milch', 'description': '2 Liter', 'list': todo_list_1_id},
    {'id': str(uuid.uuid4()), 'name': 'Arbeitsblaetter ausdrucken', 'description': 'fuer Klasse 1', 'list': todo_list_2_id},
    {'id': str(uuid.uuid4()), 'name': 'Kinokarten kaufen', 'description': 'fuer Samstag', 'list': todo_list_3_id},
]


# add some headers to allow cross origin access to the API on this server
@app.after_request
def apply_cors_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,DELETE,PATCH'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


# define route for main page
@app.route('/')
def index():
    return render_template('index.html')


# define endpoint for all todo lists
@app.route('/todo-list', methods=['GET', 'POST'])
def handle_todo_lists():
    if request.method == 'GET':
        return jsonify(todo_lists), 200
    elif request.method == 'POST':
        # parse JSON from POST data (also if content type is missing)
        new_list = request.get_json(force=True)
        if not new_list or 'name' not in new_list:
            abort(400)
        list_item = {'id': str(uuid.uuid4()), 'name': new_list['name']}
        todo_lists.append(list_item)
        return jsonify(list_item), 201


# define endpoint for one specific todo list
@app.route('/todo-list/<list_id>', methods=['GET', 'POST', 'DELETE'])
def handle_todo_list(list_id):
    # find todo list by given list id
    list_item = None
    for l in todo_lists:
        if l['id'] == list_id:
            list_item = l
            break
    # if the given list id is invalid, return 404
    if not list_item:
        abort(404)

    if request.method == 'GET':
        # return all entries for the given list
        return jsonify([entry for entry in todo_entries if entry['list'] == list_id]), 200
    elif request.method == 'POST':
        # add a new entry to the existing list
        new_entry = request.get_json(force=True)
        if not new_entry or 'name' not in new_entry or 'description' not in new_entry:
            abort(400)
        entry_item = {
            'id': str(uuid.uuid4()),
            'name': new_entry['name'],
            'description': new_entry['description'],
            'list': list_id
        }
        todo_entries.append(entry_item)
        return jsonify(entry_item), 201
    elif request.method == 'DELETE':
        # delete list and all associated entries
        todo_lists.remove(list_item)
        for entry in todo_entries[:]:
            if entry['list'] == list_id:
                todo_entries.remove(entry)
        return '', 204


# define endpoint for a single todo entry
@app.route('/todo-list/entry/<entry_id>', methods=['PATCH', 'DELETE'])
def handle_todo_entry(entry_id):
    # find todo entry by given entry id
    entry_item = None
    for entry in todo_entries:
        if entry['id'] == entry_id:
            entry_item = entry
            break
    # if the given entry id is invalid, return 404
    if not entry_item:
        abort(404)

    if request.method == 'PATCH':
        # update an existing todo entry
        update_data = request.get_json(force=True)
        if not update_data or 'name' not in update_data or 'description' not in update_data:
            abort(400)
        entry_item['name'] = update_data['name']
        entry_item['description'] = update_data['description']
        return jsonify(entry_item), 200
    elif request.method == 'DELETE':
        # delete a single todo entry
        todo_entries.remove(entry_item)
        return '', 204


if __name__ == '__main__':
    # start Flask server
    app.run(host='0.0.0.0', port=5000)