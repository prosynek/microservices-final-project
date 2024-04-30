import requests
import threading
import time
import matplotlib.pyplot as plt


def send_request(url, latencies):
    """
    Sends request & measures response latency
    """
    start_time = time.time()
    response = requests.get(url)
    end_time = time.time()
    latency = end_time - start_time
    latencies.append(latency)


def run_test(n_users, n_requests, url):
    latencies = []
    threads = []                # threads to simulate concurrent users

    for _ in range(n_users):
        for _ in range(n_requests):
            thread = threading.Thread(target=send_request, args=(url, latencies))
            threads.append(thread)

    # start the threads
    for thread in threads:
        thread.start()

    # wait for all threads to complete
    for thread in threads:
        thread.join()

    return latencies


def plot_latency(latencies):
    plt.hist(latencies, bins=20, color='blue', alpha=0.7)
    plt.title('Latency Histogram: 100 users, 5 requests each')
    plt.xlabel('Latency (seconds)')
    plt.ylabel('Frequency')
    plt.grid(True)
    plt.savefig('latency_histogram.png')


if __name__ == '__main__':
    url = 'http://146.190.166.177:5000/'  # request home endpoint - can't test others due to needing spotify accounts
    n_users = 100
    n_requests_per_user = 5

    latency_list = run_test(n_users, n_requests_per_user, url)
    plot_latency(latency_list)
