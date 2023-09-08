CREATE TABLE IF NOT EXISTS user(  
	id VARCHAR(36) PRIMARY KEY NOT NULL, /* Use UUIDs instead of AUTOINCREMENT integers */
	username VARCHAR(200) NOT NULL,
	password_ VARCHAR(100) NOT NULL, /* For some reason password is highlited as a keyword */
	p_id VARCHAR(36), /* Password ID, increases security and does password change checks */
	controls BOOLEAN DEFAULT 0 NOT NULL, /* Likely better methods but this works */
	last_login DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL /* Could be used to check unauthorized logins */
);

CREATE TABLE IF NOT EXISTS buy( /* Multiple buys can't be stored in a single trade */
	id INTEGER PRIMARY KEY AUTOINCREMENT, /* Being referenced in list only, UUIDs seem overkill */
	symbol VARCHAR(5) NOT NULL, /* Could be used in a raw format */
	price DECIMAL NOT NULL,
	shares INTEGER NOT NULL,
	stamped DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL /* No explanation required for last 3 */
);
CREATE TABLE IF NOT EXISTS sell( /* Same as above, mutliple could be stored as stringified JSON */
	id INTEGER PRIMARY KEY AUTOINCREMENT, /* Very rarely interacted with on the front end */
	symbol VARCHAR(5) NOT NULL,
	price DECIMAL NOT NULL, /* Likely the most important value */
	shares INTEGER NOT NULL,
	stamped DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL /* Stamp everything for logging purposes */
);

/* Create indexes for ids on buy/sell tables */
CREATE UNIQUE INDEX IF NOT EXISTS buy_ids ON buy(id);
CREATE UNIQUE INDEX IF NOT EXISTS sell_ids ON sell(id);

CREATE UNIQUE INDEX IF NOT EXISTS buy_dates ON buy(stamped);
CREATE UNIQUE INDEX IF NOT EXISTS sell_dates ON sell(stamped);

CREATE UNIQUE INDEX IF NOT EXISTS buy_symbol ON buy(symbol);
CREATE UNIQUE INDEX IF NOT EXISTS sell_symbol ON sell(symbol);

CREATE TABLE IF NOT EXISTS trade( /* More front-end friendly container */
	id INTEGER PRIMARY KEY AUTOINCREMENT, /* Again, does not require extreme uniqueness */
	symbol VARCHAR(5) NOT NULL, /* Centralize all data */
	buys TEXT, /* Store as CSV of ids */
	sells TEXT, /* Store as CSV of ids */
	final_sell DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL /* Final edit modifies this value */
);

CREATE UNIQUE INDEX IF NOT EXISTS t_symbols ON trade(symbol);

/* Table to store tickers to watch */
CREATE TABLE IF NOT EXISTS symbol(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	symbol VARCHAR(5) NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS ticker_index ON symbol(symbol);

CREATE TABLE IF NOT EXISTS setting( /* Storage for settings that is entirely dynamic */
	id INTEGER PRIMARY KEY AUTOINCREMENT, /* Does not require extreme uniqueness */
	name TEXT NOT NULL, /* Simple name-value method for storing... why tf didn't I just use JSON? */
	value TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS settings_index ON setting(name, value);