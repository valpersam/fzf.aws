"""helper class for constructing extra args for s3

using fzf to construct some of the extra argument for s3 operation
"""
from fzfaws.utils.pyfzf import Pyfzf
from fzfaws.kms.kms import KMS
from fzfaws.utils.util import get_confirmation


class S3Args:
    """helper class to construct extra argument

    Attributes:
        s3: s3 instance from the S3 class
        _extra_args: dict, extra argument to use for s3 operation
    """

    def __init__(self, s3):
        self.s3 = s3
        self._extra_args = {}

    def set_extra_args(self, storage=False, acl=False, metadata=False, encryption=False, tags=False, version=False, upload=False):
        """determine what attributes to set

        Use fzf menu to let user select attributes to configure

        Args:
            storage: bool, set storage
            acl: bool, set acl
            metadata: bool, set metadata
            encryption: bool, set server_side_encryption
            tags: bool, set tags
            version: bool, reduce the menu size, as some attributes cannot be configured
            upload: bool, determine if the menu could have empty selection
        Returns:
            None
        Exceptions:
            NoSelectionMade: When uplaod is false and no selection is made
        """
        attributes = []
        if version:
            if not metadata and not acl and not tags:
                print('Select attributes to configure')
                fzf = Pyfzf()
                fzf.append_fzf('ACL\n')
                fzf.append_fzf('Tagging')
                attributes = fzf.execute_fzf(
                    print_col=1, multi_select=True, empty_allow=False)
        else:
            if not storage and not acl and not metadata and not encryption and not tags:
                print('Select attributes to configure')
                fzf = Pyfzf()
                fzf.append_fzf('StorageClass\n')
                fzf.append_fzf('ACL\n')
                fzf.append_fzf('Encryption\n')
                fzf.append_fzf('Metadata\n')
                fzf.append_fzf('Tagging\n')
                attributes = fzf.execute_fzf(
                    print_col=1, multi_select=True, empty_allow=upload)

        for attribute in attributes:
            if attribute == 'StorageClass':
                storage = True
            elif attribute == 'ACL':
                acl = True
            elif attribute == 'Metadata':
                metadata = True
            elif attribute == 'Encryption':
                encryption = True
            elif attribute == 'Tagging':
                tags = True

        # only show previous values if one object is selected
        if not upload and not version and len(self.s3.path_list) == 1:
            s3_obj = self.s3.resource.Object(
                self.s3.bucket_name, self.s3.path_list[0])
            old_storage_class = s3_obj.storage_class if s3_obj.storage_class else 'STANDARD'
            old_encryption = s3_obj.server_side_encryption if s3_obj.server_side_encryption else 'None'
        elif not upload and version:
            pass

        if storage:
            self.set_storageclass(original=old_storage_class)
        if acl:
            self.set_ACL()
        if encryption:
            self.set_encryption(original=old_encryption)
        if metadata:
            self.set_metadata()
        if tags:
            self.set_tags()

    def set_metadata(self):
        """set the meta data for the object"""

        print(
            'Enter meta data for the upload objects, enter without value will skip tagging')
        print(
            'Metadata format should be a URL Query alike string (e.g. Content-Type=hello&Cache-Control=world)')
        metadata = input('Metadata: ')
        if metadata:
            self._extra_args['Metadata'] = {}
            for item in metadata.split('&'):
                key, value = item.split('=')
                self._extra_args['Metadata'][key] = value

    def set_storageclass(self, original=None):
        """set valid storage class

        Args:
            original: string, previous value of the storage_class
        """

        print('Select a storage class, esc to use the default storage class of the bucket setting')
        if original:
            print('Orignal: %s' % original)
        fzf = Pyfzf()
        fzf.append_fzf('STANDARD\n')
        fzf.append_fzf('REDUCED_REDUNDANCY\n')
        fzf.append_fzf('STANDARD_IA\n')
        fzf.append_fzf('ONEZONE_IA\n')
        fzf.append_fzf('INTELLIGENT_TIERING\n')
        fzf.append_fzf('GLACIER\n')
        fzf.append_fzf('DEEP_ARCHIVE\n')
        result = fzf.execute_fzf(empty_allow=True, print_col=1)
        if result:
            self._extra_args['StorageClass'] = result

    def set_ACL(self):
        """set the ACL option for the current operation"""
        print(
            'Select a type of ACL to grant, aws accept one of canned ACL or explicit ACL')
        fzf = Pyfzf()
        fzf.append_fzf('None (use bucket default ACL setting)\n')
        fzf.append_fzf(
            'Canned ACL (predefined set of grantees and permissions)\n')
        fzf.append_fzf(
            'Explicit ACL (explicit set grantees and permissions)\n')
        result = fzf.execute_fzf(empty_allow=True, print_col=1)
        if result == 'Canned':
            self._set_canned_ACL()
        elif result == 'Explicit':
            self._set_explicit_ACL()
        else:
            return

    def _set_explicit_ACL(self):
        """set explicit ACL for grantees and permissions

        Get user id/email first than display fzf allow multi_select
        to select permissions
        """
        # get what permission to set
        fzf = Pyfzf()
        fzf.append_fzf('GrantFullControl\n')
        fzf.append_fzf('GrantRead\n')
        fzf.append_fzf('GrantReadACP\n')
        fzf.append_fzf('GrantWriteACP\n')
        results = fzf.execute_fzf(
            empty_allow=True, print_col=1, multi_select=True)
        if not results:
            print(
                'No permission is set, default ACL settings of the bucket would be used')
        else:
            for result in results:
                print('Set permisstion for %s' % result)
                print('Enter a list of either the Canonical ID, Account email, Predefined Group url to grant permission (Seperate by comma)')
                print(
                    'Format: id=XXX,id=XXX,emailAddress=XXX@gmail.com,uri=http://acs.amazonaws.com/groups/global/AllUsers')
                accounts = input('Accounts: ')
                print(80*'-')
                self._extra_args[result] = str(accounts)

    def _set_canned_ACL(self):
        """set the canned ACL for the current operation"""
        print(
            'Select a Canned ACL option, esc to use the default ACL setting for the bucket')
        fzf = Pyfzf()
        fzf.append_fzf('private\n')
        fzf.append_fzf('public-read\n')
        fzf.append_fzf('public-read-write\n')
        fzf.append_fzf('authenticated-read\n')
        fzf.append_fzf('aws-exec-read\n')
        fzf.append_fzf('bucket-owner-read\n')
        fzf.append_fzf('bucket-owner-full-control\n')
        result = fzf.execute_fzf(empty_allow=True, print_col=1)
        if result:
            self._extra_args['ACL'] = result

    def set_encryption(self, original=None):
        """set the encryption setting

        Args:
            original_type: string, previous value of the encryption
        """
        print('Select a ecryption setting, esc to use the default encryption setting for the bucket')
        if original:
            print('Orignal: %s' % original)
        fzf = Pyfzf()
        fzf.append_fzf('None\n')
        fzf.append_fzf('AES256\n')
        fzf.append_fzf('aws:kms\n')
        result = fzf.execute_fzf(empty_allow=True, print_col=1)
        if result:
            self._extra_args['ServerSideEncryption'] = result
        if result == 'aws:kms':
            current_region = self.s3.client.get_bucket_location(
                Bucket=self.s3.bucket_name)
            current_region = current_region.get('LocationConstraint')
            kms = KMS()
            kms.set_keyid()
            self._extra_args['SSEKMSKeyId'] = kms.keyid

    def set_tags(self):
        """set tags for the object"""
        print(
            'Enter tags for the upload objects, enter without value will skip tagging')
        print(
            'Tag format should be a URL Query alike string (e.g. tagname=hello&tag2=world)')
        tags = input('Tags: ')
        if tags:
            self._extra_args['Tagging'] = tags

    def check_tag_acl(self):
        """check if the only attributes to configure is ACL or Tags

        Args:
            None
        Returns:
            result: dict, containing two keys, Tags and Grants
            Structure: {
                'Tags': list, list of tags = {'Key': value, 'Value': value}
                'Grants': dict, = {
                    'ACL': string,
                    'GrantFullControl': string,
                    'GrantRead': string,
                    'GrantReadACP': string,
                    'GrantWriteACP': string
                }
            }
        """
        result = {}
        if not self._extra_args.get('StorageClass') and not self._extra_args.get('ServerSideEncryption') and not self._extra_args.get('Metadata'):
            if self._extra_args.get('Tagging'):
                tags = []
                for tag in self._extra_args.get('Tagging').split('&'):
                    key, value = tag.split('=')
                    tags.append({'Key': key, 'Value': value})
                result['Tags'] = tags
            if self._extra_args.get('ACL'):
                if not result.get('Grants'):
                    result['Grants'] = {}
                result['Grants']['ACL'] = self._extra_args.get('ACL')
            if self._extra_args.get('GrantFullControl'):
                if not result.get('Grants'):
                    result['Grants'] = {}
                result['Grants']['GrantFullControl'] = self._extra_args.get(
                    'GrantFullControl')
            if self._extra_args.get('GrantRead'):
                if not result.get('Grants'):
                    result['Grants'] = {}
                result['Grants']['GrantRead'] = self._extra_args.get(
                    'GrantRead')
            if self._extra_args.get('GrantReadACP'):
                if not result.get('Grants'):
                    result['Grants'] = {}
                result['Grants']['GrantReadACP'] = self._extra_args.get(
                    'GrantReadACP')
            if self._extra_args.get('GrantWriteACP'):
                if not result.get('Grants'):
                    result['Grants'] = {}
                result['Grants']['GrantWriteACP'] = self._extra_args.get(
                    'GrantWriteACP')
        return result

    @property
    def extra_args(self):
        return self._extra_args

    @property
    def storage_class(self):
        return self._extra_args.get('StorageClass')

    @property
    def tags(self):
        return self._extra_args.get('Tagging', '')

    @property
    def encryption(self):
        return self._extra_args.get('ServerSideEncryption', '')

    @property
    def kms_id(self):
        return self._extra_args.get('SSEKMSKeyId', '')

    @property
    def acl(self):
        return self._extra_args.get('ACL', '')

    @property
    def metadata(self):
        return self._extra_args.get('Metadata', {})

    @property
    def acl_full(self):
        return self._extra_args.get('GrantFullControl', '')

    @property
    def acl_read(self):
        return self._extra_args.get('GrantRead', '')

    @property
    def acl_acp_read(self):
        return self._extra_args.get('GrantReadACP', '')

    @property
    def acl_acp_write(self):
        return self._extra_args.get('GrantWriteACP', '')
