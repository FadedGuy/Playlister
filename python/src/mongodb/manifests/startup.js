const dbName = "database"

db = db.getSiblingDB(dbName);

db.createUser({
    user: "gatewayUser",
    pwd: "gatewayPassword",
    roles: [
        {role: "readWrite", db: "mydb"},
    ]
});

db.createUser({
    user: "converterUser",
    pwd: "converterPassword",
    roles: [
        {role: "readWrite", db: "mydb"},
    ]
});

