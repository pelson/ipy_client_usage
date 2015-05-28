from datetime import datetime
import json
import time


def json_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    else:
        raise TypeError("Type {} not serializable".format(type(obj)))


def dump(fh, client, uuid_to_name=None):
    uuid_to_name = uuid_to_name or {}

    ids = client.history
    result = client.get_result(ids)
    metadata = result.metadata
    key = [uuid_to_name.get(job_id, job_id) for job_id in ids]
    metadata = dict(zip(key, metadata))
    json.dump(metadata, fh, default=json_datetime)


def wait_and_dump(fname, client, sample_frequency=0.5, uuid_to_name=None,
                  timeout=-1):
    # A close lift from Client.wait.
    tic = time.time()
    theids = client.outstanding
    client.spin()
    with open(fname, 'w') as fh:
        save_client_history(fh, client, uuid_to_name=uuid_to_name)
    while theids.intersection(client.outstanding):
        if timeout >= 0 and (time.time() - tic) > timeout:
            break
        time.sleep(sample_frequency)
        client.spin()
        with open(fname, 'w') as fh:
            dump(fh, client, uuid_to_name=uuid_to_name)
    return len(theids.intersection(client.outstanding)) == 0
