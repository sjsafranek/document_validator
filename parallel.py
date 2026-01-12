from concurrent.futures import ProcessPoolExecutor

def run_cpu_tasks_in_parallel(callback, args):
    with ProcessPoolExecutor(max_workers=4) as executor:
        # running_tasks = [executor.submit(task) for task in tasks]
        # for running_task in running_tasks:
        #     yield running_task.result()
        results = executor.map(callback, args)
        return results
