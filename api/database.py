import psycopg2


class TUMReadDatabase:
    def __init__(self, name, host, user, password, port):
        self.connection_error = None
        try:
            self.connection = psycopg2.connect(database=name,
                                               host=host,
                                               user=user,
                                               password=password,
                                               port=port)
            self.cursor = self.connection.cursor()
        except Exception as e:
            self.connection_error = e
            return

    def get_number_of_modules(self):
        query = "SELECT COUNT(*) FROM modules;"
        self.cursor.execute(query)
        return self.cursor.fetchone()[0]

    def get_module_info(self, module_id):
        query = "SELECT * FROM modules WHERE module_id = %s;"
        self.cursor.execute(query, (module_id,))
        return self.cursor.fetchone()

    def get_number_of_degrees(self):
        query = "SELECT COUNT(*) FROM degrees;"
        self.cursor.execute(query)
        return self.cursor.fetchone()[0]

    def get_all_degrees(self):
        query = "SELECT * FROM degrees;"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_degree_info(self, degree_id):
        query = "SELECT * FROM degrees WHERE degree_id = %s;"
        self.cursor.execute(query, (degree_id,))
        return self.cursor.fetchone()

    def get_modules_of_degree(self, degree_id, valid_from=None, valid_to=None, degree_version=None):
        query = """
            SELECT m.*
            FROM modules m
            INNER JOIN mappings mp ON m.module_id = mp.module_id
            WHERE mp.degree_id = %s
        """
        params = [degree_id]

        if valid_from:
            query += " AND mp.valid_from >= %s"
            params.append(valid_from)

        if valid_to:
            query += " AND mp.valid_to <= %s"
            params.append(valid_to)

        if degree_version:
            query += " AND mp.degree_version = %s"
            params.append(degree_version)

        query += ";"

        self.cursor.execute(query, tuple(params))
        return self.cursor.fetchall()
