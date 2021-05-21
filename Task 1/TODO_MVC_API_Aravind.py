from flask import Flask,request
from flask_restplus import Api, Resource, fields
from werkzeug.contrib.fixers import ProxyFix
import datetime
import sqlite3
from functools import wraps
app = Flask(__name__)

authorizations = {
    'apikey':{
        'type':'apiKey',
        'in' : 'header',
        'name': 'X-API-KEY'
    }
}
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version='1.0', title='TodoMVC API',
    description='A simple TodoMVC API',authorizations=authorizations)
def token_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        token = None
        if 'X-API-KEY' in request.headers:
            token = request.headers['X-API-KEY']
        if not token:
            return {'message':'Token missing'},401
        if token != "aravind1411":
            return {'message': 'Incorrect token,Try providing a correct one'},401
        return f(*args,**kwargs)
    return decorated

        
ns = api.namespace('todos', description='TODO operations')

todo = api.model('Todo', {
    'id': fields.Integer(readonly=True, description='The task unique identifier'),
    'task': fields.String(required=True, description='The task details'),
    'due_by':fields.String(required=True, description='Due date'),
    'status':fields.String(required=True, description='Status of the task')
})


class TodoDAO(object):
    def __init__(self):
        self.counter = 0
        self.todos = []
    def get(self,id):
        try:
            with sqlite3.connect('test.db') as conn:
                c = conn.cursor()
                result = c.execute('SELECT * FROM todo where id={}'.format(id)).fetchall()
                return {'id':result[0][0], 'task' :result[0][1], 'due_by':result[0][2] , 'status':result[0][3] }     
        except:
            api.abort(404, "Todo {} doesn't exist".format(id))

        

    def create(self, data):
        with sqlite3.connect('test.db') as conn:
            c = conn.cursor()
            print("Data is",data)
            c.execute('INSERT INTO TODO(task,due_by,status_of_task) VALUES (?,?,?)',(data['task'],data['due_by'],data['status']))
            conn.commit()
        conn.close()
        return obj.get(),201

    def update(self, id, data):
        try:
            with sqlite3.connect('test.db') as conn:
                c = conn.cursor()
                #print(id)
                #print(data)
                c.execute("UPDATE todo SET task=?,due_by=?,status_of_task=? where id=?",(data['task'],data['due_by'],data['status'],id))
            conn.close()
            return  self.get(id)
        except:
            return {"Failure":"Error updating the database"}, 404

    def delete(self, id):
        try:
            with sqlite3.connect('test.db') as conn:
                c = conn.cursor()
                c.execute("DELETE FROM todo where id={}".format(id))
            conn.close()
            return  {"Todo deleted successfully"}
        except:
            return {"Failure":"Error"}, 404
    def getfinishedtasks(self):
        try:
            with sqlite3.connect("test.db") as conn:
                conn.row_factory=sqlite3.Row
                c = conn.cursor()
                query = c.execute("SELECT * FROM todo where status_of_task='Finished'").fetchall()
                result = []
                for i in range(0, len(query)):
                    result.append({'id':query[i][0], 
                    'task' :query[i][1],
                    'due_by': query[i][2] , 
                    'status':query[i][3] } )
                
                
            conn.close()
            return result
        except:
            api.abort(500, "Something went wrong")
    def getoverduetasks(self):
        CurrentDate = datetime.datetime.now()
        print(CurrentDate)
        result=obj.get()
        print(result)
        overdue=[]
        for i in range(len(result)):
            if(CurrentDate>(datetime.datetime.strptime(result[i]['due_by'], "%Y-%m-%d")) and (result[i]['status']!="Finished")):
                overdue.append({'id':result[i]['id'], 
                'task' :result[i]['task'],
                'due_by': result[i]['due_by'] , 
                'status':result[i]['status'] } )
        return overdue
    def updatestatus(self,id,new_status):
        print(id)
        print(new_status)
        try:
            with sqlite3.connect('test.db') as conn:
                c = conn.cursor()
                c.execute("UPDATE TODO SET STATUS_OF_TASK=? WHERE ID=?",(new_status,id))
                conn.commit()
            conn.close()
            return self.get(id)
        except:
            return {"Failure":"Todo not found"},404

        

    


        
DAO = TodoDAO()
#DAO.create({'task': 'Build an API'})
#DAO.create({'task': '?????'})
#DAO.create({'task': 'profit!'})


@ns.route('/')
class TodoList(Resource):
    '''Shows a list of all todos, and lets you POST to add new tasks'''
    @ns.doc('list_todos')
    @ns.marshal_list_with(todo)
    def get(self):
        '''List all tasks'''
        try:
            with sqlite3.connect("test.db") as conn:
                conn.row_factory=sqlite3.Row
                c = conn.cursor()
                query = c.execute('SELECT * FROM todo').fetchall()
                result = []
                for i in range(0, len(query)):
                    result.append({'id':query[i][0], 
                    'task' :query[i][1],
                    'due_by': query[i][2] , 
                    'status':query[i][3] } )
                
                
            conn.close()
            return result
        except:
            api.abort(500, "Something went wrong")
        
    @ns.doc('create_todo',security='apikey')
    @token_required
    
    @ns.expect(todo)
    @ns.marshal_with(todo, code=201)
    def post(self):
        '''Create a new task'''
        return DAO.create(api.payload), 201
    


@ns.route('/due/<due_by>')
@ns.response(404, 'Todo not found')
@ns.param('due_by', 'Due date')
class TodoDueDate(Resource):
    @ns.doc('due')
    @ns.response(201, 'Displayed all the tasks that are due on the given date')
    def get(self,due_by):
        date=due_by
        #print(date)
        result = obj.get()
        #print(result)
        due=[]
        for i in range(len(result)):
            if(result[i]['due_by']==date):
                due.append({'id':result[i]['id'],'task':result[i]['task'],'due_by':result[i]['due_by'],'status':result[i]['status']})        
        
        return due





@ns.route('/<int:id>')
@ns.response(404, 'Todo not found')
@ns.param('id', 'The task identifier')
class Todo(Resource):
    '''Show a single todo item and lets you delete them'''
    @ns.doc('get_todo')
    @ns.marshal_with(todo)
    def get(self, id):
        '''Fetch a given resource'''
        return DAO.get(id)
    
    @ns.doc('delete_todo',security='apikey')
    @token_required
    @ns.response(204, 'Todo deleted')
    def delete(self, id):
        '''Delete a task given its identifier'''
        DAO.delete(id)
        return '', 204
    
        
    
    @ns.doc('update_todo',security='apikey')
    @token_required
    @ns.expect(todo)
    @ns.marshal_with(todo)
    def put(self, id):
        '''Update a task given its identifier'''
        return DAO.update(id, api.payload)

@ns.route('/finished')
@ns.response(404, 'There are no finished tasks yet')
class TodoFinished(Resource):
    @ns.doc('finished')
    @ns.response(201, 'Finshed tasks diplayed')
    def get(self):
        '''Diplay all finished tasks'''
        return DAO.getfinishedtasks(), 201

@ns.route('/overdue')
@ns.response(404, 'There are no overdues')
class TodoOverdue(Resource):
    @ns.doc('overdue')
    @ns.response(201, 'Overdue tasks diplayed')
    def get(self):
        '''Diplay all overdue tasks'''
        return DAO.getoverduetasks(), 201
        
@ns.route('/updatestatus/<int:id>/<new_status>')
@ns.response(404, 'Todo not found')
@ns.param('id', 'The task identifier')
@ns.param('new_status', 'Set status: Finished/In progress/Not started')
class TodoUpdateStatus(Resource):
    @ns.response(200, 'Status updated')
    @ns.doc(security='apikey')
    @token_required
    def put(self,id,new_status):
        '''Update status of a task given its identifier'''
        return DAO.updatestatus(id,new_status)

obj=TodoList()
if __name__ == '__main__':
    app.run(debug=True)