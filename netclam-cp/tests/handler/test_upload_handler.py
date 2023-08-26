from fastapi import UploadFile
from unittest import mock
from netclam_cp.handler.upload_handler import create_directory, write_file

MOCK_REQUEST_ID = 'f0fc0043-4580-4845-aa53-7805a776c085'
MOCK_UPLOAD_FILE = mock.MagicMock()

@mock.patch('os.path.exists')
@mock.patch('os.makedirs')
def testCreateDirectory_CreatesDirectoryIfDoesntExist(mock_makedirs, mock_exists):
    mock_exists.return_value = False
    create_directory(MOCK_REQUEST_ID)
    mock_makedirs.assert_called_with(f'/data/{MOCK_REQUEST_ID}')

@mock.patch('os.path.exists')
@mock.patch('os.makedirs')
def testCreateDirectory_DoesntCreateDirectoryIfExists(mock_makedirs, mock_exists):
    mock_exists.return_value = True
    create_directory(MOCK_REQUEST_ID)
    assert not mock_makedirs.called

@mock.patch('os.path.exists')
@mock.patch('os.makedirs')
@mock.patch('builtins.open')
def testWriteFile_CreatesFileIfDoesntExist(mock_open, mock_makedirs, mock_exists):
    mock_exists.return_value = False
    MOCK_UPLOAD_FILE.return_value.filename.return_value = "mock_upload_file.txt"
    MOCK_UPLOAD_FILE.return_value.file.return_value.read.return_value = b'MOCKED FILE DATA'
    mock_file_handle = mock_open.return_value.__enter__.return_value
    write_file(MOCK_REQUEST_ID, MOCK_UPLOAD_FILE)
    assert mock_open.called
    assert mock_file_handle.write.called
    assert MOCK_UPLOAD_FILE.file.read.called

@mock.patch('os.path.exists')
@mock.patch('os.makedirs')
@mock.patch('builtins.open')
def testWriteFile_DoesntWriteFileIfExists(mock_open, mock_makedirs, mock_exists):
    mock_exists.return_value = True
    MOCK_UPLOAD_FILE.return_value.filename.return_value = "mock_upload_file.txt"
    MOCK_UPLOAD_FILE.return_value.file.return_value.read.return_value = b'MOCKED FILE DATA'
    mock_file_handle = mock_open.return_value.__enter__.return_value
    write_file(MOCK_REQUEST_ID, MOCK_UPLOAD_FILE)
    assert not mock_open.called
    assert not mock_file_handle.write.called
