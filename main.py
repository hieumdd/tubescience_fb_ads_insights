import requests
from google.cloud import bigquery

from controller.handler import factory, run
from tasks import create_tasks

SESSION = requests.Session()
BQ_CLIENT = bigquery.Client()


def main(request):
    data = request.get_json()
    print(data)

    if "task" in data:
        response = create_tasks(data)
    elif "table" in data and "ads_account_id" in data:
        err_response, response = run(
            BQ_CLIENT,
            SESSION,
            factory(data["table"]),
            data["ads_account_id"],
            data.get("start"),
            data.get("end"),
        )
        if err_response:
            raise err_response
    else:
        raise ValueError(data)

    print(response)
    return response
