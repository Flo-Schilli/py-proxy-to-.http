import io
import os
import tempfile
import zipfile


class Zip:
    @staticmethod
    def zip_file(storage_path: tempfile.TemporaryDirectory) -> io.BytesIO:
        data = io.BytesIO()

        with zipfile.ZipFile(data, mode='w') as z:
            for file_name in os.listdir(storage_path.name):
                absolute_path = os.path.join(storage_path.name, file_name)
                relative_path = os.path.relpath(absolute_path, storage_path.name)
                z.write(absolute_path, arcname=relative_path)

        data.seek(0)

        return data
