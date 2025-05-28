db = db.getSiblingDB('nutri_voice_db');

db.createUser({
  user: 'nutri_app_user',
  pwd: 'nutri_app_password',
  roles: [
    {
      role: 'readWrite',
      db: 'nutri_voice_db'
    }
  ]
});

db.createCollection('users');
db.createCollection('meals');
db.createCollection('symptoms');

print('Database initialization completed successfully');
