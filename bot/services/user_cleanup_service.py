# services/user_cleanup_service.py

def delete_expired_users():
    expired_users = get_expired_users()  # из БД
    for user in expired_users:
        remove_client(user.uuid)         # из config.json
        delete_user_from_db(user.uuid)   # из БД