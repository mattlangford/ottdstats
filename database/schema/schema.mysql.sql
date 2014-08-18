CREATE TABLE db_upgrade (
  id INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL,
  sql_query TEXT,
  version INTEGER
);

CREATE TABLE IF NOT EXISTS 'upgrade_history' (
  id INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL,
  upgrade_date DATE,
  version INTEGER
);

INSERT INTO db_upgrade (sql_query, version)
VALUES (
'CREATE TABLE Server (
  id INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL,
  name VARCHAR(50)
);', 1);

INSERT INTO db_upgrade (sql_query, version)
VALUES (
'CREATE TABLE State (
  server_id INTEGER PRIMARY KEY NOT NULL,
  last_snapshot TEXT,
  last_snapshot_time DATE,
  game_id INTEGER
);', 1);

INSERT INTO db_upgrade (sql_query, version)
VALUES (
'CREATE TABLE game(
  id INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL,
  server_id INTEGER PRIMARY KEY NOT NULL,
  game_start DATE,
  game_end DATE
);', 1);

INSERT INTO db_upgrade (sql_query, version)
VALUES (
'CREATE TABLE game_history(
  id INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL,
  server_id INTEGER NOT NULL,
  game_id INTEGER NOT NULL,
  company_id INTEGER NOT NULL
);', 1);