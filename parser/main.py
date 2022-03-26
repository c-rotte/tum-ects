import os
from parser import Parser
from database import Database


if __name__ == '__main__':

    mongodb_connection = os.getenv('MONGODB', 'mongodb://localhost:27017')

    print('Connecting to MongoDB... ')
    database = Database(mongodb_connection)

    if database.connection_error:
        print(f'Could not connect to <{mongodb_connection}>.')
        print(database.connection_error)
        exit(-1)

    parser = Parser(database=database)
    exception = parser.run()
    if exception:
        print(exception)
        exit(-1)

