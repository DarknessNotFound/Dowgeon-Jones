import os
import sqlite3
import re
import Logging as Log

# Database Names
STOCK_DB = "DB_StockSimulator.db"

# Sqlite Database Settings
CONNECTION_PATH = os.path.join("./Databases", STOCK_DB)
ISOLATION_LEVEL = "DEFERRED"

# Tables Names
COMPANY_T = "Company"
INDUSTRY_T = "Industry"
HISTORY_T = "History"
PLAYERS_T = "Players"

# For purposes of the logging system.
FILE_NAME = "DbManagement"


# region "Helper"
def ExtractDiscordId(string: str) -> list:
    """Gets the discord id from the inputed string

    Args:
        string (str): string to extract from

    Returns:
        str: Empty if none are found, the discord id if that is found,
        and the original string if more than one is found.
    """
    pattern = "<@\d{18}>"
    patternIdOnly = "\d{18}"
    Canidates = re.findall(pattern, string)

    if len(Canidates) == 0:
        return []

    if len(Canidates) > 1:
        return [re.findall(patternIdOnly, Id)[0] for Id in Canidates]

    return [re.findall(patternIdOnly, Canidates[0])[0]]


# endregion


# region "Database Creation"
def CreateDb():
    """Creates all the databases nessessary for the program."""
    try:
        print("Creating the Sniping DB started.")
        conn = sqlite3.connect(CONNECTION_PATH)

        CreatePlayersTable(conn)

    except Exception as ex:
        print(f"Logging -- CreateDb -- {ex}")
        Log.Error(FILE_NAME, "CreateDb", str(ex))
    finally:
        conn.close()


def CreatePlayersTable(Conn: sqlite3.Connection) -> None:
    """Creates the datatable tracking all users.
    Args:
        Conn (sqlite3.Connection): Connection to the database
    """
    try:
        if TableExists(Conn, PLAYERS_T):
            return

        sql = f"""
        CREATE TABLE {PLAYERS_T}(
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            DiscordId TEXT NULL,
            Name TEXT NULL,
            Copper INTEGER NULL,
            PermissionLevel INTEGER NOT NULL DEFAULT 0,
            IsDeleted INTEGER NOT NULL DEFAULT 0
        );
        """
        Conn.execute(sql)
        Conn.commit()
        print(f"{PLAYERS_T} table has been created in the {Conn}")
    except Exception as ex:
        print(f"Logging -- CreatePlayersTable -- {ex}")
        Conn.rollback()
        raise ex


def CreateCompanyTable(Conn: sqlite3.Connection) -> None:
    """Creates the datatable tracking all companies.
    Args:
        Conn (sqlite3.Connection): Connection to the database
    """
    try:
        if TableExists(Conn, COMPANY_T):
            return

        sql = f"""
        CREATE TABLE '{COMPANY_T}' (
            Id INTEGER NOT NULL UNIQUE,
            Name TEXT UNIQUE,
            Stock TEXT UNIQUE,
            Price REAL NULL,
            UpperCap INTEGER NULL,
            LowerCap INTEGER NULL,
            Base INTEGER NULL,
            PlayerInfluence INTEGER NULL,
            LastPriceUpdate TEXT NULL,
            Industry INTEGER NULL,
            FOREIGN KEY("Industry") REFERENCES "Industry"("Id"),
            PRIMARY KEY("Id" AUTOINCREMENT)
        );
        """
        Conn.execute(sql)
        Conn.commit()
        print(f"{COMPANY_T} table has been created in the {Conn}")
    except Exception as ex:
        print(f"Logging -- CreateCompanyTable -- {ex}")
        Conn.rollback()
        raise ex


def CreateIndustryTable(Conn: sqlite3.Connection) -> None:
    """Creates the datatable tracking all the industries.
    Args:
        Conn (sqlite3.Connection): Connection to the database
    """
    try:
        if TableExists(Conn, INDUSTRY_T):
            return

        sql = f"""
        CREATE TABLE {INDUSTRY_T} (
            Id INTEGER NOT NULL UNIQUE,
            Name TEXT UNIQUE NULL,
            Trend INTEGER DEFAULT 0 NULL,
            PRIMARY KEY("Id" AUTOINCREMENT)
        );
        """
        Conn.execute(sql)
        Conn.commit()
        print(f"{INDUSTRY_T} table has been created in the {Conn}")
    except Exception as ex:
        print(f"Logging -- CreateIndustryTable -- {ex}")
        Conn.rollback()
        raise ex


def CreateHistoryTable(Conn: sqlite3.Connection) -> None:
    """Creates the datatable tracking the history of companies.
    Args:
        Conn (sqlite3.Connection): Connection to the database
    """
    try:
        if TableExists(Conn, INDUSTRY_T):
            return

        sql = f"""
            CREATE TABLE {HISTORY_T} (
                "Id"	INTEGER NOT NULL UNIQUE,
                "CompanyId"	INTEGER NOT NULL,
                FOREIGN KEY("CompanyId") REFERENCES "Company"("Id"),
                PRIMARY KEY("Id" AUTOINCREMENT)
            );
        """
        Conn.execute(sql)
        Conn.commit()
        print(f"{INDUSTRY_T} table has been created in the {Conn}")
    except Exception as ex:
        print(f"Logging -- CreateIndustryTable -- {ex}")
        Conn.rollback()
        raise ex


def TableExists(Conn: sqlite3.Connection, Table: str) -> bool:
    """Checks wether a table exists or not in the given database.

    Args:
        Conn (sqlite3.Connection): The database connection to check.
        Table (str): The name of the table.

    Returns:
        bool: True if the table exists; False otherwise.
    """
    try:
        sql = f"""SELECT name
              FROM sqlite_master
              WHERE type='table'
              AND name='{Table}';"""
        cur = Conn.execute(sql)
        result = cur.fetchall()
        return len(result) == 1
    except Exception as ex:
        print(f"DbManagement -- TableExists -- {ex}")
        raise ex

# endregion


# region "Create Commands"
def CreateSuperuser(DiscordId: str):
    """Creates a super user, this really should only be used once in main
    so that there is at least one user able to give others admin.

    Args:
        DiscordId (str): Their 18 digit discord id (only the numbers)
    """
    if PlayerExistsDiscordId(DiscordId=DiscordId):
        owner = ReadPlayerDiscordId(DiscordId=DiscordId)
        if len(owner) > 0:
            UpdatePlayerPermissionLevel(Id=owner[0], PermissionLevel=10)
    else:
        Id = CreatePlayer(DiscordId=DiscordId, Name="Owner")
        UpdatePlayerPermissionLevel(Id=Id, PermissionLevel=10)


def CreatePlayer(DiscordId: str = "", Name: str = "") -> int:
    """Adds a player by their discord id and/or their name.

    Args:
        DiscordId (str): The string to identify players,
                        should be the ctx.author.id.
        User (str): This should either be their name or discord username.

    Raises:
        Exception: PlayerExists --> if the user already exists then doesn't add
                                    and just returns that user's id
        Exception: No data return --> The query didn't return a user id.

    Returns:
        int: The user id or -1 if there was an exception thrown.
    """

    try:
        if DiscordId == "" and Name == "":
            raise Exception("Neither DiscordId nor Name inputed.")

        conn = sqlite3.connect(CONNECTION_PATH,
                               isolation_level=ISOLATION_LEVEL)
        cur = conn.cursor()
        sql = f"""
                INSERT INTO {PLAYERS_T}(DiscordId, Name)
                VALUES (?, ?);
            """
        params = (DiscordId, Name)
        cur.execute(sql, params)
        conn.commit()
        if cur.rowcount == 0:
            raise Exception("Insertion didn't return Id")

        result = cur.lastrowid

    except Exception as ex:
        print(f"{FILE_NAME} -- CreatePlayer -- {ex}")
        result = -1
        conn.rollback()

    finally:
        conn.close()
        return result

# endregion
# region Player CRUD


def PlayerExistsId(Id: int) -> bool:
    """Checks if a given Id exists in the players table

    Args:
        Id (Id): Id to check

    Raises:
        ex: Any error occurs

    Returns:
        bool: True if the table returns only one row
    """
    try:
        result = False
        conn = sqlite3.connect(CONNECTION_PATH)
        sql = f"SELECT * FROM {PLAYERS_T} WHERE Id=? AND IsDeleted=0"
        param = [str(Id)]
        cur = conn.execute(sql, param)
        NumRows = len(cur.fetchall())
        result = NumRows == 1

        if cur.rowcount > 1:
            raise Exception(f"Returned {NumRows} rows.")

    except Exception as ex:
        print(f"{FILE_NAME} -- PlayerExistsId -- {ex}")
        raise ex

    finally:
        conn.close()
        return result


def PlayerExistsDiscordId(DiscordId: str) -> bool:
    """Checks if a given DiscordId exists in the players table

    Args:
        DiscordId (str): Id to check

    Raises:
        ex: Any error occurs

    Returns:
        bool: True if the table returns only one row
    """
    try:
        result = False
        conn = sqlite3.connect(CONNECTION_PATH)
        sql = f"SELECT * FROM {PLAYERS_T} WHERE DiscordId=? AND IsDeleted=0"
        param = [str(DiscordId)]
        cur = conn.execute(sql, param)
        NumRows = len(cur.fetchall())
        result = NumRows != 0

        if cur.rowcount > 1:
            raise Exception(f"Returned {NumRows} rows.")

    except Exception as ex:
        print(f"{FILE_NAME} -- PlayerExistsDiscordId -- {ex}")
        raise ex

    finally:
        conn.close()
        return result


def PlayerExistsName(Name: str) -> bool:
    """Checks if a given DiscordId exists in the players table

    Args:
        DiscordId (str): Id to check

    Raises:
        ex: Any error occurs

    Returns:
        bool: True if the table returns only one row
    """
    try:
        result = False
        conn = sqlite3.connect(CONNECTION_PATH)
        sql = f"SELECT * FROM {PLAYERS_T} WHERE Name=? AND IsDeleted=0"
        param = [str(Name)]
        cur = conn.execute(sql, param)
        NumRows = len(cur.fetchall())
        result = NumRows == 1

        if cur.rowcount > 1:
            raise Exception(f"Returned {NumRows} rows.")

    except Exception as ex:
        print(f"{FILE_NAME} -- PlayerExistsName -- {ex}")
        raise ex

    finally:
        conn.close()
        return result


def ReadPlayerId(Id: int) -> list:
    """Returns a list of a Player's properties.

    Args:
        Id (int): Player Id to return

    Returns:
        list: Id, DiscordId, Name, Permissions, IsDeleted
    """
    try:
        result = []
        conn = sqlite3.connect(CONNECTION_PATH)
        sql = f"SELECT * FROM {PLAYERS_T} WHERE Id=? AND IsDeleted=0"
        param = [str(Id)]
        cur = conn.execute(sql, param)
        row = cur.fetchone()
        result = list(row)
    except Exception as ex:
        Log.Error(FILE_NAME, "ReadPlayerId", str(ex))
        print(f"{FILE_NAME} -- ReadPlayerId -- {ex}")
    finally:
        conn.close()
        return result


def ReadPlayerDiscordId(DiscordId: str) -> list:
    """Returns a list of a Player's properties.

    Args:
        DiscordId (str): Player DiscordId to return

    Returns:
        list: Id, DiscordId, Name, Permissions, IsDeleted
    """
    try:
        result = []
        conn = sqlite3.connect(CONNECTION_PATH)
        if PlayerExistsDiscordId(DiscordId=DiscordId):
            sql = f"SELECT * FROM {PLAYERS_T} WHERE DiscordId=? AND IsDeleted=0"
            param = [str(DiscordId)]
            cur = conn.execute(sql, param)
            row = cur.fetchone()
            result = list(row)
        else:
            print(f"Player DiscordId '{DiscordId}' does not exists.")
    except Exception as ex:
        Log.Error(FILE_NAME, "ReadPlayerDiscordId", str(ex))
    finally:
        conn.close()
        return result


def GetPermissionLevel(Id: int) -> int:
    """Returns the permission level of a given player Id.

    Args:
        Id (int): The player Id int the database.

    Returns:
        int: The permission level
    """
    try:
        result = 0
        conn = sqlite3.connect(CONNECTION_PATH)
        if PlayerExistsId(Id=Id):
            sql = f"SELECT * FROM {PLAYERS_T} WHERE Id=?;"
            param = (Id,)
            cur = conn.execute(sql, param)
            row = cur.fetchone()
            result = list(row)[3]
        else:
            print(f"Player Id:{Id} does not exists.")
    except Exception as ex:
        Log.Error(FILE_NAME, "GetPermissionLevel", str(ex))
    finally:
        conn.close()
        return result


def ReadPlayerName(Name: str) -> list:
    """Returns a list of a Player's properties.

    Args:
        Name (str): Player Name to return

    Returns:
        list: Id, DiscordId, Name, Permissions, IsDeleted
    """
    try:
        result = []
        conn = sqlite3.connect(CONNECTION_PATH)
        sql = f"SELECT * FROM {PLAYERS_T} WHERE Name=?;"
        param = [str(Name)]
        cur = conn.execute(sql, param)
        row = cur.fetchone()
        result = list(row)
    except Exception as ex:
        Log.Error(FILE_NAME, "ReadPlayerName", str(ex))
    finally:
        conn.close()
        return result


def ReadAllPlayers() -> list:
    """Gets all of the non-deleted players from the database.

    Returns:
        list: A list of all the players with the data being in
        the order of, respectively,
              Id, DiscordId, Name, Permissions, IsDeleted.
    """
    result = []
    try:
        conn = sqlite3.connect(CONNECTION_PATH)
        sql = f"SELECT * FROM {PLAYERS_T} WHERE IsDeleted=0;"
        cur = conn.execute(sql)
        rows = cur.fetchall()

        for row in rows:
            result.append(list(row))

    except Exception as ex:
        Log.Error(FILE_NAME, "ReadAllPlayers", str(ex))
        result = []
    finally:
        conn.close()
        return result


def ReadAllDeletedPlayers() -> list:
    """Gets a list of all the deleted players from the database.

    Returns:
        list: A list of all the deleted players with the data being in the
        order of, respectively,
              Id, DiscordId, Name, Permissions, IsDeleted.
    """
    result = []
    try:
        conn = sqlite3.connect(CONNECTION_PATH)
        sql = f"SELECT * FROM {PLAYERS_T} WHERE IsDeleted=1;"
        cur = conn.execute(sql)
        rows = cur.fetchall()

        for row in rows:
            result.append(list(row))

    except Exception as ex:
        Log.Error(FILE_NAME, "ReadAllDeletedPlayers", str(ex))
        result = []
    finally:
        conn.close()
        return result


def AuthorHavePermission(DiscordId, PermissionLevel: int) -> bool:
    """Checks if a given user has permission to use a command.

    Args:
        DiscordId (int or string): The player's 18 digit discord id
        PermissionLevel (int): The permission level to compare to.

    Returns:
        bool: True if they have permission, false otherwise.
    """
    player = ReadPlayerDiscordId(DiscordId)
    if len(player) < 4:
        return False
    else:
        return PermissionLevel <= player[3]


def PlayerDisplayName(Id: int) -> str:
    """Gets a player's display name.

    Args:
        Id (int): The player id.

    Returns:
        str: If the user has a discord id then it
        returns <@*18 digit id*> otherwise returns the name.
    """
    if PlayerExistsId(Id=Id):
        player = ReadPlayerId(Id=Id)
        if len(player) == 0:
            return ""

        # If player doesn't have a DiscordId then display name
        if player[1] == "":
            return player[2]
        # Otherwise show their discord name.
        else:
            return f"<@{player[1]}>"

    else:
        return ""


# endregion

# region "Update Commands"
def UpdatePlayerDiscordId(Id: int, DiscordId: str) -> None:
    """WIP: Update a given player's discord id.

    Args:
        Id (int): Player's id
        DiscordId (str): New Discord id.
    """
    return


def UpdatePlayerName(Id: int, Name: str) -> str:
    """Updates a player's name in the database.

    Args:
        Id (int): The player's id.
        Name (str): The new name of the player.

    Returns:
        str: A result message.
    """
    Updated = False
    if not PlayerExistsId(Id=Id):
        return False

    try:
        conn = sqlite3.connect(CONNECTION_PATH)
        sql = f"UPDATE {PLAYERS_T} SET Name=? WHERE Id=?;"
        param = (Name, Id)
        conn.execute(sql, param)
        conn.commit()
        Updated = True
    except Exception as ex:
        print("Error in UpdatePlayerPermissionLevel: " + str(ex))
        Log.Error(FILE_NAME, "UpdatePlayerPermissionLevel", str(ex))
    finally:
        conn.close()
        return Updated


def UpdatePlayerPermissionLevel(Id: int, PermissionLevel: int) -> bool:
    """Updates a player's permission level in the database.

    Args:
        Id (int): The players id.
        PermissionLevel (int): The new permission level.

    Returns:
        str: True if updated successfully.
    """
    Updated = False
    if not PlayerExistsId(Id=Id):
        return False

    try:
        conn = sqlite3.connect(CONNECTION_PATH)
        sql = f"UPDATE {PLAYERS_T} SET PermissionLevel=? WHERE Id=?"
        param = (PermissionLevel, Id)
        conn.execute(sql, param)
        conn.commit()
        Updated = True
    except Exception as ex:
        print("Error in UpdatePlayerPermissionLevel: " + str(ex))
        Log.Error(FILE_NAME, "UpdatePlayerPermissionLevel", str(ex))
    finally:
        conn.close()
        return Updated


def DeletePlayer(Id: int) -> str:
    """Soft deletes a player from the database.

    Args:
        Id (int): The player id to soft delete.

    Returns:
        str: Function output message.
    """
    Updated = "Didn't update."
    if not PlayerExistsId(Id=Id):
        return "Snipe Id doesn't exists."

    try:
        conn = sqlite3.connect(CONNECTION_PATH)
        sql = f"UPDATE {PLAYERS_T} SET IsDeleted=1 WHERE Id=?;"
        param = (Id,)
        conn.execute(sql, param)
        conn.commit()
        Updated = f'Removed player of id "{Id}" from the database.'
    except Exception as ex:
        print(f'ERROR: In file "{FILE_NAME}" of function "DeleteSnipe"')
        print(f"Message: {str(ex)}")
        Log.Error(FILE_NAME, "DeletePlayer", str(ex))
        Updated = "ERROR: An error has occured..."
    finally:
        conn.close()
        return Updated


def UndoDeletePlayer(Id: int) -> str:
    """Undos the soft deletion of a player from the database.

    Args:
        Id (int): Player id to undo.

    Returns:
        str: Output message.
    """
    Updated = "Didn't update."

    try:
        conn = sqlite3.connect(CONNECTION_PATH)
        sql = f"UPDATE {PLAYERS_T} SET IsDeleted=0 WHERE Id=?;"
        param = (Id,)
        conn.execute(sql, param)
        conn.commit()
        Updated = f'Readded player of id "{Id}" from the database.'
    except Exception as ex:
        print(f'ERROR: In file "{FILE_NAME}" of function "DeleteSnipe"')
        print(f"Message: {str(ex)}")
        Log.Error(FILE_NAME, "UndoDeletePlayer", str(ex))
        Updated = "ERROR: An error has occured..."
    finally:
        conn.close()
        return Updated
# endregion
