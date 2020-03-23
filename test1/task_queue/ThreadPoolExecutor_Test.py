from concurrent.futures import ThreadPoolExecutor
import time

def get_html(times):
    time.sleep(times)
    #print("get page {}s finished".format(times))
    return times

executor = ThreadPoolExecutor(max_workers=1)

task1 = executor.submit(get_html, (3))
task2 = executor.submit(get_html, (2))
#print(task1.result()) # 阻塞
print(task1.done())   # 立即返回
print(task2.cancel())
time.sleep(4)
print(task1.done())
print(task2.result())