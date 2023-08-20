import pytest
from fastapi.testclient import TestClient
from netclam_common.exception import FileNotFoundException, ResultNotFoundException, RequestNotFoundException
from netclam_common.models.request import request
from netclam_common.models.result import result
from netclam_common.models.file import file
from netclam_cp.main import app
from netclam_cp import version, api_name
from unittest import mock

mockRequestData = [
    {
        "id": "f0fc0043-4580-4845-aa53-7805a776c085",
        "status": "PENDING",
        "created_time": "2023-08-19 21:34:17.000000",
        "updated_time": "2023-08-19 21:34:17.000000"
    },{
        "id": "939b91eb-a844-41f4-86b0-237e9df2839c",
        "status": "COMPLETED",
        "created_time": "2023-08-19 21:34:17.000000",
        "updated_time": "2023-08-19 22:15:14.000000"
    },
    {
        "id": "72710413-b3d8-4883-ac30-8a03ee9dfccd",
        "status": "COMPLETED",
        "created_time": "2023-08-19 21:36:17.000000",
        "updated_time": "2023-08-19 22:17:14.000000"
    }
]

mockFileData = [
    {
        "request_id": "f0fc0043-4580-4845-aa53-7805a776c085",
        "name": "mock_file1.txt"
    },
    {
        "request_id": "939b91eb-a844-41f4-86b0-237e9df2839c",
        "name": "mock_file2.pdf"
    },
    {
        "request_id": "72710413-b3d8-4883-ac30-8a03ee9dfccd",
        "name": "mock_file3.tar"
    }
]

mockResultData = [
    {
        "request_id": "939b91eb-a844-41f4-86b0-237e9df2839c",
        "decision": "INFECTED",
        "decision_time": "2023-08-19 22:15:14.000000"
    },
    {
        "request_id": "72710413-b3d8-4883-ac30-8a03ee9dfccd",
        "decision": "CLEAN",
        "decision_time": "2023-08-19 22:17:14.000000"
    }
]


api_root = f"/v{version}/{api_name}"

@pytest.fixture
def test_client():
    return TestClient(app)

@mock.patch('netclam_cp.main.get_request')
def testGetNoRequestIdProvided_returns400(mock_request, test_client):
    response = test_client.get(api_root)
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid Request ID"}

@mock.patch('netclam_cp.main.get_request')
def testGetRequestNotFound_returns404(mock_request, test_client):
    mock_request.side_effect = RequestNotFoundException(
        "Unable to find request with id: 4a57d0bf-7e1a-4a5f-b5bf-605c27c30006"
    )
    response = test_client.get(f"{api_root}?id=4a57d0bf-7e1a-4a5f-b5bf-605c27c30006")
    assert response.status_code == 404
    assert response.json() == {"detail": "Request Not Found"}

@mock.patch('netclam_cp.main.get_request')
@mock.patch('netclam_cp.main.get_file')
def testGetFileNotFound_returns500(mock_file, mock_request, test_client):
    mock_request.return_value = request(**mockRequestData[0])
    mock_file.side_effect = FileNotFoundException(
        "Unable to find file for request with id: f0fc0043-4580-4845-aa53-7805a776c085"
    )
    response = test_client.get(f"{api_root}?id=f0fc0043-4580-4845-aa53-7805a776c085")
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal Server Error"}

@mock.patch('netclam_cp.main.get_request')
@mock.patch('netclam_cp.main.get_result')
@mock.patch('netclam_cp.main.get_file')
def testGetResultNotFound_returns500(mock_file, mock_result, mock_request, test_client):
    mock_request.return_value = request(**mockRequestData[1])
    mock_result.side_effect = ResultNotFoundException(
        "Unable to find result for request with id: 939b91eb-a844-41f4-86b0-237e9df2839c"
    )
    mock_file.return_value = file(**mockFileData[1])
    response = test_client.get(f"{api_root}?id=939b91eb-a844-41f4-86b0-237e9df2839c")
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal Server Error"}

@mock.patch('netclam_cp.main.get_request')
@mock.patch('netclam_cp.main.get_file')
def testGetRequestPendingRequest_returns200(mock_file, mock_request, test_client):
    mock_request.return_value = request(**mockRequestData[0])
    mock_file.return_value = file(**mockFileData[0])
    response = test_client.get(f"{api_root}?id=f0fc0043-4580-4845-aa53-7805a776c085")
    mock_response = mockRequestData[0].copy()
    mock_response['file'] = mockFileData[0].copy()
    assert response.status_code == 200
    assert response.json() == mock_response

@mock.patch('netclam_cp.main.get_request')
@mock.patch('netclam_cp.main.get_result')
@mock.patch('netclam_cp.main.get_file')
def testGetRequestCompletedRequest_returns200(mock_file, mock_result, mock_request, test_client):
    mock_request.return_value = request(**mockRequestData[1])
    mock_result.return_value = result(**mockResultData[0])
    mock_file.return_value = file(**mockFileData[1])
    response = test_client.get(f"{api_root}?id=939b91eb-a844-41f4-86b0-237e9df2839c")
    mock_response = mockRequestData[1].copy()
    mock_response['result'] = mockResultData[0].copy()
    mock_response['file'] = mockFileData[1].copy()
    assert response.status_code == 200
    assert response.json() == mock_response
