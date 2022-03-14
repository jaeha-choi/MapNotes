import hashlib
import hmac
import io
import os
import pathlib
import pickle
import secrets
import stat
import sys

from azure.storage.blob import BlobServiceClient
from azure.storage.blob import ContainerClient


# Internal node for representing directory structure
class _Node:
    def __init__(self):
        self.subdir = {}  # dir_str:Node
        self.file = {}  # filename: checksum

    def _str_helper(self, curr: "_Node", space: int) -> str:
        spacer = space * "\t"
        string = ""
        for sub, node in curr.subdir.items():
            string += spacer + sub + "/\n"
            string += self._str_helper(node, space + 1)
        for file, checksum in curr.file.items():
            string += spacer + file + ": " + str(checksum[:10]) + "...\n"
        return string

    def __str__(self) -> str:
        return self._str_helper(self, 0)


class AzureUpload:
    def __init__(self, storage_url: str, container_name: str, storage_key: str, signature_key: bytes):
        """
        Initializes Azure file upload tool
        :param container_name: Name of a container to store backups
        :param signature_key: Key to use when generating signatures
        """
        # Constants
        self._p_file = "index.bin"
        self._sig_byte_size = 64
        self._sig_hash_func = hashlib.sha512
        self._file_hash_func = hashlib.md5

        # Variables
        c: BlobServiceClient = BlobServiceClient(account_url=storage_url, credential=storage_key)

        self._secret_key = signature_key
        self._container = None

        for b in c.list_containers():
            if b.name == container_name:
                self._container: ContainerClient = c.get_container_client(container_name)
        if self._container is None:
            self._container: ContainerClient = c.create_container(container_name)

    def _read_local_helper(self, full_path: str, path: str, n: _Node, follow: bool) -> None:
        path = os.path.normpath(path)
        curr = n.subdir[path] = _Node()
        root, sub_dirs, files = next(os.walk(full_path))

        for sub_dir in sub_dirs:
            if not follow and os.path.islink(os.path.join(root, sub_dir)):
                continue
            self._read_local_helper(os.path.join(full_path, sub_dir), sub_dir, curr, follow)
        for file in files:
            with open(os.path.join(root, file), "rb") as f:
                # curr.file[file] = self._file_hash_func(f.read()).digest()
                curr.file[file] = self._file_hash_func(f.read()).hexdigest()

    def _read_local(self, path: str, follow: bool) -> (_Node, _Node, str):
        n = _Node()
        curr = n
        path = os.path.abspath(path)
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)
        dirs = path.split(os.sep)
        for dd in dirs[:-1]:
            curr.subdir[dd] = _Node()
            curr = curr.subdir[dd]

        self._read_local_helper(path, dirs[-1], curr, follow)
        return n, curr.subdir[dirs[-1]], path

    def _read_server(self, path: str, insecure: bool = False) -> (_Node, _Node, str):
        found = False
        for b in self._container.list_blobs():
            found = b.name == self._p_file
            if found:
                break

        if not found:
            print("No existing backup found")
            new = _Node()
        else:
            with io.BytesIO() as tmp:
                self._container.download_blob(self._p_file).readinto(tmp)
                tmp.seek(0)
                file_sig = tmp.read(self._sig_byte_size)
                b = tmp.read()
            sig = hmac.new(self._secret_key, b, self._sig_hash_func)
            if not hmac.compare_digest(file_sig, sig.digest()):
                if insecure:
                    print("#######################################")
                    print("#### Index file signature mismatch ####")
                    print("#######################################")
                    print("Index file is breached or signature is updated locally")
                    print("--insecure flag detected; Continuing...")
                else:
                    raise AssertionError("index file signature mismatch")
            new = pickle.loads(b)

        curr = new
        path = os.path.normpath(os.path.join("prog5", path))
        for dd in path.split(os.sep):
            curr.subdir.setdefault(dd, _Node())
            curr = curr.subdir[dd]

        return new, curr, path

    def _restore_helper(self, local_full_path: str, remote_full_path: str, local_curr: _Node,
                        remote_curr: _Node, overwrite: bool) -> int:
        cnt = 0
        for sub_dir_str, node in remote_curr.subdir.items():
            local_curr.subdir.setdefault(sub_dir_str, _Node())
            cnt += self._restore_helper(os.path.join(local_full_path, sub_dir_str),
                                        os.path.join(remote_full_path, sub_dir_str),
                                        local_curr.subdir[sub_dir_str], node, overwrite)

        pathlib.Path(local_full_path).mkdir(parents=True, exist_ok=True)

        for file, checksum in remote_curr.file.items():
            if overwrite or file not in local_curr.file or local_curr.file[file] != checksum:
                print("Downloading:", os.path.normpath(os.path.join(remote_full_path, file)))
                with open(os.path.join(local_full_path, file) + ".unsafe", "w+b") as f:
                    try:
                        self._container.download_blob(os.path.join(remote_full_path, file)).readinto(f)
                    except Exception as e:
                        print("Error:", e)
                        continue
                    f.seek(0)
                    print("Verification... ", end="")
                    verified = checksum == self._file_hash_func(f.read()).hexdigest()
                if verified:
                    print("OK")
                    os.renames(os.path.join(local_full_path, file) + ".unsafe", os.path.join(local_full_path, file))
                else:
                    print("FAIL. Removing.")
                    os.remove(os.path.join(local_full_path, file) + ".unsafe")
                cnt += 1
        return cnt

    def restore(self, local_path: str, remote_path: str, overwrite: bool = False) -> None:
        """
        Restore contents in container to specified local directory.

        :param local_path: Local path to restore to. Can be absolute or relative path.
                            Creates new directory if it doesn't exist.
        :param remote_path: Path to save to in container. No-op if remote-path not found.
        :param overwrite: Whether to overwrite files on the local machine even if the hash matches. (per spec)
        :return: None
        :raise AssertionError: If index file signature does not match local signature
        """
        _, local_cd, local_full_path = self._read_local(local_path, follow=False)
        _, remote_cd, remote_full_path = self._read_server(remote_path, insecure=False)

        print("----- Remote directory tree -----\n" + str(remote_cd) + "---------------------------------")

        processed = self._restore_helper(local_full_path, remote_full_path, local_cd, remote_cd, overwrite)
        print("Restored %d files" % processed)

    def _backup_helper(self, local_full_path: str, remote_full_path: str, local_curr: _Node, remote_curr: _Node,
                       overwrite: bool) -> int:
        cnt = 0
        for sub_dir_str, node in local_curr.subdir.items():
            # If remote does not have current sub dir, create it
            remote_curr.subdir.setdefault(sub_dir_str, _Node())
            cnt += self._backup_helper(os.path.join(local_full_path, sub_dir_str),
                                       os.path.join(remote_full_path, sub_dir_str),
                                       node, remote_curr.subdir[sub_dir_str],
                                       overwrite)

        for file, checksum in local_curr.file.items():
            if file not in remote_curr.file or remote_curr.file[file] != checksum:
                remote_curr.file[file] = checksum
                print("Uploading: %s\t%s" % (str(file).ljust(10),
                                             os.path.normpath(os.path.join(remote_full_path, file))))
                with open(os.path.join(local_full_path, file), "rb") as f:
                    self._container.upload_blob(os.path.normpath(os.path.join(remote_full_path, file)), data=f,
                                                overwrite=overwrite)
                cnt += 1

        # Create empty folder
        # if not local_curr.subdir and not local_curr.file:
        #     self._container.put_object(Key=remote_full_path)

        return cnt

    def backup(self, local_path: str, remote_path: str, follow: bool = False, overwrite: bool = True,
               insecure: bool = False) -> None:
        """
        Performs a backup and upload it to container.

        :param local_path: Local path to back up. Can be absolute or relative path.
        :param remote_path: Path to save to in container. Creates directories if not found.
        :param follow: Whether to follow the symlinks. WARNING: This function does NOT detect cycles.
        :param overwrite: overwrite existing file
        :param insecure: If set to true, continue even when the validation fails
        :return: None
        :raise ValueError: If local_path is not a valid directory
        :raise AssertionError: If index file signature does not match local signature
        """
        if not os.path.isdir(local_path):
            raise ValueError("%s is not a directory" % local_path)
        local_full_struct, local_cd, local_full_path = self._read_local(local_path, follow=follow)
        remote_full_struct, remote_cd, remote_full_path = self._read_server(remote_path, insecure=insecure)

        # print("----- Local directory tree -----\n" + str(local_cd) + "--------------------------------")

        processed = self._backup_helper(local_full_path, remote_full_path, local_cd, remote_cd, overwrite)

        if processed:
            with io.BytesIO() as tmp:
                res = pickle.dumps(remote_full_struct, protocol=pickle.HIGHEST_PROTOCOL)
                tmp.write(hmac.new(self._secret_key, res, digestmod=self._sig_hash_func).digest())
                tmp.write(res)
                tmp.seek(0)
                self._container.upload_blob(self._p_file, data=tmp, overwrite=True)

        print("Uploaded %d files + 1 index file" % processed)


def get_secret(filename: str = "secret.key") -> bytes:
    """
    Read or create secret key for signatures

    :param filename: Name of a file containing secret key
    :return: Secret key in bytes
    """
    if os.path.isfile(filename):
        print("Using existing key")
        with open(filename, "rb") as s:
            k = s.read()
    else:
        print("Creating new keys")
        k = secrets.token_hex(64).encode()
        with open(filename, "wb") as s:
            s.write(k)
    os.chmod(filename, stat.S_IRUSR | stat.S_IWUSR)  # chmod 600
    return k


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("You must pass in exactly 3 arguments")
        print("Usage:")
        print("% backup <local-directory-name> <container-name::remote-directory-name>")
        print("% restore <local-directory-name> <container-name::remote-directory-name>")
        sys.exit(1)

    try:
        local, remote_dir = sys.argv[2], sys.argv[3]

        s_name = os.getenv("PROJ_5_STORAGE_URL")
        s_key = os.getenv("PROJ_5_STORAGE_CREDENTIAL_KEY")

        key = get_secret()

        auto = AzureUpload(s_name, "prog5", s_key, key)
        if sys.argv[1].lower() == "backup":
            auto.backup(local_path=local, remote_path=remote_dir, overwrite=False)
        elif sys.argv[1].lower() == "restore":
            auto.restore(local_path=local, remote_path=remote_dir, overwrite=False)
        else:
            print("First argument must be backup or restore.")
            sys.exit(1)
    except (ValueError, AssertionError, PermissionError) as exception:
        print("Error:", exception)
        sys.exit(1)
