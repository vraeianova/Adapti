from .sanitize_folders import sanitize_name


def file_path(instance, filename):
    filename = sanitize_name(filename)
    return f"files/{filename}"


# USER'S GENERAL
def user_profile_pic_directory_path(instance, filename):
    folder_name = sanitize_name(instance.id_user.email)
    filename = sanitize_name(filename)
    return f"user_{folder_name}/profile_pictures/{filename}"
