from concurrent.futures import ThreadPoolExecutor, as_completed


def run_fetch_jobs(fetch_jobs, max_workers=5):
    if not fetch_jobs:
        return {}, {}

    worker_count = min(max_workers, len(fetch_jobs))
    results = {}
    errors = {}

    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        future_names = {
            executor.submit(fetch_job): name
            for name, fetch_job in fetch_jobs.items()
        }

        for future in as_completed(future_names):
            name = future_names[future]
            try:
                results[name] = future.result()
            except Exception as exc:
                results[name] = None
                errors[name] = str(exc)

    return results, errors
