import psycopg2


class TUMWriteDatabase:

    def __init__(self, name, host, user, password, port):
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

        # Create the 'degrees' table if it doesn't exist
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS degrees (
                degree_id SERIAL PRIMARY KEY,
                full_text_en VARCHAR(255),
                short_text_en VARCHAR(255),
                full_text_de VARCHAR(255),
                short_text_de VARCHAR(255)
            );
        """)
        # Create the 'modules' table if it doesn't exist
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS modules (
                module_id SERIAL PRIMARY KEY,
                name_en VARCHAR(255),
                name_de VARCHAR(255)
            );
        """)
        # Create the 'mappings' table if it doesn't exist
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS mappings (
                degree_id INTEGER,
                module_id INTEGER,
                degree_version VARCHAR(255),
                ects FLOAT,
                weighting_factor FLOAT,
                valid_from VARCHAR(255),
                valid_to VARCHAR(255),
                PRIMARY KEY (degree_id, module_id),
                FOREIGN KEY (degree_id) REFERENCES degrees(degree_id) ON DELETE CASCADE,
                FOREIGN KEY (module_id) REFERENCES modules(module_id) ON DELETE CASCADE
            );
        """)
        # Commit the changes
        self.connection.commit()

    def insert_degree(self, degree_id, full_text_en, short_text_en, full_text_de, short_text_de):
        query = """
            INSERT INTO degrees (degree_id, full_text_en, short_text_en, full_text_de, short_text_de)
            VALUES (%s, %s, %s, %s, %s);
        """
        self.cursor.execute(query, (degree_id, full_text_en, short_text_en, full_text_de, short_text_de))
        self.connection.commit()

    def insert_module(self, module_id, name_en, name_de):
        query = """
            INSERT INTO modules (module_id, name_en, name_de)
            VALUES (%s, %s, %s);
        """
        self.cursor.execute(query, (module_id, name_en, name_de))
        self.connection.commit()

    def insert_mapping(self, degree_id, module_id, degree_version, ects, weighting_factor, valid_from, valid_to):
        query = """
            INSERT INTO mappings (degree_id, module_id, degree_version, ects, weighting_factor, valid_from, valid_to)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        self.cursor.execute(query, (degree_id, module_id, degree_version, ects, weighting_factor, valid_from, valid_to))
        self.connection.commit()
