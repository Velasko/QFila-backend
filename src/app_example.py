from flask import Flask
from flask_restx import Api, Resource, fields

app = Flask(__name__)
api = Api(app, version='0.1', title='Cardápio',
    description='A simple menu API',
)

ns = api.namespace('cardapio', description='Menu operations')

item = api.model('Item', {
    'id': fields.Integer(readonly=True, description='The item unique identifier'),
    'name': fields.String(required=True, description='Name of the item'),
    'price': fields.Fixed(required=True, description='Price of the item', decimals=2)
})


class ItemDAO(object):
    def __init__(self):
        self.counter = 0
        self.cardapio = []

    def get(self, id):
        for item in self.cardapio:
            if item['id'] == id:
                return item
        api.abort(404, "Item {} doesn't exist".format(id))

    def create(self, data):
        item = data
        item['id'] = self.counter = self.counter + 1
        self.cardapio.append(item)
        return item

    def update(self, id, data):
        item = self.get(id)
        item.update(data)
        return item

    def delete(self, id):
        item = self.get(id)
        self.cardapio.remove(item)


DAO = ItemDAO()


@ns.route('/')
class TodoList(Resource):
    '''Shows a list of all cardapio, and lets you POST to add new tasks'''
    @ns.doc('list_cardapio')
    @ns.marshal_list_with(item)
    def get(self):
        '''List all tasks'''
        return DAO.cardapio

    @ns.doc('create_todo')
    @ns.expect(item)
    @ns.marshal_with(item, code=201)
    def post(self):
        '''Create a new task'''
        return DAO.create(api.payload), 201


@ns.route('/<int:id>')
@ns.response(404, 'Todo not found')
@ns.param('id', 'The task identifier')
class Todo(Resource):
    '''Show a single todo item and lets you delete them'''
    @ns.doc('get_todo')
    @ns.marshal_with(item)
    def get(self, id):
        '''Fetch a given resource'''
        return DAO.get(id)

    @ns.doc('delete_todo')
    @ns.response(204, 'Todo deleted')
    def delete(self, id):
        '''Delete a task given its identifier'''
        DAO.delete(id)
        return '', 204

    @ns.expect(item)
    @ns.marshal_with(item)
    def put(self, id):
        '''Update a task given its identifier'''
        return DAO.update(id, api.payload)


if __name__ == '__main__':
    app.run(debug=True)