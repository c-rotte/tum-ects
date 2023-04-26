import psycopg2


class TUMWriteDatabase:

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

        # Create the 'degrees' table if it doesn't exist
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS degrees (
                degree_id SERIAL PRIMARY KEY,
                full_text_en TEXT,
                short_text_en TEXT,
                full_text_de TEXT,
                short_text_de TEXT
            );
        """)
        # Create the 'modules' table if it doesn't exist
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS modules (
                module_id SERIAL PRIMARY KEY,
                name_en TEXT,
                name_de TEXT
            );
        """)
        # Create the 'mappings' table if it doesn't exist
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS mappings (
                degree_id INTEGER,
                module_id INTEGER,
                degree_version TEXT,
                ects FLOAT,
                weighting_factor FLOAT,
                valid_from TEXT,
                valid_to TEXT,
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
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (degree_id) DO UPDATE
            SET full_text_en = EXCLUDED.full_text_en,
                short_text_en = EXCLUDED.short_text_en,
                full_text_de = EXCLUDED.full_text_de,
                short_text_de = EXCLUDED.short_text_de;
        """
        self.cursor.execute(query, (degree_id, full_text_en, short_text_en, full_text_de, short_text_de))
        self.connection.commit()

    def insert_module(self, module_id, name_en, name_de):
        query = """
            INSERT INTO modules (module_id, name_en, name_de)
            VALUES (%s, %s, %s)
            ON CONFLICT (module_id) DO UPDATE
            SET name_en = EXCLUDED.name_en,
                name_de = EXCLUDED.name_de;
        """
        self.cursor.execute(query, (module_id, name_en, name_de))
        self.connection.commit()

    def insert_mapping(self, degree_id, module_id, degree_version, ects, weighting_factor, valid_from, valid_to):
        query = """
            INSERT INTO mappings (degree_id, module_id, degree_version, ects, weighting_factor, valid_from, valid_to)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (degree_id, module_id) DO UPDATE
            SET degree_version = EXCLUDED.degree_version,
                ects = EXCLUDED.ects,
                weighting_factor = EXCLUDED.weighting_factor,
                valid_from = EXCLUDED.valid_from,
                valid_to = EXCLUDED.valid_to;
        """
        self.cursor.execute(query, (degree_id, module_id, degree_version, ects, weighting_factor, valid_from, valid_to))
        self.connection.commit()

