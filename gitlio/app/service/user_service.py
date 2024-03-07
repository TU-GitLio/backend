from ..repository import s3_repository

def upload_profile(clerk_id: str, file_name: str):
    object_name = f'profile/{clerk_id}/{file_name}'
    return s3_repository.upload_file_to_s3(file_name, object_name)