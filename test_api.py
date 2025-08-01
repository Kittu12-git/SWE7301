# test_api.py

import requests

BASE_URL = "http://127.0.0.1:8000"

test_agency = {
    "name": "Credit Bureau X",
    "description": "Provides credit reports"
}

test_report = {
    "name": "John Doe",
    "check_type": "Credit",
    "result": "Passed",
    "reference_id": "REF123456",
    "agency_id": 1
}

def test_create_agency():
    response = requests.post(f"{BASE_URL}/agencies/", json=test_agency)
    assert response.status_code in [200, 201, 400], response.text

def test_list_agencies():
    response = requests.get(f"{BASE_URL}/agencies/")
    assert response.status_code == 200
    assert isinstance(response.json(), list), response.text

def test_create_report():
    response = requests.post(f"{BASE_URL}/reports/", json=test_report)
    assert response.status_code in [200, 201], response.text

def test_get_reports():
    response = requests.get(f"{BASE_URL}/reports/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert "name" in data[0]

def test_get_report_by_id():
    reports = requests.get(f"{BASE_URL}/reports/").json()
    if reports:
        report_id = reports[0]["id"]
        response = requests.get(f"{BASE_URL}/reports/{report_id}")
        assert response.status_code == 200
        assert response.json()["id"] == report_id

def test_update_report():
    reports = requests.get(f"{BASE_URL}/reports/").json()
    if reports:
        report_id = reports[0]["id"]
        updated_data = test_report.copy()
        updated_data["result"] = "Updated Result"
        response = requests.put(f"{BASE_URL}/reports/{report_id}", json=updated_data)
        assert response.status_code == 200
        assert response.json()["result"] == "Updated Result"

def test_delete_report():
    reports = requests.get(f"{BASE_URL}/reports/").json()
    if reports:
        report_id = reports[-1]["id"]
        response = requests.delete(f"{BASE_URL}/reports/{report_id}")
        assert response.status_code == 200
        assert response.json()["detail"] == "Report deleted successfully"
