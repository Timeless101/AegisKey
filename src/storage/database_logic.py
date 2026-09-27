import sqlite3
import src.common.errors as errors

#Create database
def create_database(database_name):
    try:
        with sqlite3.connect(database_name):
            return True
    except sqlite3.Error as sql_error:
        raise errors.DatabaseError(f"Could not open database") from sql_error


def create_table(table_name: str, columns: dict, database_name: str) -> True:
    if not isinstance(columns, dict):
        raise errors.WrongDataTypeDict("Columns must be a Dictionary.")

    try:
        columns_sql = []
        for column_name, column_definition in columns.items():
            columns_sql.append(f"{column_name} {column_definition}")

        columns_sql_string = ", ".join(columns_sql)

        run = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {columns_sql_string}
        );
        """
        
        with sqlite3.connect(database_name) as connection:
            c = connection.cursor()
            c.execute(run)
            connection.commit()
        
        return True

    except sqlite3.DatabaseError as sql_error:
        raise errors.TableCreationError(f"Couldn't create table") from sql_error


def insert_data(table_name: str, column_name: list, data_insert: list, database_name: str) -> True:
    if not isinstance(data_insert, list):
        raise errors.WrongDataTypeList("Data insert isn't a list.")
    
    if not isinstance(column_name, list):
        raise errors.WrongDataTypeList("column isn't a list.")
    
    if len(column_name) != len(data_insert):
        raise errors.DataLengthError("Column name and data insert list length isn't the same.")

    try:
        columns = ", ".join(column_name)
        placeholders = ", ".join(["?"] * len(data_insert))
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        with sqlite3.connect(database_name) as connection:
            c = connection.cursor()
            c.execute(sql, data_insert)
            connection.commit()
        return True

    except sqlite3.OperationalError as sql_error:
        raise errors.InsertError(f"No such table: {table_name}") from sql_error

    except sqlite3.DatabaseError as sql_error:
        raise errors.InsertError(f"Couldn't insert data") from sql_error
    
#Search data in datebase.
def search_specific_data(table: str, column: str, data_to_be_searched: str, database_name: str, userid) -> list | None:
    try:
        query = f"SELECT * FROM {table} WHERE {column} = ? AND userid = ?"
        value = data_to_be_searched
        with sqlite3.connect(database_name) as connection:
            c = connection.cursor()
            c.execute(query, (value, userid))
            rows = c.fetchall()

        if len(rows) == 0:
            return None
        
        return rows
    
    except sqlite3.OperationalError as table_error:
        raise errors.TableError(f"No such table: {table}") from table_error


def searcher(table: str, columns: list, column: tuple, data_to_search: str, database_name: str, userid: int) -> list[tuple] | None:

    try:
        if not isinstance(column, tuple):
            raise errors.WrongDataTypeTuple("Column isn't a tuple.")

        if not isinstance(columns, list):
            raise errors.WrongDataTypeList("Columns isn't a list.")

        column = column[0]

        column_str = ", ".join(columns)
        query = f"SELECT {column_str} FROM {table} WHERE {column} = ? AND Userid = ?;"
        with sqlite3.connect(database_name) as connection:
            c = connection.cursor()
            c.execute(query, (data_to_search, userid))
            row = c.fetchall()

        if len(row) == 0:
            return None

        return row
    
    except sqlite3.ProgrammingError as sql:
        raise errors.WrongSQLStatement(sql)

    except sqlite3.OperationalError as x:
        raise errors.DatabaseError(x)

    except sqlite3.Error as e:
        raise errors.DatabaseError(e)

def search_for_search_view(to_search: str, database: str, userid: int):
    try:
        query = f"""SELECT
                        row_number() OVER( 
                            PARTITION BY UserID
                            ORDER BY Service COLLATE NOCASE ASC
                            ) AS screen_number_ID,
                        *
                    FROM vault_storage WHERE Service LIKE ? AND Userid = ?
                    OR Username LIKE ? AND Userid = ?
                    OR Comment = ? AND userid = ?"""
        to_search = "%" + to_search

        with sqlite3.connect(database) as connection:
            c = connection.cursor()
            c.execute(query, (to_search, userid, to_search, userid, to_search, userid))
            searched_data = c.fetchall()

        if len(searched_data) == 0:
            return None

        return searched_data #screen_number, cred_id, Userid, Service, Username, Password, Comment, CreationDate, EditedDate
    
    except sqlite3.ProgrammingError as Programmers_fault:
        raise errors.WrongSQLStatement("The SQL statements are wrong, please check the query you wrote.") from Programmers_fault

    except sqlite3.OperationalError as Operation_error:
        raise errors.DatabaseError(f"Database Operation failed: {Operation_error}")

    except sqlite3.Error as Error:
        raise errors.UnexpectedError(f"There was a unexpected error: {Error}")

def search_interface_password_id(userid: int, database: str, limit: int) -> list[tuple] | None:

    try:
        query = """
        SELECT
            ROW_NUMBER() OVER(
            PARTITION BY UserID
            ) AS screen_number_ID ,

        Service,
        Username,
        EditedDate
        
        FROM vault_storage
        WHERE UserID = ?
        ORDER by EditedDate DESC
        LIMIT ?;"""

        with sqlite3.connect(database) as connection:
            c = connection.cursor()
            c.execute(query, (userid, limit))
            rows = c.fetchall()

        if len(rows) == 0:
            return None
        
        return rows # returns: [(screen_number_ID, Service, Username, EditedDate)]

        
    except sqlite3.ProgrammingError as Programmers_fault:
        raise errors.WrongSQLStatement("The SQL statements are wrong, please check the query you wrote.") from Programmers_fault

    except sqlite3.OperationalError as Operation_error:
        raise errors.DatabaseError(f"Database Operation failed: {Operation_error}")

    except sqlite3.Error as Error:
        raise errors.UnexpectedError(f"There was a unexpected error: {Error}")


def search_for_view_items(userid: int, limit: int, offset: int, database) -> list[tuple] | None:
    try:
        query = """
            SELECT
                ROW_NUMBER() OVER(
                PARTITION BY UserID
                ORDER BY Service COLLATE NOCASE ASC,
                    Username COLLATE NOCASE ASC
                ) AS screen_number_id,
                cred_id, 
                Service, 
                Username,
                Comment,
                EditedDate
            FROM vault_storage
            WHERE UserID = ? 
            ORDER BY service COLLATE NOCASE ASC, 
                    Username COLLATE NOCASE ASC
            LIMIT ? 
            OFFSET ?;
            """

        with sqlite3.Connection(database) as connection:
            c = connection.cursor()
            c.execute(query, (userid, limit, offset))

            rows = c.fetchall()

            if len(rows) == 0:
                return None

            return rows # returns [(screen_number_id, Service, Username, Comment, editeddate)]
    
    except sqlite3.ProgrammingError as Programmers_fault:
        raise errors.WrongSQLStatement("The SQL statements are wrong, please check the query you wrote.") from Programmers_fault
    
    except sqlite3.OperationalError as Operation_error:
        raise errors.DatabaseError(f"Database Operation failed: {Operation_error}")

    except sqlite3.Error as Error:
        raise errors.UnexpectedError(f"There was a unexpected error: {Error}")


def delete_item(database: str, table: str, cred_id: int, userid: int) -> bool:
    try:
        query = f"DELETE FROM {table} WHERE cred_id = ? AND userid = ?"

        with sqlite3.Connection(database) as connection:
            c = connection.cursor()
            c.execute(query, (cred_id, userid))
            return True

    except sqlite3.ProgrammingError as Programmers_fault:
                raise errors.WrongSQLStatement("The SQL statements are wrong, please check the query you wrote.") from Programmers_fault
            
    except sqlite3.OperationalError as Operation_error:
        raise errors.DatabaseError(f"Database Operation failed: {Operation_error}")

    except sqlite3.Error as Error:
                raise errors.UnexpectedError(f"There was a unexpected error: {Error}")


def update_item(table: str, cred_id: int, database: str, userid: int, column: str, new_data: str, new_date) -> bool:

    query_one = f"UPDATE {table} SET {column} = ? WHERE cred_id = ? AND Userid = ?"
    query_two = f"UPDATE {table} SET EditedDate = ? WHERE cred_id = ? AND userid = ? "

    with sqlite3.Connection(database) as connection:
        c = connection.cursor()
        c.execute(query_one, (new_data, cred_id, userid))
        c.execute(query_two, (new_date, cred_id, userid))
        return True

if __name__ == "__main__":
    ...